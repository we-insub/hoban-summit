# -*- coding: utf-8 -*-
"""새로 쓴 글에서 숫자·주택형 이름이 원본에 없던 것이 생겼는지 점검한다. 사실을 바꾸지 않았다는 증거로 쓴다.
기준: 2026-10-22 자연화 이전 원본(research/.../before)과 git HEAD(이번 작업 직전) 두 가지를 모두 허용 범위로 본다."""
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOK=re.compile(r'\d[\d,]*(?:\.\d+)?(?:㎡|%|평|세대|동|호|층|만원|억|만|개|곳|형|A|B|BL|월|년|일|시|분)?|[0-9]{2,3}[AB]|A[78]|B?L?')
def flat(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in('audio','refs','checked_at','report_url','id','url','terms','adapted_from','enrichment_source'):continue
            yield from flat(v)
    elif isinstance(o,list):
        for v in o:yield from flat(v)
    elif isinstance(o,str):yield o
def nums(o):
    s=' '.join(flat(o));return set(re.findall(r'\d[\d,]*(?:\.\d+)?|[0-9]{2,3}[AB]\b|\bA[78]\b',s))
def main(v,new=None,quiet=False):
    new=new if new is not None else json.loads((ROOT/f'concepts/editorial/{v}.json').read_text(encoding='utf-8'))
    old1=json.loads((ROOT/f'concepts/research/20261022-natural-korean/before/editorial/{v}.json').read_text(encoding='utf-8'))
    old2=json.loads(subprocess.check_output(['git','show',f'HEAD:concepts/editorial/{v}.json'],cwd=ROOT).decode())
    allowed_all=nums(old1)|nums(old2)
    # 번호 사이의 사실 풀(같은 단지 공통 사실): 전 번호 editorial 숫자 합집합
    pool=set()
    for p in (ROOT/'concepts/editorial').glob('*.json'):
        pool|=nums(json.loads(p.read_text(encoding='utf-8')))
    bad=0
    def check(label,n,o):
        nonlocal bad
        added=sorted(nums(n)-nums(o)-allowed_all)
        added_not_pool=[a for a in added if a not in pool]
        if added:
            tag='★풀 밖' if added_not_pool else '풀 안'
            if not quiet:print(f'  {label:28s} 새 숫자 {added}  ({tag})')
            bad+=len(added_not_pool)
    check('(최상위)',{k:v for k,v in new.items() if k!='sections'},{k:v for k,v in old2.items() if k!='sections'})
    for k in new['sections']:check(k,new['sections'][k],old2['sections'][k])
    if not quiet:print(f'{v}: 단지 사실 풀에도 없는 새 숫자 {bad}개')
    return bad
if __name__=='__main__':
    sys.exit(1 if main(sys.argv[1]) else 0)
