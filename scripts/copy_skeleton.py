# -*- coding: utf-8 -*-
"""번호별 원고 뼈대를 만든다. 현재 글(옛 말투)이 구조에 그대로 채워져 있어서, 문자열만 새로 쓰면 구조 검사를 통과한다.
  python3 scripts/copy_skeleton.py NN > scripts/copy_data/NN.py"""
import json,pprint,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def main(v):
    e=load(f'concepts/editorial/{v}.json');r=load(f'concepts/routes/{v}.json')
    t=load('concepts/tools-copy.json')[v];c=load('concepts/calculator-copy.json')[v];sm=load('concepts/calculator-summary-copy.json')[v]
    top={k:e[k] for k in ('title','home_h1','description','question','answer','hero_kicker','hero_copy','analysis_title','analysis','faq_title','faq_intro','calc_intro','extras_intro')}
    top['faqs']=[(f['question'],f['answer']) for f in e['faqs']]
    secs={}
    for k,s in e['sections'].items():
        d=dict(title=s['title'],intro=s['intro'],question=s['question'],answer=s['answer'])
        for f in ('calc_intro','extras_intro'):
            if f in s:d[f]=s[f]
        d['cards']=[(x['title'],x['text']) for x in s['cards']]
        d['page_faqs']=[(x['question'],x['answer']) for x in s['page_faqs']]
        d['details']=[(b['title'],b['paragraphs']) for b in s['details']]
        secs[k]=d
    routes={p['slug']:p['description'] for p in r['pages']}
    meta={p['slug']:{'title':p['title'],'h1':p['h1']} for p in r['pages']}
    tools={k:{x:t[k][x] for x in ('title','h1','description','intro','faqs')} for k in ('pyeong','score','loan')}
    calc={x:c[x] for x in ('title','h1','description','intro','question','answer')}
    out=['# -*- coding: utf-8 -*-','"""%s번 새 원고. scripts/copy_data/BRIEF.md를 먼저 읽는다."""'%v,"VERSION='%s'"%v,'','TOP='+pprint.pformat(top,width=110,sort_dicts=False),'','SECTIONS='+pprint.pformat(secs,width=110,sort_dicts=False),'',
     '# 상세 페이지 검색 결과 설명(slug별). 제목·H1은 아래 ROUTE_META에서 바꿀 때만 넣는다.','ROUTES='+pprint.pformat(routes,width=110,sort_dicts=False),'',
     '# 필요하면 이 번호 독자에 맞게 제목(38자 이내)·H1을 바꾼다. 안 바꿀 slug는 지운다. 현재 값:','ROUTE_META='+pprint.pformat(meta,width=110,sort_dicts=False),'',
     'TOOLS='+pprint.pformat(tools,width=110,sort_dicts=False),'','CALC='+pprint.pformat(calc,width=110,sort_dicts=False),'','SUMMARY='+pprint.pformat(sm,width=110,sort_dicts=False),'']
    print('\n'.join(out))
main(sys.argv[1])
