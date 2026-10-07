#!/usr/bin/env python3
"""Apply one whole-page editorial model, then build and verify before returning."""
import json,sys,subprocess,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
new=json.load(sys.stdin);ident=new['id'];p=ROOT/f'concepts/editorial/{ident}.json';old=json.loads(p.read_text());old.update(new)
keys=['overview','location','premium','arrangement','types','cost','directions']
old['sections']={k:dict(zip(['title','intro','question','answer'],r[:4]),cards=[{'title':r[4],'text':r[5]},{'title':r[6],'text':r[7]}]) for k,r in zip(keys,old.pop('body_rows'))}
assert len(new['body_rows'])==7
old['sections']['cost'].update(calc_intro=new['calc_intro'],extras_intro=new['extras_intro'])
old['faqs']=[{'question':q,'answer':a,'refs':refs} for q,a,refs in old['faqs']]
html_path=ROOT/f'concepts/{ident}/index.html';before=html_path.read_text();baseline={k:hashlib.sha256(re.search(r'<section[^>]*id="'+k+r'".*?</section>',before,re.S).group().encode()).hexdigest() for k in keys}
p.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
plan_p=ROOT/'concepts/version-plan.json';plan=json.loads(plan_p.read_text());profile=next(v for v in plan['versions'] if v['id']==ident);profile.update(question=old['question'],answer=old['answer'],content_checked_at='2026-10-07');plan_p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,'scripts/build_concepts.py','--version',ident],cwd=ROOT,check=True)
subprocess.run([sys.executable,'scripts/verify_concepts.py','--version',ident],cwd=ROOT,check=True)
after=html_path.read_text();result={k:{'before':baseline[k],'after':hashlib.sha256(re.search(r'<section[^>]*id="'+k+r'".*?</section>',after,re.S).group().encode()).hexdigest(),'title':old['sections'][k]['title']} for k in keys}
assert all(v['before']!=v['after'] for v in result.values())
(ROOT/f'concepts/research/full-rewrite-20261007/{ident}-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(ident+': all 7 bodies rewritten and verified; next version may start')
