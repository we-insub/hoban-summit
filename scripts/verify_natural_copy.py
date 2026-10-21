#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check preserved data and report text changes; this does not grade Korean prose."""
import hashlib,json,re,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'concepts/research/20261022-natural-korean'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def leaves(v,path=''):
 if isinstance(v,dict):
  for k,value in v.items():
   if k=='audio':continue # Original narration/transcript is intentionally unchanged.
   yield from leaves(value,path+'/'+k)
 elif isinstance(v,list):
  for i,value in enumerate(v):yield from leaves(value,path+'/'+str(i))
 elif isinstance(v,str):yield path,v
def protected(old,new,path=''):
 if isinstance(old,dict):
  for k,value in old.items():
   assert k in new,('missing field',path,k)
   if k in ['audio','refs','checked_at','report_url','id','url','terms']:
    assert value==new[k],('protected data changed',path,k)
   else:protected(value,new[k],path+'/'+k)
 elif isinstance(old,list):
  assert len(old)==len(new),('list size changed',path)
  for i,(a,b) in enumerate(zip(old,new)):protected(a,b,path+'/'+str(i))
def verify(ident):
 ep=ROOT/f'concepts/editorial/{ident}.json';rp=ROOT/f'concepts/routes/{ident}.json'
 old=json.loads((WORK/f'before/editorial/{ident}.json').read_text());new=json.loads(ep.read_text())
 protected(old,new)
 a=json.loads((WORK/f'before/routes/{ident}.json').read_text());b=json.loads(rp.read_text())
 assert {k:v for k,v in a.items() if k not in ['changed_at','pages']}=={k:v for k,v in b.items() if k not in ['changed_at','pages']}
 assert len(a['pages'])==len(b['pages'])==8
 for x,y in zip(a['pages'],b['pages']):
  for key in x:
   if key not in ['title','description','h1']:assert x[key]==y[key],(ident,key)
 oldtext=dict(leaves(old));newtext=dict(leaves(new))
 changes=[{'field':k,'before':v,'after':newtext[k]} for k,v in oldtext.items() if newtext[k]!=v]
 assert changes,(ident,'no body edits')
 for section in old['sections']:
  assert any(c['field'].startswith('/sections/'+section+'/') for c in changes),(ident,section,'not revised')
 result={'version':ident,'editorial_sha256':sha(ep),'routes_sha256':sha(rp),'protected_facts_sources_audio':'preserved','changed_text_fields':len(changes),'before_after':changes,'korean_quality':'Requires actual reading; not inferred by this script.'}
 (WORK/f'changes-{ident}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(ident+': protected references/date/audio/URLs and all 7 section edits checked; '+str(len(changes))+' text fields changed')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--version',required=True);verify(parser.parse_args().version)
 for name,digest in json.loads((WORK/'protected-sha.json').read_text()).items():assert sha(ROOT/name)==digest,(name,'protected asset changed')
