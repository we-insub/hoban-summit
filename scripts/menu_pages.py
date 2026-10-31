"""Static menu-page split. Reads authored content; keeps shared booking assets intact."""
import copy,json,posixpath,shutil,re
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
def soup(s): return BeautifulSoup(s,'html.parser')
def fragment(s): return soup(s)
def split_version(ident):
 conf=json.loads((ROOT/f'concepts/routes/{ident}.json').read_text())
 assert conf['mode']=='local-preview','Publishing requires a separate reviewed release'
 editorial=json.loads((ROOT/f'concepts/editorial/{ident}.json').read_text())
 tools=json.loads((ROOT/'concepts/tools-pages.json').read_text())
 tool_copy=json.loads((ROOT/'concepts/tools-copy.json').read_text())[ident]
 voice_mode=json.loads((ROOT/'concepts/voice.json').read_text())[ident];voice_pairs=json.loads((ROOT/'concepts/voice-strings.json').read_text())['pairs'];voice_to_soft=json.loads((ROOT/'concepts/voice-strings.json').read_text())['formal_to_soft']
 def voice(html):
  if voice_mode=='formal':
   for soft,formal in voice_pairs:html=html.replace(soft,formal)
  else:
   for formal,soft in voice_to_soft:html=html.replace(formal,soft)
  return html
 placement=json.loads((ROOT/'concepts/audio-placement.json').read_text())
 for _k,_sites in placement.items():
  if _k!='_note' and ident not in _sites:editorial['sections'][_k].pop('audio',None)
 for t in tools['pages']:t.update(tool_copy[t['tool']])
 editorial['sections']['calculator']=json.loads((ROOT/'concepts/calculator-page.json').read_text())
 editorial['sections']['calculator'].update({k:v for k,v in json.loads((ROOT/'concepts/calculator-copy.json').read_text())[ident].items() if k in ('intro','question','answer')})
 from sale_content import REFS
 REFS['calculator']=REFS['cost']
 pages=conf['pages'];origin=conf['public_origin'];routes={p['section']:p for p in pages}
 for folder,base in [(ROOT/f'concepts/{ident}',f'/concepts/{ident}/'),(ROOT/f'dist/hoban/{ident}','/')]:
  original=soup((folder/'index.html').read_text());sections={k:copy.deepcopy(original.select_one('section#'+('cost' if k=='calculator' else k))) for k in routes}
  for key,sec in sections.items(): assert sec is not None,key
  enriched=bool(editorial.get('enrichment_revision'))
  if enriched:
   from enrich_menu_content import augment
   for k in editorial['sections']:
    if k!='calculator':augment(sections[k],editorial['sections'][k],k,('/concepts/assets/' if base!='/' else '/assets/'))
  # Keep published prices and interactive estimates on separate pages.
  calc=sections['calculator'];calc['id']='calculator'
  inner=calc.select_one('.calc-inner')
  for el in list(inner.children):
   if getattr(el,'name',None) and not (el.has_attr('class') and any(c in el['class'] for c in ['section-heading','section-answer','calc-tabs','calc-panel'])):el.decompose()
  if enriched:
   from enrich_menu_content import replace_calculator
   replace_calculator(calc,('/concepts/assets/' if base!='/' else '/assets/'),editorial['sections']['cost'])
  model=editorial['sections']['calculator']
  calc.select_one('.section-answer h3').string=model['question']
  calc.select_one('.section-answer > p').string=model['answer']
  from calc_summary import summary_html
  calc.select_one('.section-answer').insert_after(fragment(summary_html(ident,json.loads((ROOT/'concepts/calculator-summary-copy.json').read_text())[ident])))
  for el in sections['cost'].select('.calc-tabs, .calc-panel'):el.decompose()
  action=fragment('<p><a class="editorial-link" href="'+base+'calculator/">분양계산기로 필요 자금 계산하기 ↗</a></p>')
  sections['cost'].select_one('.calc-inner').append(action)
  def absolute_attrs(doc):
   for el in doc.select('[href], [src], [srcset]'):
    for attr in ['href','src']:
     val=el.get(attr)
     if not val:continue
     if attr=='href' and val.startswith('#') and val[1:] in routes: el[attr]=base+routes[val[1:]]['slug']+'/'
     elif not val.startswith(('#','/')) and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',val):el[attr]=urljoin(base,val)
    if el.get('srcset'):
     el['srcset']=', '.join(urljoin(base,p.strip().split()[0])+' '+ ' '.join(p.strip().split()[1:]) for p in el['srcset'].split(','))
  def shared(doc,current):
   for el in doc.select('.concept-label'):el.decompose()
   doc.body['class']=doc.body.get('class',[])+['multipage']+(['detail-page'] if current else [])
   modal=doc.select_one('.reservation-modal')
   modal['class']=[name for name in modal['class'] if name!='is-open']
   modal['data-popup-preference-key']='hoban:'+ident+':popup-hidden-until'
   footer=fragment('<div class="popup-dismiss"><label for="popup-hide-today"><input type="checkbox" id="popup-hide-today"><span>오늘 하루 보지 않기</span></label><button type="button" data-close-popup>닫기</button></div>')
   modal.select_one('.reservation-dialog').append(footer)
   preference=doc.new_tag('script',src=('/concepts/popup-preference.js' if base!='/' else '/popup-preference.js'))
   doc.select_one('script[src$="concepts.js"]').insert_before(preference)
   def nav_link(href,text,active=False):
    a=doc.new_tag('a',href=href);a.string=text
    if active:a['aria-current']='page'
    return a
   for nav in doc.select('.desktop-nav, #mobile-menu'):
    nav.clear();mobile=nav.get('id')=='mobile-menu'
    for p in pages:
     if p['section']=='calculator':
      items=[(base+'calculator/',tools['cost_label'],current=='calculator')]+[(base+t['slug']+'/',t['label'],current==t['tool']) for t in tools['pages']]
      open_group=any(active for _,_,active in items)
      if mobile:
       group=doc.new_tag('div');group['class']=['mobile-nav-group'];span=doc.new_tag('span');span.string=tools['label'];group.append(span)
       for item in items:group.append(nav_link(*item))
      else:
       group=doc.new_tag('div');group['class']=['nav-dropdown']
       trigger=doc.new_tag('button',type='button');trigger['class']=['nav-dropdown-trigger']+(['active'] if open_group else []);trigger['aria-haspopup']='true';trigger['aria-expanded']='false';trigger.string=tools['label']+' ▾'
       menu=doc.new_tag('div');menu['class']=['nav-dropdown-menu']
       for item in items:menu.append(nav_link(*item))
       group.append(trigger);group.append(menu)
      nav.append(group)
      nav.append(nav_link(tools['real_transactions']['href'],tool_copy.get('realtx_label',tools['real_transactions']['label'])))
      continue
     nav.append(nav_link(base+p['slug']+'/',p['label'],p['section']==current))
    nav.append(nav_link('https://mohamoa.com/','모하모아'))
   assets=('/concepts/assets/' if base!='/' else '/assets/')
   dialog=modal.select_one('.reservation-dialog');dialog['class']=dialog.get('class',[])+['visit-popup']
   old_title=dialog.select_one('#reservation-title');dialog.select_one('.modal-kicker').decompose();old_title.decompose()
   close_button=dialog.select_one('.modal-close').extract()
   parts=[dialog.select_one(sel).extract() for sel in ['.modal-summary','.modal-switch','.modal-phone-only','.reservation-form','.popup-dismiss']]
   dialog.clear();dialog.append(close_button)
   dialog.append(fragment('<aside class="vp-visual"><span class="vp-kicker">이달의 핫 현장</span><div class="vp-logo">HOBAN <strong>SUMMIT</strong></div><p class="vp-place">첨단3지구 A7BL · 광주</p><h2 id="reservation-title">호반써밋 첨단3지구<br/>방문 상담 신청</h2><p class="vp-desc">모하모아 파트너 현장 상담을 지원합니다.<br/>신청해 주시면 담당자가 전화로 방문 일정을 조율합니다.</p><div class="vp-gift"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"/></svg><span><b>메가커피 아이스 아메리카노 1잔</b><small>호반써밋 현장 방문 상담 완료 시 · 1인 1회</small></span></div></aside>'))
   content=fragment('<div class="vp-content"><p class="vp-step">방문 상담 신청</p><h3>상담받을 단지를 선택해 주세요.</h3><label class="vp-select"><span>모델하우스 <b>필수</b></span><select aria-label="모델하우스"><option>첨단3지구 A7BL 호반써밋</option></select></label><p class="vp-benefit">호반써밋 현장에서 방문 상담을 마치면 음료 혜택을 받을 수 있습니다.</p></div>')
   box=content.select_one('.vp-content')
   for part in parts:box.append(part)
   dialog.append(content)
   bar=fragment('<div class="visit-bottom-bar" role="region" aria-label="방문 상담과 방문예약"><button class="visit-bottom-close" type="button" aria-label="하단 안내 닫기">×</button><img class="visit-bottom-logo" src="'+assets+'mohamoa-mark.png" alt="" width="38" height="38"><p class="visit-bottom-text"><b data-visit-date>호반써밋 첨단3지구</b><span>모델하우스 방문 상담·예약</span></p><button class="visit-bottom-consult" type="button" data-open-booking>상담하기</button><button class="visit-bottom-reserve" type="button" data-open-booking>방문예약하기</button></div>')
   modal.insert_after(bar)
   doc.select_one('.brand')['href']=base
   doc.select_one('script[src$="concepts.js"]')['src']=('/concepts/multipage.js' if base!='/' else '/multipage.js')
   link=doc.new_tag('link',rel='stylesheet',href=('/concepts/multipage.css' if base!='/' else '/multipage.css'));doc.head.append(link)
   if current=='calculator' or current in [t['tool'] for t in tools['pages']]:
    doc.head.append(doc.new_tag('link',rel='stylesheet',href=('/concepts/tools.css' if base!='/' else '/tools.css')))
    if current!='calculator':
     js=doc.new_tag('script',src=('/concepts/mohamoa-tools.js' if base!='/' else '/mohamoa-tools.js'));js['defer']='';doc.body.append(js)
   if enriched:
    css=doc.new_tag('link',rel='stylesheet',href=('/concepts/enriched.css' if base!='/' else '/enriched.css'));doc.head.append(css)
    if current=='calculator':
     js=doc.new_tag('script',src=('/concepts/mohamoa-calculator.js' if base!='/' else '/mohamoa-calculator.js'));js['defer']='';doc.body.append(js)
   for el in doc.select('a[href]'):
    if re.match(r'^https?://(www\.)?mohamoa\.com(/|$)',el['href']) and not el.find_parent('aside',class_='report-audio'):el['rel']=['nofollow','noopener']
   absolute_attrs(doc)
  def metadata(doc,title,desc,url,h1,faqs):
   doc.title.string=title
   doc.select_one('meta[name="description"]')['content']=desc
   for el in doc.select('link[rel="canonical"], meta[property="og:url"], script[type="application/ld+json"]'):el.decompose()
   doc.head.append(doc.new_tag('link',rel='canonical',href=url))
   doc.head.append(doc.new_tag('meta',property='og:url',content=url))
   doc.select_one('meta[property="og:title"]')['content']=title
   doc.select_one('meta[property="og:description"]')['content']=desc
   graph=[{'@type':'WebPage','@id':url+'#webpage','url':url,'name':title,'description':desc,'inLanguage':'ko-KR'},
    {'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'호반써밋 첨단3지구','item':origin+'/'}]+([{'@type':'ListItem','position':2,'name':h1,'item':url}] if url!=origin+'/' else [])}]
   if faqs:graph.append({'@type':'FAQPage','mainEntity':[{'@type':'Question','name':f['question'],'acceptedAnswer':{'@type':'Answer','text':f['answer']}} for f in faqs]})
   tag=doc.new_tag('script',type='application/ld+json');tag.string=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c');doc.head.append(tag)
  def faq(doc,items):
   sec=doc.new_tag('section',id='faq');sec['class']=['section-wrap','page-faq'];h=doc.new_tag('h2');h.string='자주 묻는 질문';sec.append(h)
   for f in items:
    d=doc.new_tag('details');summary=doc.new_tag('summary');summary.string=f['question'];d.append(summary);p=doc.new_tag('p');p.string=f['answer'];d.append(p)
    for path in f.get('refs',[]):
     a=doc.new_tag('a',href='https://hobansummit-kjcd.co.kr/'+path,target='_blank',rel='noopener');a.string='공식 자료 보기 ↗';d.append(a)
    sec.append(d)
   return sec
  # Main retains the visual story; detailed information is reachable via actual URLs.
  home=copy.deepcopy(original)
  for key in routes:
   old=home.select_one('#'+key);m=editorial['sections'][key]
   block=home.new_tag('section',id=key);block['class']=['section-wrap','route-summary']
   h=home.new_tag('h2');h.string=routes[key]['label'];block.append(h)
   p=home.new_tag('p');p.string=m['answer'];block.append(p)
   a=home.new_tag('a',href=base+routes[key]['slug']+'/');a['class']=['editorial-link'];a.string=routes[key]['label']+' 자세히 보기 ↗';block.append(a)
   if old:old.replace_with(block)
   else:home.select_one('#cost').insert_after(block)
  shared(home,None)
  faqs=[{'question':editorial['question'],'answer':editorial['answer']}]+editorial['faqs']
  home_h1=editorial.get('home_h1','호반써밋 첨단3지구')
  home.select_one('h1').string=home_h1
  metadata(home,editorial['title'],editorial['description'],origin+'/',home_h1,faqs)
  (folder/'index.html').write_text(voice(str(home)))
  for p in pages:
   key=p['section'];m=editorial['sections'][key];doc=copy.deepcopy(original);main=doc.select_one('main#content');main.clear()
   header=doc.new_tag('header');header['class']=['detail-header','section-wrap']
   bc=doc.new_tag('nav',attrs={'aria-label':'현재 위치'});a=doc.new_tag('a',href=base);a.string='홈';bc.append(a);bc.append(' / '+p['label']);header.append(bc)
   h=doc.new_tag('h1');h.string=p['h1'];header.append(h)
   lead=doc.new_tag('p');lead.string=('주택형별 공급금액과 납부 조건을 정리했어요. 가진 현금과 대출을 넣어 필요한 돈을 계산하고 싶다면 분양계산기가 있어요.' if key=='cost' else m['intro']);header.append(lead);main.append(header)
   content=copy.deepcopy(sections[key]);content.select_one('.section-heading').decompose();content.select_one('.section-answer h3').name='h2';main.append(content)
   from sale_content import REFS
   paths={path.split('#')[0] for path,_ in REFS[key]}
   relevant=[f for f in editorial['faqs'] if any(ref.split('#')[0] in paths for ref in f.get('refs',[]))]
   faqs=[{'question':m['question'],'answer':m['answer']}]+m.get('page_faqs',[])+relevant
   faqs=list({f['question']:f for f in faqs}.values())
   main.append(faq(doc,faqs))
   source=copy.deepcopy(original.select_one('#sources'));main.append(source)
   related=doc.new_tag('section');related['class']=['section-wrap','related-pages'];h=doc.new_tag('h2');h.string='이런 페이지도 있어요';related.append(h)
   for other in pages:
    if other==p:continue
    a=doc.new_tag('a',href=base+other['slug']+'/');a.string=other['label']+' ↗';related.append(a)
   main.append(related)
   shared(doc,key);metadata(doc,p['title'],p['description'],origin+'/'+p['slug']+'/',p['h1'],faqs)
   dest=folder/p['slug'];dest.mkdir(exist_ok=True);(dest/'index.html').write_text(voice(str(doc)))
  for t in tools['pages']:
   doc=copy.deepcopy(original);main=doc.select_one('main#content');main.clear()
   header=doc.new_tag('header');header['class']=['detail-header','section-wrap']
   bc=doc.new_tag('nav',attrs={'aria-label':'현재 위치'});a=doc.new_tag('a',href=base);a.string='홈';bc.append(a);bc.append(' / '+tools['label']+' / '+t['label']);header.append(bc)
   h=doc.new_tag('h1');h.string=t['h1'];header.append(h)
   lead=doc.new_tag('p');lead.string=t['intro'];header.append(lead);main.append(header)
   tool_section=fragment('<section class="section-wrap tool-section" id="'+t['tool']+'-tool"><h2 class="sr-only">'+t['label']+'</h2><div data-tool="'+t['tool']+'"'+(' data-areas="'+t['areas']+'"' if t.get('areas') else '')+'></div><noscript><p>계산기는 자바스크립트가 켜져 있어야 움직여요.</p></noscript></section>')
   main.append(tool_section)
   main.append(faq(doc,t['faqs']))
   related=doc.new_tag('section');related['class']=['section-wrap','related-pages'];h=doc.new_tag('h2');h.string='이런 페이지도 있어요';related.append(h)
   for href,text in [(base+'calculator/',tools['cost_label'])]+[(base+o['slug']+'/',o['label']) for o in tools['pages'] if o is not t]+[(base+'price/','분양가'),(base+'visit/','오시는 길')]:
    a=doc.new_tag('a',href=href);a.string=text+' ↗';related.append(a)
   main.append(related)
   shared(doc,t['tool']);metadata(doc,t['title'],t['description'],origin+'/'+t['slug']+'/',t['h1'],t['faqs'])
   dest=folder/t['slug'];dest.mkdir(exist_ok=True);(dest/'index.html').write_text(voice(str(doc)))
  urls=[origin+'/']+[origin+'/'+p['slug']+'/' for p in pages]+[origin+'/'+t['slug']+'/' for t in tools['pages']]
  xml='<?xml version="1.0" encoding="UTF-8"?>\n<!-- Local release candidate; do not submit before production noindex and live URL checks. -->\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(u)+'</loc></url>' for u in urls)+'</urlset>\n'
  (folder/'sitemap.xml').write_text(xml)
  if base=='/':
   used=''.join(p.read_text(errors='ignore') for p in folder.rglob('index.html'))
   for f in list((folder/'assets'/'audio').glob('*')) if (folder/'assets'/'audio').exists() else []:
    if f.name not in used:f.unlink()
  if base=='/':
   for name in ['multipage.js','multipage.css','popup-preference.js','tools.css','mohamoa-tools.js']+(['enriched.css','mohamoa-calculator.js'] if enriched else []):shutil.copy2(ROOT/'concepts'/name,folder/name)
   (folder/'robots.txt').write_text('User-agent: *\nAllow: /\n# Local draft: noindex in HTML and headers; sitemap is a release candidate, not submitted.\n')
 print(ident+': home + 8 static detail pages + 3 calculator tool pages, draft sitemap and per-URL metadata built')
 # Keep the brief generated from the same route/editorial source as the pages.
 from sale_content import REFS
 brief=ROOT/f'concepts/{ident}/PROJECT.md'
 text=brief.read_text()+'''\n## 2026-10-21 메뉴별 페이지 분리 — 로컬 메뉴별 시안\n\n이 절이 앞선 단일 URL·앵커·로컬 canonical 해당 없음 기록보다 우선한다. 메인은 요약과 상세 진입 링크, 각 상세는 해당 주제의 원고·질문·표·공식 도면·FAQ를 제공한다. 기존 첫 답·공식 사실은 보존한다. canonical은 아래 실제 소유 도메인의 예정 상세 URL이며 로컬은 noindex를 유지한다. 운영 배포·색인 요청은 미실행이다.\n\n| 메뉴 | 예정 canonical | title | H1 | 메타 설명 |\n|---|---|---|---|---|\n'''
 for p in pages:
  text+='| '+p['label']+' | '+origin+'/'+p['slug']+'/ | '+p['title'].replace('|','\\|')+' | '+p['h1'].replace('|','\\|')+' | '+p['description'].replace('|','\\|')+' |\n'
 text+='\n## 상세별 질문·근거·검색 의도\n\n'
 for p in pages:
  m=editorial['sections'][p['section']]
  text+='### '+p['label']+'\n\n- URL: '+origin+'/'+p['slug']+'/\n- 독자 질문: '+m['question']+'\n- 직접 답: '+m['answer']+'\n- 근거: '+ ' / '.join('https://hobansummit-kjcd.co.kr/'+path for path,_ in REFS[p['section']])+'\n- 사실 확인일: 2026-10-07. 페이지 구조 수정일: 2026-10-21. 날짜를 새 사실 조사로 바꾸지 않았다.\n- 검색 표현: '+p['h1']+' — '+p['search_status']+'\n- 보완 링크: 같은 사이트의 다른 상세 및 홈으로 실제 HTML 링크 제공.\n\n'
 if editorial.get('enrichment_revision'):text+='\n## 본문 자료 보강 2026-10-22\n\n공식 재확인 자료: ../research/20261021/manifest.json 및 원문 PDF. 모하모아 리포트 전문·음성: 같은 조사 폴더의 mohamoa-reports-full.json, mohamoa-audio-full.json. 각 sections.details/page_faqs/audio에 원문과 적용 근거를 보존한다. 가격·확장비는 공고 당시 값이며 현재 판매 조건은 아니다. 공통 계산기는 Mohamoa 원본에서 이식했다. 공개·색인·Git push 미실행.\n\n'
 if editorial.get('copy_review_revision'):text+='\n## 2026-10-22 한국어 본문·메타 실독 수정\n\n시로코·경복궁 전문과 기존 분양 지침을 대조해 본문·FAQ·제목·메타를 자연화했다. 담당별 실독·before/after는 ../research/20261022-natural-korean/review-*.md, 최종 SHA와 HTML 검증은 changes-NN.json 및 ../../NATURAL_KOREAN_REVISION_20261022.md를 참고한다. 원문 사실·조건·음성과 예약 기능을 유지했다. 이 기록은 색인·순위·AI 인용 완료를 뜻하지 않는다. 초기 enrich_version.py 재가져오기로 검토한 원고를 덮어쓰지 않는다.\n\n'
 text+='재생성·검증·원문 보관·미실행 경계는 ../../MENU_PAGE_SPLIT_PILOT.md를 참고한다.\n'
 if editorial.get('home_h1'):
  text=re.sub(r'(?m)^- H1: .*$', '- H1: '+editorial['home_h1'],text,count=1)
  text+='\n## 2026-10-22 메인 검색 의도 정리\n\n메인 title·H1·description·OG·첫 소개를 모델하우스/분양정보 목적에 맞췄다. 상세페이지 제목·본문·URL과 예약 기능은 유지한다. 첫 소개: '+editorial['hero_copy']+'\n기록: ../../HOME_TITLE_REVISION_20261022.md. 로컬 noindex 유지; 운영 배포·색인 요청은 미실행.\n'
 brief.write_text(text.replace('changes-NN.json','changes-'+ident+'.json'))
