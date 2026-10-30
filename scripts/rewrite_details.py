# -*- coding: utf-8 -*-
"""번호별 본문(details) 재작성 반영기. 사실·출처 메타(refs·checked_at·adapted_from)는 기존 블록에서 이어받는다.
사용: python3 scripts/rewrite_details.py scripts/details_data/02.py ..."""
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(path):
    spec=importlib.util.spec_from_file_location('d',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    p=ROOT/f'concepts/editorial/{m.VERSION}.json';e=json.loads(p.read_text(encoding='utf-8'))
    for section,blocks in m.DETAILS.items():
        old=e['sections'][section]['details'];new=[]
        base=json.loads((ROOT/f'concepts/research/20261022-natural-korean/before/editorial/{m.VERSION}.json').read_text(encoding='utf-8'))['sections'][section]['details']
        assert [len(b[1]) for b in blocks]==[len(b['paragraphs']) for b in base],(m.VERSION,section,'block/paragraph counts must match the protected structure',[len(b[1]) for b in blocks],[len(b['paragraphs']) for b in base])
        for i,(title,paras) in enumerate(blocks):
            meta={k:v for k,v in old[min(i,len(old)-1)].items() if k not in ('title','paragraphs')}
            new.append({'title':title,'paragraphs':paras,**meta})
        e['sections'][section]['details']=new
    p.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(m.VERSION,{k:len(v) for k,v in m.DETAILS.items()})
for a in sys.argv[1:]:apply(a)
