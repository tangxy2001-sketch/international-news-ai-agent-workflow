#!/usr/bin/env python3
"""Initialize research runs and validate report/presentation handoffs (stdlib only)."""
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys
CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config/sources.json'
REGIONS = [group['id'] for group in json.loads(CONFIG_PATH.read_text(encoding='utf-8'))['groups']]
def initialize(args):
    start, end = dt.date.fromisoformat(args.start), dt.date.fromisoformat(args.end)
    keywords = [v.strip() for v in args.keywords.split(',') if v.strip()]
    if start > end or not args.topic.strip() or not keywords:
        raise ValueError('日期范围、议题或关键词无效')
    path = Path(args.path)
    if path.exists() and any(path.iterdir()):
        raise ValueError('目标目录非空；为避免覆盖，请选择新目录')
    requested = getattr(args, 'regions', None)
    regions = [v.strip() for v in requested.split(',') if v.strip()] if requested else REGIONS
    if not regions or any(v not in REGIONS for v in regions):
        raise ValueError('地区必须来自 config/sources.json')
    request = dict(topic=args.topic, keywords=keywords,start=str(start),end=str(end),regions=regions)
    path.mkdir(parents=True, exist_ok=True)
    (path/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for region in regions:
        (path/'原始素材'/region).mkdir(parents=True)
    (path/'pipeline-status.md').write_text('# Pipeline status\n\n'+'\n'.join('- {}: pending'.format(s) for s in ['search','organize','report','present'])+'\n',encoding='utf-8')
    print('已初始化：{}'.format(path))
def validate(path):
    path = Path(path)
    report = (path/'报告初稿.md').read_text(encoding='utf-8')
    articles = json.loads((path/'articles.json').read_text(encoding='utf-8'))
    definitions = re.findall(r'^\[\^(\d+)\]:\s*(https?://\S+)\s*$',report,re.M)
    if not definitions:
        raise ValueError('未找到标准脚注定义')
    ids = [int(i) for i,_ in definitions]
    urls = [url for _,url in definitions]
    if len(set(ids)) != len(ids) or len(set(urls)) != len(urls):
        raise ValueError('脚注编号或 URL 重复')
    body = re.sub(r'^\[\^\d+\]:.*$','',report,flags=re.M)
    citations = [int(v) for v in re.findall(r'\[\^(\d+)\]',body)]
    if list(dict.fromkeys(citations)) != list(range(1,len(ids)+1)) or set(citations) != set(ids):
        raise ValueError('正文引用必须首次出现有序，且与脚注定义完全对应')
    if not isinstance(articles,list) or not all(isinstance(a,dict) for a in articles):
        raise ValueError('articles.json 必须为对象数组')
    expected = sorted((int(i),url) for i,url in definitions)
    actual = [(a.get('footnote'),a.get('url')) for a in articles]
    if actual != expected:
        raise ValueError('articles.json 顺序、编号或 URL 与报告脚注不一致')
    if '\ufffd' in report or '\ufffd' in json.dumps(articles,ensure_ascii=False):
        raise ValueError('发现 Unicode 替换字符')
    print('脚注与素材映射通过：{} 篇；语义质量仍需回查原文。'.format(len(articles)))
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    init = sub.add_parser('init'); init.add_argument('path')
    for name in ['topic','keywords','start','end']:
        init.add_argument('--'+name,required=True)
    init.add_argument('--regions', help='Comma-separated source groups; defaults to the full catalog')
    check = sub.add_parser('validate'); check.add_argument('path')
    args = parser.parse_args()
    try:
        initialize(args) if args.command == 'init' else validate(args.path)
    except (ValueError,OSError,TypeError) as error:
        print('错误：{}'.format(error),file=sys.stderr); return 1
    return 0
if __name__ == '__main__':
    sys.exit(main())
