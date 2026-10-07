#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import html
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
plan=json.loads((ROOT/'concepts/version-plan.json').read_text())
profiles={v['id']:v for v in plan['versions']}
assert set(profiles)=={str(i).zfill(2) for i in range(1,11)}
assert len({tuple(v['menu']) for v in profiles.values()})==10
parser=argparse.ArgumentParser()
parser.add_argument('--version', choices=list(profiles))
args=parser.parse_args()
class Page(HTMLParser):
 def __init__(self):
  super().__init__(); self.ids=[]; self.refs=[]; self.h1=0; self.current_nav=None; self.menus={}
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='nav' and (attrs.get('class')=='desktop-nav' or attrs.get('id')=='mobile-menu'):
   self.current_nav=attrs.get('id','desktop');self.menus[self.current_nav]=[]
  if tag=='a' and self.current_nav:self.menus[self.current_nav].append(attrs.get('href'))
  if 'id' in attrs:self.ids.append(attrs['id'])
  if tag=='h1':self.h1+=1
  for key in ['href','src']:
   if key in attrs:self.refs.append(attrs[key])
 def handle_endtag(self,tag):
  if tag=='nav':self.current_nav=None
for ident in ([args.version] if args.version else list(profiles)):
 for bundle in [ROOT/'concepts'/ident,ROOT/'dist'/'hoban'/ident]:
  source=(bundle/'index.html').read_text();page=Page();page.feed(source)
  assert page.h1==1 and len(page.ids)==len(set(page.ids)),f'{bundle}: heading/IDs'
  profile=profiles[ident]
  expected=['https://mohamoa.com/' if key=='mohamoa' else '#'+key for key in profile['menu']]
  assert expected[0]=='#overview' and expected[-1]=='https://mohamoa.com/'
  assert page.menus['desktop']==page.menus['mobile-menu']==expected,f'{ident}: nav mismatch'
  positions=[source.index('<section id="'+key+'"') for key in profile['order']]
  assert positions==sorted(positions),f'{ident}: body order mismatch'
  assert all(k['section'] in page.ids for k in plan['keywords']),f'{ident}: keyword answer missing'
  assert (ROOT/'concepts'/ident/'PROJECT.md').exists()
  for ref in page.refs:
   if ref.startswith('#'): assert ref[1:] in page.ids,ref
   elif not re.match(r'^[a-z]+:',ref): assert (bundle/ref.split('#')[0]).exists(),f'{bundle}: missing {ref}'
  assert 'noindex,follow' in source
  assert 'previewMode=true' not in source
  assert 'name="smsAdConsent"' in source
  assert 'window.RESERVATION_CONFIG.sourceVariant="'+ident+'";' in source
  config=(bundle.parent/'reservation-config.js' if bundle.parent.name=='concepts' else bundle/'reservation-config.js').read_text()
  assert 'previewMode = false' in config
  assert 'hoban-summit-reservation' in config
  assert '호반써밋 첨단3지구 상담예약' in source and '챔피언스시티' not in source
  schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source).group(1))
  assert schema['mainEntity'], 'FAQ must reflect actual questions'
  editorial_path=ROOT/'concepts/editorial'/f'{ident}.json'
  if editorial_path.exists():
   editorial=json.loads(editorial_path.read_text())
   assert len(schema['mainEntity'])==1+len(editorial['faq_indices'])
   answer_id='focus' if int(ident)>3 else 'version-answer'
   assert source.index('<section id="'+answer_id+'"') < source.index('<div class="stats-strip"')
   assert editorial['title'] in html.unescape(source)
   assert 'property="og:title"' in source and '2026.10.07' in source
   assert editorial['analysis_title'] in source
   answer_section=source.split('<section id="'+answer_id+'"',1)[1].split('</section>',1)[0]
   assert '確認' not in answer_section
   for ref in editorial['refs']: assert ref['path'] in answer_section, (ident,'direct answer source missing')
   assert Image.open(bundle/'branding/favicon-96.png').size==(96,96)
   assert Image.open(bundle/'branding/apple-touch-icon.png').size==(180,180)
   assert Image.open(bundle/'branding/favicon.ico').ico.sizes()=={(16,16),(32,32),(48,48)}
  assert schema['mainEntity'][0]['name']==profile['question']
  if int(ident)>3:
   assert 'id="focus"' in source
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
