"""Render authored whole-page sale content while preserving booking/calculator controls."""
import html,re
esc=lambda x:html.escape(str(x),quote=True)
OFFICIAL='https://hobansummit-kjcd.co.kr/'
KEYS=['overview','location','premium','arrangement','types','cost','directions']
REFS={
 'overview':[('sub/planning.php','공식 사업개요'),('images/gonggo7bl_01_v2.pdf','A7 모집공고'),('images/gonggo8bl_01_v2.pdf#page=11','A8 모집공고')],
 'location':[('sub/location.php','공식 입지 지도·계획 기준')],
 'premium':[('sub/premium.php','공식 프리미엄'),('sub/block.php','단지 시설 배치'),('images/gonggo8bl_01_v2.pdf#page=53','A8 커뮤니티 안내')],
 'arrangement':[('sub/block.php','공식 단지·동호수배치도')],
 'types':[('sub/unit_7bl.php','A7 공식 평면도'),('sub/unit_8bl.php','A8 공식 평면도')],
 'cost':[('images/gonggo7bl_01_v2.pdf#page=8','A7 공급금액·납부 조건'),('images/gonggo8bl_01_v2.pdf#page=12','A8 공급금액·납부 조건')],
 'directions':[('sub/contact.php','공식 모델하우스 위치·운영 안내')]
}
KICKERS=dict(zip(KEYS,['PROJECT','LOCATION','PREMIUM','SITE PLAN','UNIT PLAN','BUDGET','VISIT']))
def sources(refs):
 return '<p class="source-note">공식 자료 확인일 2026.10.07 · '+' · '.join('<a href="'+OFFICIAL+p+'" target="_blank" rel="noopener">'+esc(label)+' ↗</a>' for p,label in refs)+'</p>'
def heading(key,m):
 return '<div class="section-heading"><div><span class="section-number">01 / '+KICKERS[key]+'</span><h2>'+esc(m['title'])+'</h2></div><p>'+esc(m['intro'])+'</p></div>'
def direct(key,m):
 return '<div class="section-answer"><h3>'+esc(m['question'])+'</h3><p>'+esc(m['answer'])+'</p>'+sources(REFS[key])+'</div>'
def cards(m,kind='fact'):
 css='feature-grid' if kind=='feature' else 'fact-grid'
 item='feature' if kind=='feature' else 'fact-card'
 return '<div class="'+css+'">'+''.join('<article class="'+item+'"><h3>'+esc(c['title'])+'</h3><p>'+esc(c['text'])+'</p>'+('<a class="editorial-link" href="'+esc(c['link'])+'">'+esc(c.get('label','관련 내용 보기'))+' ↗</a>' if c.get('link') else '')+'</article>' for c in m['cards'])+'</div>'
def table(caption,headers,rows):
 return '<div class="table-scroll"><table class="focus-table"><caption>'+esc(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def render_sections(editorial,data,original):
 models=editorial['sections'];assert set(models)==set(KEYS)
 result={};units=data['units']
 for key,m in models.items():
  prefix=heading(key,m)+direct(key,m)
  body=''
  if key=='overview':
   body=cards(m)+table('호반써밋 첨단3지구 블록별 공급 정보',['구분','A7블록','A8블록'],[
    ['사업지','광주 북구 월출동','전남 장성군 진원면'],['공급 규모','356세대 · 5개동','449세대 · 6개동'],['주택형','84A · 84B','117A · 117B · 135'],['규모','지하 1층~지상 20층','지하 1층~지상 18~20층'],['입주 예정','2028년 9월','2028년 10월']])
   body+='<p class="source-note">공고의 전체 공급 규모이며 현재 잔여 물량과 다릅니다. 정확한 입주일은 추후 안내됩니다. 시행사는 첨단678피에프브이 주식회사, 시공사는 (주)호반건설입니다.</p>'
  elif key=='location':
   body=re.search(r'<figure class="official-image location-image">.*?</figure>',original[key],re.S).group()+cards(m)
  elif key=='premium':body=cards(m,'feature')
  elif key=='arrangement':
   body='<div class="fact-grid">'+''.join(re.findall(r'<figure class="official-image">.*?</figure>',original[key],re.S))+'</div>'+cards(m)
  elif key=='types':
   body=re.search(r'<div class="unit-select-row">.*?</div>',original[key],re.S).group()
   body+=re.search(r'<figure class="official-image">.*?</figure>',original[key],re.S).group()
   body+=table('공고 기준 주택형별 전용면적·공급면적',['블록·주택형','전용면적','공급면적'],[[u['block']+' · '+u['id']+'형',f'{u["exclusive_area"]:.4f}㎡',f'{u["supply_area"]:.4f}㎡'] for u in units])+cards(m)
  elif key=='directions':
   body=cards(m)+'<div class="visit-address"><span>호반써밋 첨단3지구 모델하우스</span><strong>광주 서구 마륵동 164-11</strong><p>공식 안내: 오전 10시~오후 5시 30분 · 상무역 2번 출구에서 약 200m</p><p>모하모아 담당자와 방문 시간을 확인한 뒤 방문해 주세요.</p><button class="primary" data-open-booking>방문예약 신청</button> <a class="secondary" href="tel:16005184">전화로 문의하기 ↗</a></div>'
   body+='<p class="source-note">이 페이지의 상담은 모하모아 담당자에게 연결됩니다. 시행사·시공사 공식 상담 창구와는 다릅니다.</p>'
  else:
   price_table=table('2026년 6월 5일 공고의 주택형별 분양가 범위',['주택형','최저~최고 공급금액'],[[u['block']+' · '+u['id']+'형',f'{u["prices"][0]["won"]//10000:,}~{u["prices"][-1]["won"]//10000:,}만원'] for u in units])
   old=original[key]
   old_heading=re.search(r'<div class="section-heading">.*?</h2></div><p>.*?</p></div>',old,re.S).group()
   cost=old.replace(old_heading,prefix+price_table+cards(m),1).replace('2026.10.01','2026.10.07')
   cost=cost.replace('주택형과 층을 선택한 뒤 보유 현금과 예상 대출금을 입력해 주세요.',esc(m['calc_intro']))
   cost=cost.replace('옵션표나 별도 안내에서 확인한 비용을 입력해 주세요. 발코니 확장비, 옵션 비용, 세금은 자동으로 입력되지 않습니다.',esc(m['extras_intro']))
   result[key]=cost.replace('<section id="cost"','<section id="cost" data-content-revision="full-20261007"',1)
   continue
  result[key]='<section id="'+key+'" data-content-revision="full-20261007" class="section-wrap">'+prefix+body+sources(REFS[key])+'</section>'
 # Each variant has authored questions, not a fixed subset of the old FAQ list.
 faqs=[{'question':editorial['question'],'answer':editorial['answer'],'refs':[r['path'] for r in editorial['refs']]}]+editorial['faqs']
 faq_html=''
 for f in faqs:
  faq_html+='<details><summary>'+esc(f['question'])+'</summary><p>'+esc(f['answer'])+'</p>'+(sources([(p,'관련 공식 자료') for p in f['refs']]) if f['refs'] else '')+'</details>'
 result['faq']='<section id="faq" class="section-wrap"><div class="section-heading"><div><span class="section-number">08 / QUESTIONS</span><h2>'+esc(editorial['faq_title'])+'</h2></div><p>'+esc(editorial['faq_intro'])+'</p></div><div class="faq-list">'+faq_html+'</div></section>'
 result['sources']=original['sources'].replace('2026.10.01','2026.10.07')
 return result,faqs
