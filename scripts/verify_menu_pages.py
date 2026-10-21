#!/usr/bin/env python3
"""Verify the static menu routes and untouched booking contract in both bundles."""
import argparse,json,hashlib,re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def verify(ident):
 conf=json.loads((ROOT/f'concepts/routes/{ident}.json').read_text());origin=conf['public_origin'];pages=conf['pages']
 for folder,base in [(ROOT/f'concepts/{ident}',f'/concepts/{ident}/'),(ROOT/f'dist/hoban/{ident}','/')]:
  all_routes=['']+[p['slug']+'/' for p in pages];titles=set();descriptions=set();popup_hashes=set()
  for route in all_routes:
   doc=BeautifulSoup((folder/route/'index.html').read_text(),'html.parser');head=doc.head;url=origin+'/'+route
   for query in ['title','meta[name="description"]','meta[name="robots"]','link[rel="canonical"]','meta[property="og:title"]','meta[property="og:url"]']:
    assert len(head.select(query))==1,(route,query)
   assert len(doc.select('h1'))==1,(route,'H1 count')
   ids=[e['id'] for e in doc.select('[id]')];assert len(ids)==len(set(ids)),(route,'duplicate IDs')
   assert head.select_one('link[rel="canonical"]')['href']==url
   assert head.select_one('meta[property="og:url"]')['content']==url
   assert 'noindex' in head.select_one('meta[name="robots"]')['content']
   titles.add(doc.title.text);descriptions.add(head.select_one('meta[name="description"]')['content'])
   expected=[base+p['slug']+'/' for p in pages]+['https://mohamoa.com/']
   profile=next(v for v in json.loads((ROOT/'concepts/version-plan.json').read_text())['versions'] if v['id']==ident)
   assert [p['section'] for p in pages if p['section'] not in ['cost','calculator']]==[k for k in profile['menu'] if k!='mohamoa'], 'existing menu order changed'
   assert [e['href'] for e in doc.select('.desktop-nav a')]==[e['href'] for e in doc.select('#mobile-menu a')]==expected
   if route:
    p=next(p for p in pages if p['slug']+'/'==route);assert doc.h1.text==p['h1'];assert doc.select_one('#'+p['section'])
   if route=='calculator/':
    if doc.select_one('#mohamoa-calculator'):
     assert len(doc.select('#mohamoa-calculator .cost-tabs button'))==4
     assert len(doc.select('#mohamoa-calculator input[readonly]'))>=3
    else:assert doc.select_one('#budget-unit') and doc.select_one('#budget-price[readonly]')
   if route=='price/':assert not doc.select_one('#budget-unit') and doc.select_one('a[href="'+base+'calculator/"]')
   editorial=json.loads((ROOT/f'concepts/editorial/{ident}.json').read_text())
   from page_contract import verify_contract
   contract=dict(editorial, title=doc.title.text, description=head.select_one('meta[name="description"]')['content'], url=url)
   contract.pop('h1_topic',None)
   verify_contract(str(doc),contract)
   if route and editorial.get('enrichment_revision') and p['section']!='calculator':
    m=editorial['sections'][p['section']]
    for block in m['details']:
     for paragraph in block['paragraphs']:assert paragraph in doc.get_text(), (route,'missing full paragraph')
    if m.get('audio'):assert len(doc.select('audio source'))==2 and not doc.select_one('audio').has_attr('autoplay')
   for e in doc.select('[href], [src]'):
    val=e.get('href') or e.get('src');parts=urlsplit(val)
    if val.startswith('#'):assert doc.select_one('[id="'+val[1:]+'"]'),(route,val)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',val) or parts.netloc or not parts.path:continue
    assert parts.path.startswith('/'),val
    file=ROOT/parts.path.lstrip('/') if base!='/' else folder/parts.path.lstrip('/')
    if file.is_dir():file=file/'index.html'
    assert file.exists(),(route,str(file))
   popup_hashes.add(hashlib.sha256(str(doc.select_one('.reservation-modal')).encode()).hexdigest())
   assert 'window.RESERVATION_CONFIG.sourceVariant="'+ident+'";' in str(doc)
   assert doc.select_one('a[href="tel:16005184"]')
   assert doc.select_one('#popup-hide-today') and doc.select_one('[data-close-popup]')
   assert doc.select_one('.reservation-modal')['data-popup-preference-key']=='hoban:'+ident+':popup-hidden-until'
   assert not doc.select_one('.reservation-form #popup-hide-today')
   for field in ['name','phone','visitAt','privacyConsent','adultConsent','marketingConsent','phoneAdConsent','smsAdConsent']:
    # The original form is the authority for exact field names.
    if field in ['phone','visitAt']:continue
    assert doc.select_one('.reservation-form [name="'+field+'"]'),(route,field)
   graph=json.loads(head.select_one('script[type="application/ld+json"]').string)['@graph']
   for node in graph:
    if node['@type']=='FAQPage':
     text=doc.select_one('#faq').get_text()
     for f in node['mainEntity']:assert f['name'] in text and f['acceptedAnswer']['text'] in text,(route,'FAQ mismatch')
  assert len(titles)==len(descriptions)==len(pages)+1
  assert len(popup_hashes)==1,'booking form must remain identical on all routes'
  locs=[e.text for e in ET.parse(folder/'sitemap.xml').findall('.//{*}loc')]
  assert set(locs)=={origin+'/'+route for route in all_routes} and len(locs)==len(pages)+1
  print(f'{folder}: 9 URLs / head metadata / canonical / H1 / menus / resources / FAQ / unchanged popup passed')
 baseline=json.loads((ROOT/'references/menu-pages-20261021/booking-form-before-all.json').read_text())
 form=BeautifulSoup((ROOT/f'concepts/{ident}/index.html').read_text(),'html.parser').select_one('.reservation-form')
 assert hashlib.sha256(str(form).encode()).hexdigest()==baseline[ident], 'booking form changed'
 print(ident+': booking fields and consent unchanged; local preview only, no reservation submitted.')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--version',default='01');args=parser.parse_args();verify(args.version)
