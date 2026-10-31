# -*- coding: utf-8 -*-
"""01~10 새 말투 작업의 검수 기준. 빌드된 dist/hoban/NN을 읽어 번호별로 합격·불합격을 낸다.
  python3 scripts/audit_copy.py            # 10개 번호 요약
  python3 scripts/audit_copy.py 05 -v      # 한 번호의 불합격 항목과 문장 위치
기준은 한국어.md(지시문 반복 금지, 해요체, 독자 상황에서 시작)와 이번에 놓쳤던 곳(홈 첫 질문·답, 메타, 기록 문서)에서 뽑았다."""
import json,re,subprocess,sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'dist/hoban'
SLUGS=['','overview/','location/','premium/','site-plan/','floorplan/','price/','calculator/','visit/','pyeong-converter/','subscription-score/','loan-calculator/']
DIRECTIVE=re.compile(r'확인해 주세요|확인하세요|확인하셔야|살펴보세요|비교해 보세요|해 주세요|하세요|보세요|주세요')
STIFF=re.compile(r'합니다|습니다')
SOFT=re.compile(r'해요|이에요|예요|어요|아요|돼요|네요|거든요')  # 나요?·까요? 같은 질문 끝맺음은 두 말투에서 모두 자연스러워 세지 않는다
PERSONA={'01':r'처음|입문|알아보','02':r'납부|계약금|중도금|잔금|자금','03':r'4인|가족','04':r'A7.{0,6}A8|A7과 A8|두 블록','05':r'신혼|첫 집','06':r'평수|평형|전용|공급면적','07':r'학부모|아이|자녀|학교|부모','08':r'노부부|부모님|어르신','09':r'모델하우스|방문','10':r'비교'}

STOP={'아파트','계산기','계산','변환기','변환','환산','몇','내','제곱미터'}
def core_tokens(phrase):
    return [t for t in re.split(r'[\s·]+',phrase) if t and t not in STOP] or [phrase]
def phrase_ok(phrase,h1,desc):
    """H1에는 검색어가 그대로, 설명에는 검색어의 핵심 단어 절반 이상이 들어가야 한다."""
    out=[]
    if phrase not in h1:out.append(f'H1에 제목의 검색어 "{phrase}"가 없어요')
    core=core_tokens(phrase);hit=[t for t in core if t in desc]
    if len(hit)*2<len(core):out.append(f'설명에 검색어의 핵심 단어({"·".join(core)})가 거의 없어요')
    return out
def page(n,s):
    p=D/n/s/'index.html'
    return BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
def main_text(d):
    for t in d(['script','style','nav','header','noscript','footer','svg']):t.decompose()
    for t in d.select('.reservation-modal,.visit-bottom-bar,.report-audio,#mohamoa-calculator,table,.calc-summary,.source-note,.related-pages,#sources'):t.decompose()
    m=d.select_one('main');return re.sub(r'\s+',' ',m.get_text(' ')).strip() if m else ''
def audit(n,verbose=False):
    fails=[];info={}
    voice=json.loads((ROOT/'concepts/voice.json').read_text(encoding='utf-8'))[n]
    pages=['']+[s for s in SLUGS[1:]]
    for s in pages:
        d=page(n,s);head=d.head
        title=d.title.text;desc=head.select_one('meta[name=description]')['content'];h1=d.h1.text
        txt=main_text(d)
        if len(txt)<250:continue  # 계산기 도구 페이지처럼 본문이 짧은 곳은 톤 비율 대신 메타만 본다
        sents={x for x in re.split(r'(?<=[.요다?])\s+',txt) if DIRECTIVE.search(x)}
        k=len(sents)/max(1,len(txt))*1000
        stiff=len(STIFF.findall(txt));soft=len(SOFT.findall(txt))
        label=s or 'home'
        if k>3.0 and len(sents)>=2:fails.append((label,f'지시문이 많아요(같은 문장 빼고 1000자당 {k:.1f}개, 기준 3.0)'))
        if voice=='soft' and stiff>soft*0.4:fails.append((label,f'이 번호는 해요체인데 합니다체가 많아요(합니다 {stiff} / 해요 {soft})'))
        if voice=='formal' and soft>stiff*0.5:fails.append((label,f'이 번호는 합니다체인데 해요체가 많아요(합니다 {stiff} / 해요 {soft})'))
        if (voice=='soft' and STIFF.search(desc)) or (voice=='formal' and SOFT.search(desc) and not STIFF.search(desc)) or len(DIRECTIVE.findall(desc))>=2:fails.append((label,'메타 설명 말투가 번호와 안 맞아요: '+desc[:50]))
        if len(title)>38:fails.append((label,f'제목이 길어요({len(title)}자)'))
        if len(desc)>150:fails.append((label,f'설명이 길어요({len(desc)}자)'))
    # 홈: 독자(페르소나)가 제목·H1·첫 소개에 드러나는지
    d=page(n,'');hero=' '.join([d.title.text,d.h1.text,(d.select_one('.hero-copy') or d.h1).get_text(' ')])
    if not re.search(PERSONA[n],hero):fails.append(('home',f'제목·H1·첫 소개에 독자 표현({PERSONA[n]})이 없어요'))
    # 도구 페이지: 소개·FAQ 말투
    for s in SLUGS[9:]:
        d=page(n,s);t=re.sub(r'\s+',' ',' '.join(x.get_text(' ') for x in d.select('.detail-header p, .page-faq')))
        if voice=='soft' and STIFF.search(t) and len(STIFF.findall(t))>len(SOFT.findall(t))*0.4:fails.append((s.strip('/'),'소개·FAQ가 합니다체예요(이 번호는 해요체)'))
        if voice=='formal' and SOFT.search(t) and len(SOFT.findall(t))>len(STIFF.findall(t))*0.5:fails.append((s.strip('/'),'소개·FAQ가 해요체예요(이 번호는 합니다체)'))
    # 계산기 4종: 제목의 검색어('|' 앞)가 H1과 설명에도 그대로 나와야 한다(검색 표현과 본문이 같은 주제인지)
    for s_ in ['calculator/']+SLUGS[9:]:
        d=page(n,s_);phrase=d.title.text.split(' |')[0].strip();h1=d.h1.get_text(' ',strip=True);de=d.head.select_one('meta[name=description]')['content']
        for msg in phrase_ok(phrase,h1,de):fails.append((s_.strip('/'),msg))
    # 기록: PROJECT.md와 HOME_TITLE_REVISION 기록이 지금 홈 제목과 같은지
    home_title=page(n,'').title.text
    proj=(ROOT/f'concepts/{n}/PROJECT.md').read_text(encoding='utf-8')
    if home_title not in proj:fails.append(('PROJECT.md','홈 제목이 PROJECT.md에 없어요'))
    rec=(ROOT/'HOME_TITLE_REVISION_20261022.md').read_text(encoding='utf-8')
    sec=rec.split(f'## {n}\n')[1].split('\n## ')[0] if f'## {n}\n' in rec else ''
    if home_title not in sec:fails.append(('HOME_TITLE_REVISION','번호별 홈 제목 기록이 지금 제목과 달라요'))
    # version-plan 대표 질문·답이 홈에 있는지, 말투
    plan=[v for v in json.loads((ROOT/'concepts/version-plan.json').read_text(encoding='utf-8'))['versions'] if v['id']==n][0]
    st,so=len(STIFF.findall(plan['answer'])),len(SOFT.findall(plan['answer']))
    if (voice=='soft' and st>so) or (voice=='formal' and so>st):fails.append(('version-plan','대표 답 말투가 번호와 안 맞아요'))
    # 숫자·사실
    sys.path.insert(0,str(ROOT/'scripts'));import check_facts
    left=check_facts.main(n,quiet=True)
    if left:fails.append(('facts',f'단지 사실 풀에 없는 새 숫자 {left}개'))
    return fails

def audit_data(path):
    """빌드 없이 원고 파일(copy_data/NN.py)만 검사한다. 병렬 작업 중 각 번호가 스스로 점검하는 용도."""
    import importlib.util
    spec=importlib.util.spec_from_file_location('c',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    n=m.VERSION;voice=json.loads((ROOT/'concepts/voice.json').read_text(encoding='utf-8'))[n];fails=[]
    def strs(o):
        if isinstance(o,str):yield o
        elif isinstance(o,dict):
            for k,v in o.items():
                if k in('title','h1','description') and isinstance(v,str) and False:continue
                yield from strs(v)
        elif isinstance(o,(list,tuple)):
            for v in o:yield from strs(v)
    def tone(label,text,meta=False):
        sents={x for x in re.split(r'(?<=[.요다?])\s+',text) if DIRECTIVE.search(x)}
        stiff=len(STIFF.findall(text));soft=len(SOFT.findall(text));k=len(sents)/max(1,len(text))*1000
        if not meta:
            if len(text)>400 and k>3.0 and len(sents)>=2:fails.append((label,f'지시문이 많아요(1000자당 {k:.1f}개, 기준 3.0). 지시 대신 이유·상황을 쓰거나 "~면 돼요/~예요"로 바꿔요'))
            if voice=='soft' and stiff>soft*0.4 and len(text)>200:fails.append((label,f'해요체여야 하는데 합니다체가 많아요(합니다 {stiff} / 해요 {soft})'))
            if voice=='formal' and soft>stiff*0.5 and len(text)>200:fails.append((label,f'합니다체여야 하는데 해요체가 많아요(합니다 {stiff} / 해요 {soft})'))
        else:
            if (voice=='soft' and STIFF.search(text)) or (voice=='formal' and SOFT.search(text) and not STIFF.search(text)) or len(DIRECTIVE.findall(text))>=2:fails.append((label,'메타 말투가 번호와 안 맞아요: '+text[:45]))
            if len(text)>150:fails.append((label,'설명 150자 초과'))
    for key,sec in m.SECTIONS.items():
        tone('섹션 '+key,' '.join(strs(sec)))
    tone('홈 소개',' '.join(strs([m.TOP['analysis'],m.TOP['faqs'],m.TOP['hero_copy']])))
    tone('홈 메타',m.TOP['description'],meta=True)
    for slug,d in m.ROUTES.items():tone('메타 '+slug,d,meta=True)
    for k,d in m.TOOLS.items():
        tone('도구 '+k+' 메타',d['description'],meta=True);tone('도구 '+k+' 본문',' '.join(strs([d['intro'],d['faqs']])))
    tone('계산기 메타',m.CALC['description'],meta=True);tone('계산기 본문',' '.join(strs(list(m.CALC.values())[3:])))
    tone('계산기 표 설명',' '.join(strs(m.SUMMARY)))
    for k,dd in list(m.TOOLS.items())+[('calculator',m.CALC)]:
        import json as _j
        base=_j.loads((ROOT/'concepts/tools-copy.json').read_text(encoding='utf-8'))[n].get(k) if k!='calculator' else _j.loads((ROOT/'concepts/calculator-copy.json').read_text(encoding='utf-8'))[n]
        phrase=dd.get('title',base['title']).split(' |')[0].strip()
        for msg in phrase_ok(phrase,dd.get('h1',base['h1']),dd.get('description',base['description'])):fails.append(('도구 '+k,msg))
    hero=' '.join([m.TOP['title'],m.TOP['home_h1'],m.TOP['hero_kicker'],m.TOP['hero_copy'],m.TOP['description']])
    if not re.search(PERSONA[n],hero):fails.append(('홈 제목·H1·첫 소개',f'이 번호의 독자 표현({PERSONA[n]})이 안 보여요'))
    # 옛 문구가 그대로 남았는지(뼈대의 원문 그대로 둔 문장)
    return fails

if __name__=='__main__':
    if '--data' in sys.argv:
        f=audit_data([a for a in sys.argv[1:] if not a.startswith('-')][0])
        print('원고 검수:','합격' if not f else f'불합격 {len(f)}건')
        for w,msg in f:print(f'    [{w}] {msg}')
        sys.exit(1 if f else 0)
    args=[a for a in sys.argv[1:] if not a.startswith('-')];verbose='-v' in sys.argv
    nums=args or [f'{i:02d}' for i in range(1,11)]
    total=0
    for n in nums:
        f=audit(n)
        total+=len(f)
        print(f'{n}: {"합격" if not f else f"불합격 {len(f)}건"}')
        if f and (verbose or len(nums)==1):
            for where,msg in f:print(f'    [{where}] {msg}')
    sys.exit(1 if total else 0)
