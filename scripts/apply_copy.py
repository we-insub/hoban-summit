# -*- coding: utf-8 -*-
"""번호별 새 말투 원고(scripts/copy_data/NN.py)를 editorial·routes·계산기 문구에 반영한다.
기존 블록 개수·문단 개수·refs·확인일·음성 등 보호 항목은 그대로 두고 글만 바꾼다.
  python3 scripts/apply_copy.py --check scripts/copy_data/NN.py   # 쓰기 없이 구조·길이·숫자만 검사(병렬 작업용)
  python3 scripts/apply_copy.py scripts/copy_data/NN.py            # 실제 반영(공유 파일을 쓰므로 한 번에 하나씩)
"""
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d,**kw):Path(p).write_text(json.dumps(d,ensure_ascii=False,**kw)+'\n',encoding='utf-8')
def apply(path,write=True):
    spec=importlib.util.spec_from_file_location('c',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    v=m.VERSION;e=load(ROOT/f'concepts/editorial/{v}.json')
    base=load(ROOT/f'concepts/research/20261022-natural-korean/before/editorial/{v}.json')
    for k,val in m.TOP.items():
        if k=='faqs':
            assert len(val)==len(e['faqs']),('faqs 개수',len(val),len(e['faqs']))
            for i,(q,a) in enumerate(val):e['faqs'][i]['question']=q;e['faqs'][i]['answer']=a
        elif k=='analysis':
            assert len(val)==len(e['analysis']),('analysis 문단 수',len(val),len(e['analysis']));e[k]=val
        else:
            assert k in e,k;e[k]=val
    assert len(e['description'])<=150 and len(e['title'])<=38,('홈 title<=38, description<=150',len(e['title']),len(e['description']))
    for key,s in m.SECTIONS.items():
        tgt=e['sections'][key];b=base['sections'][key]
        for f in ('title','intro','question','answer','calc_intro','extras_intro'):
            if f in s:
                assert f in tgt,(key,f);tgt[f]=s[f]
        assert len(s['cards'])==len(b['cards']),(key,'cards 개수')
        for i,(t,x) in enumerate(s['cards']):tgt['cards'][i].update(title=t,text=x)
        assert len(s['page_faqs'])==len(b['page_faqs']),(key,'page_faqs 개수',len(s['page_faqs']),len(b['page_faqs']))
        for i,(q,a) in enumerate(s['page_faqs']):tgt['page_faqs'][i].update(question=q,answer=a)
        assert [len(x[1]) for x in s['details']]==[len(x['paragraphs']) for x in b['details']],(key,'details 블록·문단 개수',[len(x[1]) for x in s['details']],[len(x['paragraphs']) for x in b['details']])
        for i,(t,ps) in enumerate(s['details']):tgt['details'][i].update(title=t,paragraphs=ps)
    missing=set(base['sections'])-set(m.SECTIONS)
    assert not missing,('빠진 섹션',missing)
    # 라우트 메타
    r=load(ROOT/f'concepts/routes/{v}.json')
    for pg in r['pages']:
        d=m.ROUTES.get(pg['slug'],m.ROUTES.get(pg['section']))
        if d:pg['description']=d
        meta=getattr(m,'ROUTE_META',{}).get(pg['slug'])
        if meta:pg.update({k:meta[k] for k in ('title','h1','description') if k in meta})
        assert len(pg['title'])<=38 and len(pg['description'])<=150,(pg['slug'],'title<=38, description<=150',len(pg['title']),len(pg['description']))
    t=load(ROOT/'concepts/tools-copy.json')
    for tool,d in m.TOOLS.items():
        assert len(d['faqs'])==3 or len(d['faqs'])==len(t[v][tool]['faqs']),(tool,'faqs 개수')
        t[v][tool].update(d)
        assert len(t[v][tool]['title'])<=38 and len(t[v][tool]['description'])<=150,(tool,'title<=38, description<=150')
    c=load(ROOT/'concepts/calculator-copy.json');c[v].update(m.CALC)
    for pg in r['pages']:
        if pg['section']=='calculator':
            pg.update({k:m.CALC[k] for k in ('title','h1','description') if k in m.CALC})
            assert len(pg['title'])<=38 and len(pg['description'])<=150,('calculator','title<=38, description<=150')
    s2=load(ROOT/'concepts/calculator-summary-copy.json');s2[v]=m.SUMMARY
    assert len(m.SUMMARY['points'])==3,('summary points는 3개',)
    plan=load(ROOT/'concepts/version-plan.json')
    if 'question' in m.TOP or 'answer' in m.TOP:
        for x in plan['versions']:
            if x['id']==v:x['question']=e['question'];x['answer']=e['answer']
    import check_facts
    left=check_facts.main(v,new=e,quiet=not write)
    if not write:
        print(v,'검사 통과(구조·길이). 단지 사실 풀 밖의 새 숫자:',left,'개 / 쓰기 안 함');return
    save(ROOT/f'concepts/editorial/{v}.json',e,indent=2);save(ROOT/f'concepts/routes/{v}.json',r,indent=2)
    save(ROOT/'concepts/tools-copy.json',t,indent=1);save(ROOT/'concepts/calculator-copy.json',c,indent=1)
    save(ROOT/'concepts/calculator-summary-copy.json',s2,indent=1);save(ROOT/'concepts/version-plan.json',plan,indent=2)
    print(v,'applied')
if __name__=='__main__':
    args=[a for a in sys.argv[1:] if not a.startswith('--')]
    for a in args:apply(a,write='--check' not in sys.argv)
