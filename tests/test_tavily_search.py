import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, MagicMock
from urllib.error import HTTPError

spec=importlib.util.spec_from_file_location('tavily_search',Path(__file__).resolve().parents[1]/'scripts/tavily_search.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SearchTests(unittest.TestCase):
    def prepare(self,folder):
        run=Path(folder)
        task={'topic':'Fictional port pilot','keywords':['pilot'],'start':'2031-04-01','end':'2031-04-30','regions':['英国']}
        module.write_json(run/'request.json',task)
        module.write_json(run/'queries.json',{'reviewed':True,'queries':[{'group':'英国','query':'fictional port pilot','domains':['example.com'],'topic':'news'}]})
        return run,task
    def result(self,url='https://example.com/a'):
        return {'url':url,'title':'Synthetic item','published_date':'Thu, 03 Apr 2031 09:00:00 GMT','raw_content':'Synthetic source paragraph. '*20,'content':'Summary.'}
    def test_auth_header_and_redaction(self):
        key='TEST_ONLY_NOT_A_REAL_CREDENTIAL'
        opener=MagicMock();opener.open.return_value.__enter__.return_value.read.return_value=json.dumps({'results':[],'echo':key}).encode()
        result=module.TavilyClient(key,opener).search({'query':'demo'})
        req=opener.open.call_args[0][0]
        self.assertEqual(req.full_url,module.ENDPOINT)
        self.assertEqual(req.get_header('Authorization'),'Bearer '+key)
        self.assertNotIn(key,req.data.decode())
        self.assertEqual(result['echo'],'[REDACTED]')
    def test_errors_never_echo_provider_body(self):
        secret='TEST_ONLY_PRIVATE_VALUE'
        opener=Mock();opener.open.side_effect=HTTPError(module.ENDPOINT,401,secret,{},io.BytesIO(secret.encode()))
        with self.assertRaises(module.SearchError) as error:
            module.TavilyClient(secret,opener).search({'query':'demo'})
        self.assertNotIn(secret,str(error.exception))
        self.assertIn('401',str(error.exception))
    def test_missing_key_rejected(self):
        with self.assertRaises(module.SearchError):module.TavilyClient('')
    def test_url_normalization_preserves_article_identity(self):
        self.assertEqual(module.canonical_url('https://EXAMPLE.com/a?id=2&utm_source=x#part'),'https://example.com/a?id=2')
        self.assertNotEqual(module.canonical_url('https://example.com/a?id=2'),module.canonical_url('https://example.com/a?id=3'))
    def test_dates_and_partial_content(self):
        task={'start':'2031-04-01','end':'2031-04-30'}
        candidate=module.normalize_result(self.result(),'英国',task)
        self.assertEqual(candidate['date_status'],'in_range')
        self.assertEqual(candidate['content_quality'],'partial')
        for date,status in [(None,'unknown'),('2031-05-01','out_of_range')]:
            data=self.result();data['published_date']=date;data['raw_content']=''
            c=module.normalize_result(data,'英国',task)
            self.assertEqual(c['date_status'],status)
            self.assertEqual(c['retrieval_content'],'summary')
    def test_unreviewed_plan_cannot_search(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder);plan=module.read_json(run/'queries.json');plan['reviewed']=False;module.write_json(run/'queries.json',plan)
            client=Mock()
            with self.assertRaises(ValueError):module.retrieve(run,1,client=client)
            client.search.assert_not_called()
    def test_budget_resume_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder)
            plan=module.read_json(run/'queries.json');plan['queries'].append({'group':'英国','query':'second query','domains':['example.com']});module.write_json(run/'queries.json',plan)
            client=Mock();client.search.return_value={'results':[self.result(),self.result('https://example.com/a?utm_source=test')],'usage':{'credits':2}}
            self.assertFalse(module.retrieve(run,1,client=client))
            self.assertEqual(client.search.call_count,1)
            self.assertTrue(module.retrieve(run,1,client=client))
            self.assertEqual(client.search.call_count,2)
            self.assertTrue(module.retrieve(run,1,client=client))
            self.assertEqual(client.search.call_count,2)
            candidates=module.read_json(run/'candidates.json')['candidates'];self.assertEqual(len(candidates),1)
            decisions=[{'id':candidates[0]['id'],'decision':'accept','reason':'Synthetic relevance checked','content_reviewed':True,'content_quality':'full'}]
            module.write_json(run/'screening.json',decisions)
            module.save_selected(run);module.save_selected(run)
            files=list((run/'原始素材').rglob('*.md'));self.assertEqual(len(files),1)
            self.assertIn('content_quality: "full"',files[0].read_text())
    def test_unknown_date_cannot_be_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder);item=self.result();item['published_date']=None
            client=Mock();client.search.return_value={'results':[item]};module.retrieve(run,1,client=client)
            c=module.read_json(run/'candidates.json')['candidates'][0]
            module.write_json(run/'screening.json',[{'id':c['id'],'decision':'accept','reason':'test','content_reviewed':True}])
            with self.assertRaises(ValueError):module.save_selected(run)
            self.assertFalse((run/'原始素材').exists())
    def test_changed_task_invalidates_candidate_handoff(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder);client=Mock();client.search.return_value={'results':[self.result()]};module.retrieve(run,1,client=client)
            task['end']='2031-04-29';module.write_json(run/'request.json',task)
            with self.assertRaises(ValueError):module.save_selected(run)
    def test_failed_query_is_retried_only_on_next_invocation(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder);client=Mock();client.search.side_effect=module.SearchError('Tavily HTTP 429')
            self.assertFalse(module.retrieve(run,3,client=client));self.assertEqual(client.search.call_count,1)
            log=module.read_json(run/'search-log.json');self.assertEqual(log['pending_or_failed'][0]['status'],'failed')
            client.search.side_effect=None;client.search.return_value={'results':[self.result()]}
            self.assertTrue(module.retrieve(run,1,client=client));self.assertEqual(client.search.call_count,2)
    def test_summary_cannot_be_promoted_to_full(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder);item=self.result();item['raw_content']=None
            client=Mock();client.search.return_value={'results':[item]};module.retrieve(run,1,client=client)
            c=module.read_json(run/'candidates.json')['candidates'][0]
            module.write_json(run/'screening.json',[{'id':c['id'],'decision':'accept','reason':'test','content_reviewed':True,'content_quality':'full'}])
            with self.assertRaises(ValueError):module.save_selected(run)
    def test_dry_run_needs_no_key_and_makes_no_request(self):
        with tempfile.TemporaryDirectory() as folder:
            run,task=self.prepare(folder);client=Mock()
            self.assertTrue(module.retrieve(run,1,dry_run=True,client=client))
            client.search.assert_not_called()
