#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import html
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids=[]; self.refs=[]; self.h1=0
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if 'id' in attrs:self.ids.append(attrs['id'])
  if tag=='h1':self.h1+=1
  for key in ['href','src']:
   if key in attrs:self.refs.append(attrs[key])
for ident in ['01','02','03']:
 for bundle in [ROOT/'concepts'/ident,ROOT/'dist'/'hoban'/ident]:
  source=(bundle/'index.html').read_text();page=Page();page.feed(source)
  assert page.h1==1 and len(page.ids)==len(set(page.ids)),f'{bundle}: heading/IDs'
  for ref in page.refs:
   if ref.startswith('#'): assert ref[1:] in page.ids,ref
   elif not re.match(r'^[a-z]+:',ref): assert (bundle/ref.split('#')[0]).exists(),f'{bundle}: missing {ref}'
  assert 'noindex,follow' in source
  assert '호반써밋 첨단3지구 상담예약' in source and '챔피언스시티' not in source
  schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source).group(1))
  assert len(schema['mainEntity'])==8
  for faq in schema['mainEntity']:
   assert html.escape(faq['name'],quote=True) in source
   assert html.escape(faq['acceptedAnswer']['text'],quote=True) in source
  assert 'id="budget-price" value="49,400" readonly' in source
 print(f'{ident}: local/standalone assets, anchors, FAQ parity, read-only price passed')
client=(ROOT/'concepts'/'consent-policy.js').read_text()
server=(ROOT/'supabase/functions/hoban-summit-reservation/consent-policy.ts').read_text()
assert json.loads(client[client.index('{'):client.rindex('}')+1])==json.loads(server[server.index('{'):server.rindex('}')+1])
subprocess.run(['node','-e',r'''
const assert=require('assert');
const {calculate}=require('./concepts/budget-math');
assert.deepStrictEqual(calculate(494000000,100000000,200000000,5000000),{total:499000000,first:10000000,second:14700000,deposit:24700000,interim:296400000,balance:172900000,equity:299000000,gap:199000000});
assert.equal(calculate(687000000,100000000,300000000,0).gap,287000000);
assert.throws(()=>calculate(494000000,-1,0,0));
assert.throws(()=>calculate(494000000,0,999000000,0));
assert.equal(calculate(494000000,999000000,0,0).gap,0);
for(const unit of require('./concepts/source-data.json').units)for(const row of unit.prices){const r=calculate(row.won,0,0,0);assert.equal(r.deposit+r.interim+r.balance,row.won);assert.equal(r.first+r.second,r.deposit);}
console.log('Budget amount/units/negative/loan guards: passed');
'''],cwd=str(ROOT),check=True)
print('Frontend/server Hoban consent policy parity: passed. No live booking submitted.')
