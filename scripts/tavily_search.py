#!/usr/bin/env python3
"""Tavily Search: plan -> retrieve candidates -> agent screening -> save sources."""
import argparse
import datetime as dt
from email.utils import parsedate_to_datetime
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = 'https://api.tavily.com/search'


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temporary.replace(path)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def canonical_url(url):
    parts = urlsplit(url)
    if parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password:
        raise ValueError('Invalid source URL')
    query = [(k,v) for k,v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in ('fbclid','gclid')]
    return urlunsplit((parts.scheme.lower(),parts.netloc.lower(),parts.path or '/',urlencode(query),''))


def publication_date(value):
    if not isinstance(value,str):
        return None
    try:
        return dt.date.fromisoformat(value[:10]).isoformat()
    except ValueError:
        try:
            return parsedate_to_datetime(value).date().isoformat()
        except (ValueError,TypeError,OverflowError):
            return None


def task_at(run):
    task = read_json(run/'request.json')
    start, end = dt.date.fromisoformat(task['start']), dt.date.fromisoformat(task['end'])
    if start > end:
        raise ValueError('Invalid task date interval')
    return task


def make_plan(run):
    task = task_at(run)
    catalog = {g['id']:g for g in read_json(ROOT/'config/sources.json')['groups']}
    queries=[]
    for group in task['regions']:
        entry=catalog[group]
        queries.append({'group':group,'query':' '.join([task['topic']]+task['keywords']),
                        'language_hint':entry['languages'][0],'domains':entry['domains'],
                        'topic':'general' if group=='国际智库' else 'news'})
    target=run/'queries.json'
    if target.exists():
        raise ValueError('queries.json exists; edit it rather than overwrite it')
    write_json(target,{'reviewed':False,'queries':queries})
    print('Created queries.json. Agent must localize queries, check scope, then set reviewed to true.')


def jobs_at(run):
    task=task_at(run)
    plan=read_json(run/'queries.json')
    if plan.get('reviewed') is not True:
        raise ValueError('Agent must review/localize queries.json before retrieval')
    queries=plan.get('queries')
    if not isinstance(queries,list) or not queries:
        raise ValueError('queries must be a non-empty array')
    jobs=[]
    for query in queries:
        group=query['group']
        if group not in task['regions'] or group in ('.','..') or '/' in group or '\\' in group:
            raise ValueError('Invalid or unselected source group')
        text=query['query']
        if not isinstance(text,str) or not text.strip():
            raise ValueError('Empty query')
        domains=query.get('domains',[])
        if not isinstance(domains,list) or not all(isinstance(d,str) and re.fullmatch(r'[A-Za-z0-9.-]+',d) for d in domains):
            raise ValueError('domains must be hostnames, not URLs')
        topic=query.get('topic','news')
        if topic not in ('news','general'):
            raise ValueError('Use news or general topic')
        # Widen API boundaries, then enforce the user's inclusive dates locally.
        payload={'query':text,'topic':topic,'search_depth':'advanced','max_results':5,
                 'include_raw_content':True,'include_domains':domains,'include_usage':True,
                 'include_published_date':True,
                 'start_date':str(dt.date.fromisoformat(task['start'])-dt.timedelta(days=1)),
                 'end_date':str(dt.date.fromisoformat(task['end'])+dt.timedelta(days=1))}
        identity={'group':group,'payload':payload,'task_start':task['start'],'task_end':task['end']}
        jobs.append({'id':fingerprint(identity),'group':group,'payload':payload})
    unique={job['id']:job for job in jobs}
    return task,list(unique.values())


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class SearchError(Exception):
    pass


class TavilyClient:
    def __init__(self,key,opener=None):
        if not isinstance(key,str) or not key.strip():
            raise SearchError('Set your own TAVILY_API_KEY or use --prompt-key in your terminal.')
        self.key=key.strip()
        self.opener=opener or build_opener(NoRedirect())

    def search(self,payload):
        request=Request(ENDPOINT,data=json.dumps(payload).encode('utf-8'),method='POST',
                        headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json'})
        try:
            with self.opener.open(request,timeout=60) as response:
                raw=response.read().decode('utf-8')
            # Defensive redaction if a provider ever echoes the credential.
            result=json.loads(raw.replace(self.key,'[REDACTED]'))
            if not isinstance(result,dict) or not isinstance(result.get('results'),list):
                raise SearchError('Unexpected provider response; no content saved.')
            return result
        except HTTPError as error:
            # Never print response bodies, URLs, request headers, or raw exceptions.
            raise SearchError('Tavily HTTP {}. Check credentials, quota, rate limits or request parameters; rerun later.'.format(error.code)) from None
        except (URLError,TimeoutError,OSError,ValueError) as error:
            raise SearchError('Tavily network/response error; details withheld to protect credentials.') from None


def normalize_result(item,group,task):
    try:
        url=canonical_url(item.get('url',''))
    except (ValueError,AttributeError):
        return None
    raw=item.get('raw_content') or ''
    summary=item.get('content') or ''
    if not isinstance(raw,str) or not isinstance(summary,str):
        return None
    noisy=len(re.findall(r'<(?:nav|header|footer)\b',raw,re.I))>3
    body=raw if len(raw.strip())>=200 and not noisy else summary
    published=publication_date(item.get('published_date'))
    status='unknown' if not published else ('in_range' if task['start']<=published<=task['end'] else 'out_of_range')
    return {'id':hashlib.sha256(url.encode()).hexdigest()[:20],
            'title':str(item.get('title') or url),'source':url,'publisher':urlsplit(url).hostname,
            'source_group':group,'published':published,'date_status':status,
            'created':dt.date.today().isoformat(),'content_quality':'partial',
            'retrieval_content':'raw' if body==raw and raw else 'summary',
            'body':body,'quality_note':'Agent must verify date, identity, relevance and completeness against the source.'}


def retrieve(run,max_calls,key='',dry_run=False,client=None):
    if max_calls<1:
        raise ValueError('max-calls must be positive')
    task,jobs=jobs_at(run)
    if dry_run:
        print(json.dumps({'endpoint':ENDPOINT,'max_new_calls':max_calls,'queries':jobs},ensure_ascii=False,indent=2))
        return True
    client=client or TavilyClient(key)
    cache_dir=run/'.search-cache'
    calls=0; errors=[]; candidates={}; records=[]; blocked=False
    for job in jobs:
        cache=cache_dir/(job['id']+'.json')
        if cache.exists():
            record=read_json(cache)
        elif calls>=max_calls or blocked:
            errors.append({'query_id':job['id'],'status':'provider_blocked' if blocked else 'budget_pending'})
            continue
        else:
            calls+=1
            try:
                response=client.search(job['payload'])
                items=[normalize_result(item,job['group'],task) for item in response['results'] if isinstance(item,dict)]
                record={'query_id':job['id'],'group':job['group'],'candidates':[x for x in items if x],
                        'usage':response.get('usage'),'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat()}
                write_json(cache,record)
            except SearchError as error:
                errors.append({'query_id':job['id'],'status':'failed','error':str(error)})
                # Authentication/quota failures cannot improve by querying another region.
                if any(code in str(error) for code in ['401','403','432','433','429']):
                    blocked=True
                continue
        records.append({k:v for k,v in record.items() if k!='candidates'})
        for candidate in record['candidates']:
            previous=candidates.get(candidate['id'])
            if not previous or (candidate['retrieval_content']=='raw',len(candidate['body']))>(previous['retrieval_content']=='raw',len(previous['body'])):
                candidates[candidate['id']]=candidate
    output={'task_fingerprint':fingerprint(task),'candidates':list(candidates.values())}
    write_json(run/'candidates.json',output)
    write_json(run/'search-log.json',{'new_calls':calls,'completed_queries':records,'pending_or_failed':errors,
                                    'unique_candidates':len(candidates),'all_queries_retrieved':len(records)==len(jobs)})
    (run/'search-log.md').write_text('# Search log\n\nNew API calls: {}\n\nUnique candidates: {}\n\nQuery retrieval: {}\n\nSee search-log.json for per-query usage and failures. Semantic screening remains pending.\n'.format(calls,len(candidates),'complete' if len(records)==len(jobs) else 'incomplete'),encoding='utf-8')
    with (run/'pipeline-status.md').open('a',encoding='utf-8') as file:
        file.write('\n- Search retrieval: {}; candidate screening pending.\n'.format('retrieved' if len(records)==len(jobs) else 'incomplete'))
    print('API calls: {}; candidates: {}; pending/failed: {}. Review candidates.json before saving.'.format(calls,len(candidates),len(errors)))
    return not errors


def save_selected(run):
    task=task_at(run)
    candidate_doc=read_json(run/'candidates.json')
    if candidate_doc.get('task_fingerprint')!=fingerprint(task):
        raise ValueError('Task changed; retrieve candidates for the current task')
    candidates={c['id']:c for c in candidate_doc['candidates']}
    decisions=read_json(run/'screening.json')
    if not isinstance(decisions,list):
        raise ValueError('screening.json must be an array')
    ids=[d['id'] for d in decisions]
    if len(ids)!=len(set(ids)) or set(ids)!=set(candidates):
        raise ValueError('Provide exactly one screening decision per current candidate')
    selected=[]
    for decision in decisions:
        if decision.get('decision') not in ('accept','reject','needs_review') or not str(decision.get('reason','')).strip():
            raise ValueError('Each decision needs accept/reject/needs_review and a reason')
        if decision['decision']!='accept':
            continue
        if decision.get('content_reviewed') is not True:
            raise ValueError('Accept requires content_reviewed: true')
        c=candidates[decision['id']]
        published=publication_date(c.get('published'))
        if not published or not task['start']<=published<=task['end']:
            raise ValueError('Accepted source must have a verified publication date in the requested interval')
        if not c.get('body','').strip():
            raise ValueError('Accepted source has no content')
        group=c['source_group']
        if group not in task['regions'] or group in ('.','..') or '/' in group or '\\' in group:
            raise ValueError('Invalid source group')
        quality=decision.get('content_quality','partial')
        if quality not in ('full','partial'):
            raise ValueError('content_quality must be full or partial')
        if quality=='full' and c['retrieval_content']!='raw':
            raise ValueError('Summary-only content cannot be labeled full')
        metadata={k:c[k] for k in ['title','source','publisher','source_group','published','created']}
        metadata['content_quality']=quality
        metadata['candidate_id']=c['id']
        # JSON scalar strings are valid YAML values; preserve quotation marks safely.
        text='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in metadata.items())+'\n---\n\n'+c['body']+'\n'
        selected.append((run/'原始素材'/group/(c['id']+'.md'),text))
    saved=0
    for path,text in selected:
        if path.exists():
            continue
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as file:
            file.write(text)
        saved+=1
    with (run/'pipeline-status.md').open('a',encoding='utf-8') as file:
        file.write('\n- Screening: {} accepted, {} newly saved; inspect search-log.json and needs_review decisions before marking Search completed.\n'.format(len(selected),saved))
    print('Accepted: {}; newly saved: {}. Existing files preserved.'.format(len(selected),saved))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for command in ['plan','search','save']:
        subparser=sub.add_parser(command)
        subparser.add_argument('run',type=Path)
        if command=='search':
            subparser.add_argument('--max-calls',type=int,default=16)
            subparser.add_argument('--dry-run',action='store_true')
            subparser.add_argument('--prompt-key',action='store_true',help='User enters own key privately in an interactive terminal')
    args=parser.parse_args()
    try:
        if args.command=='plan':make_plan(args.run)
        elif args.command=='save':save_selected(args.run)
        else:
            key='' if args.dry_run else os.environ.get('TAVILY_API_KEY','')
            if args.prompt_key and not args.dry_run:
                key=getpass.getpass('Your own Tavily API key (hidden): ')
            return 0 if retrieve(args.run,args.max_calls,key,args.dry_run) else 1
    except SearchError as error:
        print(str(error),file=sys.stderr)
        return 1
    except (ValueError,OSError,KeyError,TypeError,OverflowError):
        # No arbitrary exception bodies: provider/input exceptions may contain secrets.
        print('Unable to complete. Check task/plan/screening formats, dates, your TAVILY_API_KEY, and local file access. See search-log.json for safe per-query failures.',file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
