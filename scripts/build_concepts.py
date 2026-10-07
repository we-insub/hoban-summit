#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build ten Hoban design concepts with shared, source-checked data."""
import argparse
import html
import json
import re
import shutil
from concept_variants import VARIANTS, focus_section
from site_branding import build_branding
from sale_content import render_sections, REFS as SECTION_REFS
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'concepts'
parser = argparse.ArgumentParser()
parser.add_argument('--version', choices=[str(n).zfill(2) for n in range(1,11)])
args = parser.parse_args()
e = lambda x: html.escape(str(x), quote=True)
data = json.loads((BASE / 'source-data.json').read_text())
version_plan = json.loads((BASE / 'version-plan.json').read_text())
profiles = {v['id']: v for v in version_plan['versions']}
official = 'https://hobansummit-kjcd.co.kr/'
menu = [('overview','사업개요'),('location','입지환경'),('premium','프리미엄'),('arrangement','단지배치'),('types','평면타입'),('directions','오시는 길')]
nav = ''.join(f'<a href="#{key}">{name}</a>' for key,name in menu) + '<a href="https://mohamoa.com/">모하모아</a>'
base = (ROOT / 'templates' / 'reservation-template.html').read_text()
popup = base[base.index('    <div class="reservation-modal'):base.index('    <main id="content">')]
popup = popup.replace('CHAMPIONS CITY','HOBAN SUMMIT · CHEOMDAN 3').replace('챔피언스시티 상담 내용 예약','호반써밋 첨단3지구 상담예약')
popup = popup.replace('<form class="reservation-form">','''<div class="modal-summary"><div><p class="eyeline">FIRST PAYMENT</p><strong>1차 계약금<br />1,000만원</strong><p>모집공고 기준, 전체 계약금은 분양가의 5%입니다.</p></div><div><a class="phone-link" href="tel:16005184">전화 상담하기 ↗</a><p>궁금한 주택형이나 방문 일정을 모하모아 담당자에게 문의하세요.</p><p class="modal-source">2026.06.05 모집공고의 납부 조건입니다. 현재 계약 조건과 남아 있는 동·호수는 상담 시 확인해 주세요.</p></div></div>
<div class="modal-switch" aria-label="상담 방식"><button type="button" data-modal-mode="phone" aria-pressed="true">전화 상담</button><button type="button" data-modal-mode="booking" aria-pressed="false">방문예약</button></div><p class="modal-phone-only">통화가 어려우신가요? ‘방문예약’에서 연락처와 방문을 원하는 날짜·시간을 남겨 주세요.</p><form class="reservation-form" hidden>''')
popup = popup.replace('<label class="reservation-trap"', '<label><span>관심 주택형 (선택)</span><select name="interest"><option value="">주택형 선택</option>' + ''.join(f'<option value="{u["id"]}">{u["block"]} · {u["id"]}형</option>' for u in data['units']) + '</select></label><label class="reservation-trap"')
popup = popup.replace('방문 일시는 한국 시간 기준입니다. 입력한 정보는 모하모아에 상담 예약 신청 목적으로 전달됩니다.', '방문 날짜와 시간은 한국 시간 기준으로 입력해 주세요. 모하모아 담당자가 신청 내용을 확인한 후 연락드립니다.')
popup = popup.replace('>예약</button>','>상담예약 신청</button>')

def heading(number, kicker, title, description):
 return f'<div class="section-heading"><div><span class="section-number">{number} / {kicker}</span><h2>{title}</h2></div><p>{description}</p></div>'
def note(path, label):
 return f'<p class="source-note">확인일 2026.10.01 · <a href="{official}{path}" target="_blank" rel="noopener">{label} ↗</a></p>'

def photo(filename, alt, css='', eager=False):
 stem=Path(filename).stem
 maxw=1200 if stem.startswith('official-design') else 1920 if stem.startswith('official-') else 1672
 height=1574 if maxw==1200 else 965 if maxw==1920 else 941
 dimensions=json.loads((BASE/'assets'/'photo-sizes.json').read_text()).get(stem)
 if dimensions: maxw,height=dimensions['width'],dimensions['height']
 return f'<img class="{css}" src="../assets/{stem}-{maxw}.webp" srcset="../assets/{stem}-960.webp 960w, ../assets/{stem}-{maxw}.webp {maxw}w" sizes="(max-width: 850px) 100vw, {"100vw" if eager else "65vw"}" width="{maxw}" height="{height}" alt="{e(alt)}" loading="{"eager" if eager else "lazy"}" decoding="async" {"fetchpriority=high" if eager else ""}>'

faq = [
 ('A7블록과 A8블록은 어떻게 다른가요?', 'A7블록은 광주 북구 월출동에 있으며, 84A·84B형 총 356세대입니다. A8블록은 전남 장성군 진원면에 있으며, 117A·117B·135형 총 449세대입니다. 두 블록을 합한 805세대는 전체 공급 세대수로, 현재 남아 있는 세대수를 뜻하지 않습니다.', 'sub/planning.php'),
 ('모델하우스는 단지와 같은 곳에 있나요?', '아니요. 모델하우스는 광주 서구 마륵동 164-11에 있고, 단지는 첨단3지구 A7·A8블록에 들어섭니다. 방문 전 모델하우스 운영 여부와 방문 시간을 확인해 주세요.', 'sub/contact.php'),
 ('계산기에 나오는 분양가는 언제 기준인가요?', '2026년 6월 5일 모집공고에 나온 주택형·층별 분양가입니다. 주택형과 층을 선택하면 해당 금액이 표시되며 직접 수정할 수는 없습니다. 현재 남아 있는 동·호수의 가격과 계약 조건은 별도로 확인해 주세요.', 'sub/gonggo.php'),
 ('1차 계약금 1,000만원만 내면 계약금 납부가 끝나나요?', '아니요. 모집공고상 전체 계약금은 분양가의 5%입니다. 계약할 때 1차 계약금 1,000만원을 내고, 나머지 계약금은 계약 후 30일 이내에 납부하는 조건입니다. 중도금은 60%, 잔금은 35%이며, 계약 전 변경된 조건이 있는지 확인해 주세요.', 'sub/gonggo.php'),
 ('발코니 확장비와 옵션 비용도 분양가에 포함되나요?', '아니요. 모집공고의 분양가에는 발코니 확장, 시스템에어컨, 추가 선택품목 비용이 포함되지 않습니다. 계산할 때는 ‘추가비용’에 확인한 금액을 입력해 주세요. 입력하지 않은 비용은 계산 결과에 포함되지 않습니다.', 'sub/gonggo.php'),
 ('입지 안내에 나온 교통시설과 학교는 모두 확정됐나요?', '아니요. 단지 주변 초·중·고와 유치원 부지, 도시철도 2호선 2단계와 연결도로는 계획 사항입니다. 지도 속 첨단역·지스트역·신용역은 가칭이며, 역까지의 거리나 개통 시기를 보장하지 않습니다. 개통·개교 일정과 학교 배정은 해당 기관의 최신 안내를 확인해 주세요.', 'sub/location.php'),
 ('방문예약을 신청하면 바로 확정되나요?', '신청 후 모하모아 담당자가 연락드려 방문 시간을 확인해 드립니다. 담당자의 안내를 받은 뒤 방문해 주세요. 선택 항목인 홍보 동의에 체크하지 않아도 예약을 신청할 수 있습니다.', None),
 ('계산기에 입력한 현금이나 대출금도 저장되나요?', '아니요. 자금 계산에 입력한 금액은 브라우저 안에서만 사용하며 상담예약 정보로 전송하지 않습니다. 계산 결과는 참고용으로, 실제 대출 가능 금액이나 세금과는 다를 수 있습니다.', None)
]
faq_html = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p>' + (f'<p><a href="{official}{path}" target="_blank" rel="noopener">공식 근거 확인 ↗</a> · 확인일 2026.10.01</p>' if path else '') + '</details>' for q,a,path in faq)
unit_options = ''.join(f'<option value="{u["id"]}">{u["block"]} · {u["id"]}형</option>' for u in data['units'])
price_rows = ''.join(f'<tr><th scope="row">{u["block"]} {u["id"]}형</th><td>{u["prices"][0]["won"]:,}~{u["prices"][-1]["won"]:,}원</td><td><a href="{u["source_url"]}#page={u["pdf_page"]}">공고 {u["pdf_page"]}쪽 ↗</a></td></tr>' for u in data['units'])
calculator = f'''<section id="cost" class="calc-section"><div class="calc-inner">{heading('07','BUDGET','주택형별 분양가와<br />필요 자금 계산','주택형과 층을 선택하면 모집공고의 분양가가 표시됩니다. 보유 현금과 예상 대출금을 입력해 추가로 필요한 금액을 확인해 보세요.')}
<div class="calc-tabs" role="tablist" aria-label="비용계산 메뉴">{''.join(f'<button id="tab-{key}" role="tab" aria-controls="panel-{key}" aria-selected="{str(i==0).lower()}" tabindex="{0 if i==0 else -1}" data-cost-tab="{key}">{label}</button>' for i,(key,label) in enumerate([('budget','자금 모의계산'),('schedule','납부계획'),('extras','추가비용'),('guide','계산 안내')]))}</div>
<section class="calc-panel" id="panel-budget" role="tabpanel" aria-labelledby="tab-budget"><h3>내 집 마련 자금 모의계산</h3><p class="lead">주택형과 층을 선택한 뒤 보유 현금과 예상 대출금을 입력해 주세요.</p><div class="calc-fields">
<label class="calc-field">주택형 선택<select id="budget-unit">{unit_options}</select></label><label class="calc-field">층 구분<select id="budget-floor">{''.join(f'<option value="{i}">{r["floor"]}</option>' for i,r in enumerate(data['units'][0]['prices']))}</select></label>
<label class="calc-field">분양가 (모집공고 기준)<div class="input-wrap"><input id="budget-price" value="49,400" readonly /><span>만원</span></div></label>
<label class="calc-field">보유 현금<div class="input-wrap"><input id="budget-cash" inputmode="decimal" type="number" min="0" step="0.01" placeholder="직접 입력" /><span>만원</span></div></label>
<label class="calc-field">예상 대출금<div class="input-wrap"><input id="budget-loan" inputmode="decimal" type="number" min="0" step="0.01" placeholder="직접 입력" /><span>만원</span></div></label>
<label class="calc-field">계약금 비율 · 공고 기준<div class="input-wrap"><input value="5" readonly /><span>%</span></div></label>
<label class="calc-field">중도금 비율 · 공고 기준<div class="input-wrap"><input value="60" readonly /><span>%</span></div></label></div>
<p id="price-context" class="calc-notice">A7BL · 84A형 · 1층 · 2026.06.05 공고의 공급금액입니다.</p>
<p class="calc-notice">발코니 확장, 유상옵션, 취득 관련 비용은 분양가에 포함되지 않습니다. 입력하지 않은 금액은 0원으로 계산합니다.</p><p class="calc-error" id="budget-error" role="status"></p><div class="budget-result" aria-live="polite"><div class="budget-item"><span>총 필요 금액</span><strong id="result-total">4억 9,400만원</strong></div><div class="budget-item"><span>대출 외에 준비할 금액</span><strong id="result-equity">4억 9,400만원</strong></div><div class="budget-item"><span>추가로 필요한 금액</span><strong id="result-gap">4억 9,400만원</strong></div></div></section>
<section class="calc-panel" id="panel-schedule" role="tabpanel" aria-labelledby="tab-schedule" hidden><h3>선택한 주택형의 납부 금액</h3><p class="lead">모집공고 기준 계약금 5%·중도금 60%·잔금 35%입니다. 아래 금액은 선택한 주택형과 층에 따라 바뀝니다.</p><div class="schedule-grid"><div><small>01 / 1차 계약금</small><strong id="result-first">1,000만원</strong><span>계약 시</span></div><div><small>02 / 2차 계약금</small><strong id="result-second">1,470만원</strong><span>계약 후 30일 이내</span></div><div><small>03 / 중도금 총액</small><strong id="result-interim">2억 9,640만원</strong><span>공고 기준 6회 분납</span></div><div><small>04 / 잔금</small><strong id="result-balance">1억 7,290만원</strong><span>입주지정일</span></div></div><p class="calc-notice">예상 대출금은 필요한 현금을 계산하는 데만 사용합니다. 중도금 납부 시점별 대출 실행과 이자, 대출 가능 여부는 따로 확인해 주세요.</p></section>
<section class="calc-panel" id="panel-extras" role="tabpanel" aria-labelledby="tab-extras" hidden><h3>분양가 외 추가 비용</h3><p class="lead">옵션표나 별도 안내에서 확인한 비용을 입력해 주세요. 발코니 확장비, 옵션 비용, 세금은 자동으로 입력되지 않습니다.</p><div class="calc-fields"><label class="calc-field">발코니 확장·선택 옵션 합계<div class="input-wrap"><input id="budget-options" type="number" min="0" step="0.01" inputmode="decimal" placeholder="확인한 금액 입력" /><span>만원</span></div></label><label class="calc-field">취득 관련 세금·기타 비용 합계<div class="input-wrap"><input id="budget-fees" type="number" min="0" step="0.01" inputmode="decimal" placeholder="확인한 금액 입력" /><span>만원</span></div></label></div><p class="calc-notice">입력한 비용은 총 필요 금액에 더해집니다. 취득세율과 중과·감면 여부는 이 계산기에서 판단하지 않습니다.</p></section>
<section class="calc-panel" id="panel-guide" role="tabpanel" aria-labelledby="tab-guide" hidden><h3>금액의 근거와 계산 범위</h3><p class="lead">아래 가격은 모집공고에 나온 주택형별 최저·최고 분양가입니다. 현재 남아 있는 세대의 가격이나 판매 조건과는 다를 수 있습니다.</p><div class="table-scroll"><table class="price-table"><caption>공고 기준 주택형별 공급금액 범위</caption><thead><tr><th>주택형</th><th>공급금액 범위</th><th>근거</th></tr></thead><tbody>{price_rows}</tbody></table></div><p class="calc-notice">총 필요 금액 = 공급금액 + 입력한 추가 비용. 자기자금 = 총 필요 금액 − 예상 대출금. 부족분 = 자기자금 − 보유 현금(최소 0원). 확인일 2026.10.01.</p></section>
</div></section>'''

content = f'''<section id="overview" class="section-wrap">{heading('01','PROJECT','호반써밋 첨단3지구<br />사업개요','A7블록은 광주 북구 월출동, A8블록은 전남 장성군 진원면에 들어섭니다. 블록별 세대수와 주택형을 확인해 보세요.')}
<div class="project-answer"><p>호반써밋 첨단3지구는 A7·A8블록 총 805세대 규모의 단지입니다. A7블록에는 84A·84B, A8블록에는 117A·117B·135형이 공급됩니다. 모델하우스는 사업지와 다른 곳인 광주 서구 마륵동 164-11에 있습니다.</p><a href="#directions">모델하우스 위치 확인하기 ↗</a></div><div class="fact-grid"><article class="fact-card"><p class="eyeline">A7 BLOCK</p><h3>A7블록 · 84A·84B</h3><strong>356세대</strong><dl><dt>사업지</dt><dd>광주 북구 월출동 · 첨단3지구 A7BL</dd><dt>주택형</dt><dd>84A · 84B</dd><dt>규모</dt><dd>지하 1층~지상 20층 · 5개동</dd><dt>입주</dt><dd>2028년 9월 예정 · 정확한 입주일은 추후 안내</dd></dl></article><article class="fact-card"><p class="eyeline">A8 BLOCK</p><h3>A8블록 · 117A·117B·135</h3><strong>449세대</strong><dl><dt>사업지</dt><dd>전남 장성군 진원면 · 첨단3지구 A8BL</dd><dt>주택형</dt><dd>117A · 117B · 135</dd><dt>규모</dt><dd>지하 1층~지상 18~20층 · 6개동</dd><dt>입주</dt><dd>2028년 10월 예정 · 정확한 입주일은 추후 안내</dd></dl></article></div>{note('sub/planning.php','공식 사업개요')}{note('sub/gonggo.php','공급 위치·규모의 모집공고')}</section>
<section id="location" class="section-wrap">{heading('02','LOCATION','첨단 생활권의<br />교육·교통·생활시설','롯데마트 첨단점과 첨단종합병원, 국립광주과학관까지. 생활시설의 위치와 단지 주변에 계획된 학교·교통시설을 함께 살펴보세요.')}<figure class="official-image location-image"><a href="../assets/location.jpg" target="_blank" rel="noopener"><img src="../assets/location.jpg" alt="호반써밋 첨단3지구 A7·A8 위치와 학교 예정 부지, 롯데마트, 첨단종합병원, 도시철도 2호선 계획을 표시한 공식 입지 지도" loading="lazy" /></a><figcaption>이미지를 누르면 입지 지도를 크게 볼 수 있습니다. 지도에 적힌 예정 연도는 제작 당시의 계획이며, 최신 개통·개교 일정과 다를 수 있습니다.</figcaption></figure><div class="fact-grid"><article class="fact-card"><p class="eyeline">LIFE</p><h3>쇼핑·의료·문화시설</h3><p>첨단 생활권에는 롯데마트 첨단점, 첨단종합병원, 국립광주과학관이 있습니다. 장보기나 병원 방문, 가족 나들이에 필요한 시설의 위치를 지도에서 살펴보세요.</p></article><article class="fact-card"><p class="eyeline">EDUCATION</p><h3>단지 주변 학교 조성 계획</h3><p>A7·A8블록 주변에 초·중·고와 유치원 부지가 계획돼 있습니다. 첨단 생활권의 광주과학기술원(GIST)과 광주과학고 위치도 함께 볼 수 있습니다. 예정 학교의 개교 시기와 자녀의 배정학교는 별도로 확인해 주세요.</p></article><article class="fact-card"><p class="eyeline">TRANSPORT</p><h3>도시철도 2호선과 연결도로 계획</h3><p>도시철도 2호선 2단계와 상무지구~첨단산단 도로, 첨단3지구 진입도로가 계획 사항으로 소개돼 있습니다. 지도에 표시된 첨단역·지스트역·신용역은 가칭입니다. 단지에서 역까지의 실제 거리와 이용 가능 시기는 별도로 확인해야 합니다.</p></article><article class="fact-card"><p class="eyeline">WORK</p><h3>첨단산업단지와 이어지는 생활권</h3><p>입지 지도에서 광주첨단과학국가산업단지와 삼성전자 3캠퍼스, 국가AI데이터센터의 위치를 볼 수 있습니다. 첨단 일대에서 근무하신다면 직장과 단지 사이의 출퇴근 경로를 비교해 보세요.</p></article></div>{note('sub/location.php','공식 입지환경·계획의 기준 시점')}<p class="source-note">시설 안내: <a href="https://culture.lottemart.com/cu/customer/branchSearch/main.do">롯데마트 문화센터 지점 안내</a> · <a href="https://www.cheomdanhosp.co.kr/">첨단종합병원</a> · <a href="https://www.sciencecenter.or.kr/kor/menu/sub.do?menuId=20_58_60">국립광주과학관 위치 안내</a>. 시설별 운영시간과 휴무일은 방문 전 확인해 주세요.</p></section>
<section id="premium" class="section-wrap">{heading('03','PREMIUM','분양가부터<br />단지 안의 시설까지','분양가 상한제 적용, 다섯 가지 주택형, A8블록의 커뮤니티 시설 계획을 확인해 보세요. 우리 가족에게 필요한 공간과 비용을 함께 비교할 수 있습니다.')}<div class="feature-grid"><article class="feature"><p class="eyeline">PRICE</p><h3>분양가 상한제 적용</h3><p>분양가 상한제가 적용되는 단지입니다. 주택형·층별 분양가는 모집공고에서 확인할 수 있으며, 발코니 확장과 유상옵션 비용은 별도입니다.</p><a class="editorial-link" href="#cost">주택형별 분양가 확인 ↗</a></article><article class="feature"><p class="eyeline">SPACE</p><h3>84·117·135㎡ 주택형</h3><p>A7블록은 84A·84B, A8블록은 117A·117B·135형으로 구성됩니다. 숫자는 전용면적의 약식 표기입니다. 정확한 면적과 방·거실 배치는 평면도에서 비교해 보세요.</p><a class="editorial-link" href="#types">평면도 비교하기 ↗</a></article><article class="feature"><p class="eyeline">COMMUNITY</p><h3>A8블록 커뮤니티 시설 계획</h3><p>A8블록에는 피트니스와 골프연습장, 작은도서관, 에듀센터, 게스트하우스 등이 계획돼 있습니다. 설치 범위와 운영 방식, 이용료는 계약 전 확인해 주세요. 블록별 시설은 다를 수 있습니다.</p><a class="editorial-link" href="{official}images/gonggo8bl_01_v2.pdf#page=53">A8 모집공고의 시설 안내 ↗</a></article></div>{note('sub/premium.php','공식 프리미엄')}{note('images/gonggo8bl_01_v2.pdf','A8 공급 규모·입주시기·부대복리시설')}</section>
<section id="arrangement" class="section-wrap">{heading('04','SITE PLAN','A7·A8블록<br />단지배치도','배치도에서 동의 위치와 방향, 출입구를 살펴보세요. 이미지를 누르면 동·호수표를 포함한 전체 도면을 볼 수 있습니다.')}<div class="fact-grid">{''.join(f'<figure class="official-image"><a href="../assets/block-a{n}.jpg" target="_blank" rel="noopener"><div class="plan-crop"><img src="../assets/block-a{n}.jpg" alt="공식 A{n}BL 단지배치도 상단 미리보기" loading="lazy" /></div></a><figcaption>A{n}BL 단지배치도입니다. 이미지를 누르면 전체 도면과 동·호수표를 볼 수 있습니다. 도면의 축척과 시설, 외관은 실제와 다를 수 있습니다.</figcaption></figure>' for n in [7,8])}</div>{note('sub/block.php','공식 단지·동호수배치도')}</section>
<section id="types" class="section-wrap">{heading('05','UNIT PLAN','주택형별<br />평면도','보고 싶은 주택형을 선택해 방과 거실 배치를 확인해 보세요. 이미지를 누르면 확장형·비확장형 평면과 면적표를 함께 볼 수 있습니다.')}<div class="unit-select-row"><label for="plan-unit">공식 평면도 선택</label><select id="plan-unit">{unit_options}</select><button class="secondary" data-open-booking>선택한 주택형 상담하기 ↗</button></div><figure class="official-image"><a id="plan-original" href="../assets/unit-84a.jpg" target="_blank" rel="noopener"><div class="plan-crop unit-crop"><img id="plan-image" src="../assets/unit-84a.jpg" alt="공식 A7BL 84A 확장 기본형 평면도 미리보기" loading="lazy" /></div></a><figcaption id="plan-caption">A7BL · 84A형 확장형 평면도입니다. 이미지를 누르면 면적표와 비확장형 평면도도 볼 수 있습니다. 옵션과 가구, 시공 범위는 계약할 때 확인해 주세요.</figcaption></figure>{note('sub/unit_7bl.php','공식 A7 세대안내')}{note('sub/unit_8bl.php','공식 A8 세대안내')}</section>
<section id="directions" class="section-wrap">{heading('06','VISIT','모델하우스<br />오시는 길','모델하우스는 광주 서구 마륵동 164-11에 있습니다. 방문예약을 신청하시면 모하모아 담당자가 연락드려 방문 시간을 확인해 드립니다.')}<div class="fact-grid"><article class="fact-card"><p class="eyeline">MODEL HOUSE</p><h3>광주 서구 마륵동 164-11</h3><p>운영시간: 오전 10시~오후 5시 30분<br />교통 안내: 상무역 2번 출구에서 약 200m</p><p>방문 전 운영 여부와 주차 안내를 확인해 주세요.</p><button class="primary" data-open-booking>방문예약</button></article><article class="fact-card"><p class="eyeline">CONTACT</p><h3>모하모아 상담 안내</h3><p>주택형이나 방문 일정이 궁금하시면<br />모하모아 담당자에게 문의해 주세요.</p><a class="secondary" href="tel:16005184">모하모아 전화 상담 ↗</a><p class="source-note">이 페이지의 전화 상담은 모하모아 담당자에게 연결됩니다. 시행사·시공사의 공식 상담 창구는 아닙니다.</p></article></div>{note('sub/contact.php','공식 오시는 길')}</section>
{calculator}<section id="faq" class="section-wrap">{heading('08','QUESTIONS','자주 묻는 질문','단지 위치부터 분양가, 방문예약까지 궁금한 내용을 모았습니다. 공식 자료는 2026년 10월 1일에 확인했습니다.')}<div class="faq-list">{faq_html}</div></section>
<section id="sources" class="section-wrap"><p class="eyeline">SOURCES & UPDATE</p><h2>정보의 기준과 출처</h2><ul class="source-list"><li><a href="{official}">호반써밋 첨단3지구 공식 홈페이지</a> · 사업·입지·설계·방문 안내</li><li><a href="{official}images/gonggo7bl_01_v2.pdf">A7BL 모집공고 정정본</a> · 공급금액 PDF 8쪽</li><li><a href="{official}images/gonggo8bl_01_v2.pdf">A8BL 모집공고 정정본</a> · 공급금액 PDF 12쪽</li></ul><p class="source-note">확인일 2026.10.01 · 공고 기준 2026.06.05. 모하모아가 공식 자료를 바탕으로 정리한 안내입니다. 현재 남아 있는 동·호수와 계약 조건은 상담 시 다시 확인해 주세요. 공식 자료가 변경되면 가격표와 안내도 수정합니다.</p></section>'''

variants=[('01','전체 이미지형','호반써밋<br />첨단3지구','rendered-exterior-01.png','호반써밋 첨단3지구 | 주택형·가격·방문 안내'),('02','네이비 분할형','첨단3지구<br />호반써밋','rendered-exterior-02.png','첨단3지구 호반써밋 | 사업개요와 자금계획'),('03','밝은 갤러리형','호반써밋 첨단3지구','rendered-exterior-01.png','호반써밋 첨단3지구 모델하우스 | 평면도·분양가 안내')]
extra_variants = {v['id']:v for v in VARIANTS}
variants += [(v['id'],v['label'],'호반써밋 <br />첨단3지구',v['image'],v['title']) for v in VARIANTS]
section_keys = ['overview','location','premium','arrangement','types','directions','cost','faq','sources']
section_starts = [(content.index('<section id="'+key+'"'),key) for key in section_keys]
section_starts.sort()
sections = {key:content[pos:section_starts[i+1][0] if i+1<len(section_starts) else len(content)] for i,(pos,key) in enumerate(section_starts)}
for ident,label,title,image,title_meta in variants:
 if args.version and ident != args.version: continue
 profile = profiles[ident]
 menu_labels = dict(menu)
 nav = ''.join('<a href="https://mohamoa.com/">모하모아</a>' if key=='mohamoa' else f'<a href="#{key}">{menu_labels[key]}</a>' for key in profile['menu'])
 out=BASE/ident;out.mkdir(exist_ok=True)
 hero_caption = '호반써밋 첨단3지구 단지 투시도'
 description=extra_variants[ident]['description'] if ident in extra_variants else {'01':'호반써밋 첨단3지구 A7·A8블록의 위치와 사업개요, 공식 평면도를 확인하세요. 모집공고 기준 분양가와 자금 계산, 모델하우스 방문예약을 안내합니다.','02':'호반써밋 첨단3지구의 블록별 세대수와 주택형, 층별 분양가를 정리했습니다. 계약금·중도금·잔금과 필요한 자금을 계산해 보세요.','03':'호반써밋 첨단3지구 84A·84B·117A·117B·135형 평면도를 비교해 보세요. 단지배치도, 공고 기준 분양가, 모델하우스 위치도 확인할 수 있습니다.'}[ident]
 variant_content = content
 variant_faq = faq
 if ident not in extra_variants:
  variant_faq = [(profile['question'],profile['answer'],None)] + faq
  new_faq = '<details><summary>'+e(profile['question'])+'</summary><p>'+e(profile['answer'])+'</p><p><a href="#'+profile['focus']+'">관련 자료 보기</a></p></details>'
  direct_answer = '<section id="version-answer" class="focus-section section-wrap"><div class="focus-heading"><h2>'+e(profile['question'])+'</h2><p>'+e(profile['answer'])+'</p></div>'+note('sub/planning.php' if ident=='01' else 'sub/gonggo.php' if ident=='02' else 'sub/unit_7bl.php','공식 근거')+(note('sub/unit_8bl.php','공식 A8 세대안내') if ident=='03' else '')+'</section>'
  variant_content = direct_answer + ''.join(sections[key].replace(faq_html,new_faq+faq_html) if key=='faq' else sections[key] for key in profile['order'])
 if ident in extra_variants:
  v = extra_variants[ident]
  variant_faq = [(v['question'],v['answer'],None)] + faq
  new_faq = '<details><summary>'+e(v['question'])+'</summary><p>'+e(v['answer'])+'</p><p><a href="#focus">비교표와 확인 사항 보기</a></p></details>'
  variant_content = focus_section(v,data) + ''.join(sections[key].replace(faq_html,new_faq+faq_html) if key=='faq' else sections[key] for key in v['order'])
 editorial_path = BASE/'editorial'/f'{ident}.json'
 editorial = json.loads(editorial_path.read_text()) if editorial_path.exists() else None
 if editorial:
  title_meta, description = editorial['title'], editorial['description']
  variant_faq = [(profile['question'],profile['answer'],editorial['refs'][0]['path'])] + [faq[i] for i in editorial['faq_indices']]
  current_faq_html = ''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p>'+ ('<p class="source-note"><a href="'+official+path+'" target="_blank" rel="noopener">公式 근거 확인 ↗</a> · 확인일 2026.10.07</p>' if path else '') + '</details>' for q,a,path in variant_faq).replace('公式','공식')
  refs_html = '<p class="source-note">확인일 2026.10.07 · '+ ' · '.join('<a href="'+official+r['path']+'" target="_blank" rel="noopener">'+e(r['label'])+' ↗</a>' for r in editorial['refs'])+'</p>'
  first_faq_end=current_faq_html.index('</details>')
  first_faq=current_faq_html[:first_faq_end]
  first_faq=re.sub(r'<p class="source-note">.*?</p>',refs_html,first_faq)
  current_faq_html=first_faq+current_faq_html[first_faq_end:]
  if ident in extra_variants:
   v = dict(extra_variants[ident],question=profile['question'],answer=profile['answer'])
   direct_answer = focus_section(v,data).replace('2026.10.01','2026.10.07')
  else:
   direct_answer = '<section id="version-answer" class="focus-section section-wrap"><div class="focus-heading"><h2>'+e(profile['question'])+'</h2><p>'+e(profile['answer'])+'</p></div>'+'</section>'
  heading_end=direct_answer.index('</div>')+len('</div>')
  direct_answer=direct_answer[:heading_end]+refs_html+direct_answer[heading_end:]
  details_html = '<div class="editorial-analysis"><h3>'+e(editorial['analysis_title'])+'</h3>'+ ''.join('<p>'+e(paragraph)+'</p>' for paragraph in editorial['analysis'])+'</div>'
  direct_answer = direct_answer.rsplit('</section>',1)[0]+details_html+'</section>'
  variant_content = ''.join(sections[key].replace(faq_html,current_faq_html) if key=='faq' else sections[key] for key in profile['order'])
  # Only reviewed official facts receive the new check date; facility operators retain their older check date.
  variant_content = variant_content.replace('2026.10.01','2026.10.07').replace('2026년 10월 1일','2026년 10월 7일')
 else:
  direct_answer = ''
 if editorial and 'sections' in editorial:
  rewritten,authored_faqs=render_sections(editorial,data,sections)
  variant_content=''.join(rewritten[key] for key in profile['order'])
  variant_faq=[(f['question'],f['answer'],f['refs'][0] if f['refs'] else None) for f in authored_faqs]
 numbers = iter(range(1,30))
 variant_content = re.sub(r'(<span class="section-number">)\d{2} /',lambda m:m.group(1)+str(next(numbers)).zfill(2)+' /',variant_content)
 schema={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a,_ in variant_faq]}
 page=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title_meta)}</title><meta name="description" content="{e(description)}"><meta name="robots" content="noindex,follow"><link rel="stylesheet" href="../../styles.css"><link rel="stylesheet" href="../concepts.css"><link rel="stylesheet" href="../variants.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script></head><body id="top" class="variant-{ident}"><a class="skip-link" href="#content">본문으로 건너뛰기</a><header class="site-header"><a class="brand" href="#top"><span class="brand-wordmark">HOBAN <b>SUMMIT</b></span><small>호반써밋 첨단3지구 · 모하모아</small></a><nav class="desktop-nav" aria-label="주요 메뉴">{nav}</nav><button class="menu-toggle" aria-controls="mobile-menu" aria-expanded="false" type="button"><span class="sr-only">메뉴 열기</span><i></i><i></i><i></i></button></header><nav id="mobile-menu" class="mobile-menu" aria-label="모바일 주요 메뉴" hidden>{nav}</nav><div class="concept-label"><span>DESIGN {ident} · {label} 시안</span><a href="../">10가지 시안 비교 ↗</a></div>{popup}<main id="content"><section class="hero">{photo(image,hero_caption,'hero-image',True) if image else ''}<div class="hero-content"><p class="eyeline">새로운 일상의 시작</p><h1>{title}</h1><p class="hero-copy">84·117·135㎡, 우리 가족에게 맞는 공간. <br />모델하우스에서 직접 만나보세요.</p><div class="hero-actions"><button class="primary" data-open-booking>방문예약 ↗</button><a class="secondary" href="#types">평면도 살펴보기</a></div></div></section><section id="residence" class="residence-story" aria-labelledby="residence-story-title"><div class="story-intro"><p class="eyeline">HOBAN SUMMIT LIFE</p><h2 id="residence-story-title">우리 가족의 일상에<br />맞는 집을 만나세요.</h2><p>방의 크기부터 거실의 배치까지.<br />평면도를 살펴보고 모델하우스에서<br />우리 가족의 생활에 맞는지 확인해 보세요.</p><a href="#types" class="editorial-link">주택형별 공간 살펴보기 <span>↗</span></a></div><figure class="story-exterior">{photo('rendered-exterior-02.png','공식 투시도를 바탕으로 재구성한 호반써밋 첨단3지구 단지 연출 이미지')}</figure></section><section class="living-story" aria-label="공간 살펴보기"><figure><a href="../assets/official-design-a8.jpg" target="_blank" rel="noopener"><div class="design-preview">{photo('official-design-a8.jpg','공식 홈페이지 A8블록 단지 조감도 미리보기')}</div></a><figcaption>A8블록 단지 조감도 · 누르면 전체 자료가 열립니다.</figcaption></figure><div class="living-copy"><p class="eyeline">YOUR SPACE</p><h2>우리 가족에게<br />어떤 집이 어울릴까요?</h2><p>84A·84B부터 117A·117B·135형까지.<br />방과 거실의 배치를 비교하고,<br />궁금한 점은 담당자에게 물어보세요.</p><button class="editorial-link" data-open-booking>모델하우스 방문예약 <span>↗</span></button></div></section><div class="stats-strip"><div class="stat"><strong>805세대</strong><span>A7·A8 전체 공급 규모</span></div><div class="stat"><strong>84 · 117 · 135㎡</strong><span>주택형 (전용면적 기준 약식 표기)</span></div><div class="stat"><strong>A7 · A8</strong><span>광주 월출동 / 장성 진원면</span></div><div class="stat"><strong>1,000만원</strong><span>공고 기준 1차 계약금</span></div></div>{variant_content}</main><footer class="site-footer"><p>모하모아 운영 · 사업자등록번호 597-17-02567 · 개인정보 문의 1555-1698<br />본 페이지는 모하모아의 정보·상담 안내이며 시행사·시공사 공식 홈페이지가 아닙니다.</p><p><a href="https://mohamoa.com/privacy">모하모아 개인정보 안내</a> · <a href="{official}">단지 공식 홈페이지</a></p></footer><nav class="contact-bar" aria-label="방문 및 전화 예약"><button class="contact-action visit-action" data-open-booking>방문예약</button><a class="contact-action phone-action" href="tel:16005184">전화예약</a></nav><button class="scroll-top" type="button" aria-label="위로 스크롤">↑</button><script src="../reservation-config.js"></script><script>window.RESERVATION_CONFIG.sourceVariant="{ident}";</script><script src="../consent-policy.js"></script><script src="../../script.js"></script><script src="../budget-math.js"></script><script src="../data.js"></script><script src="../concepts.js"></script></body></html>'''
 if ident in extra_variants:
  v = extra_variants[ident]
  hero_start = page.index('<section class="hero">')
  story_end = page.index('<div class="stats-strip">', hero_start)
  hero = '<section class="hero hero-new">'+photo(image,hero_caption,'hero-image',True)
  if ident=='08':
   hero += '<figure class="hero-detail"><div class="design-preview">'+photo('official-design-a8.jpg','A8블록 공식 조감도 미리보기')+'</div></figure>'
  hero += '<div class="hero-content"><p class="eyeline">'+e(v['kicker'])+'</p><h1>'+title+'</h1><p class="hero-copy">'+v['copy'].replace('<br />','<br /> ')+'</p><div class="hero-actions"><button class="primary" data-open-booking>방문예약 ↗</button><a class="secondary" href="#'+v['link']+'">'+e(v['action'])+'</a></div></div><div class="hero-aside"><strong>'+e(v['metric'])+'</strong><span>'+e(v['detail'])+'</span></div></section>'
  page = page[:hero_start]+hero+page[story_end:]
 if editorial and 'sections' in editorial:
  page=re.sub(r'(<section class="hero[^>]*>.*?<div class="hero-content"><p class="eyeline">).*?(</p>)',lambda m:m[1]+e(editorial['hero_kicker'])+m[2],page,count=1,flags=re.S)
  page=re.sub(r'(<p class="hero-copy">).*?(</p>)',lambda m:m[1]+e(editorial['hero_copy'])+m[2],page,count=1,flags=re.S)
  if ident not in extra_variants:
   page=re.sub(r'(<h2 id="residence-story-title">).*?(</h2>)',lambda m:m[1]+e(editorial['story_title'])+m[2],page,count=1,flags=re.S)
   page=re.sub(r'(<h2 id="residence-story-title">.*?</h2><p>).*?(</p>)',lambda m:m[1]+e(editorial['story_text'])+m[2],page,count=1,flags=re.S)
   page=re.sub(r'(<div class="living-copy"><p class="eyeline">.*?</p><h2>).*?(</h2>)',lambda m:m[1]+e(editorial['living_title'])+m[2],page,count=1,flags=re.S)
   page=re.sub(r'(<div class="living-copy">.*?</h2><p>).*?(</p>)',lambda m:m[1]+e(editorial['living_text'])+m[2],page,count=1,flags=re.S)
 if editorial:
  build_branding(ident,out/'branding')
  page=page.replace('</head>','<link rel="icon" type="image/svg+xml" href="branding/favicon.svg"><link rel="icon" type="image/png" sizes="96x96" href="branding/favicon-96.png"><link rel="icon" type="image/x-icon" href="branding/favicon.ico"><link rel="apple-touch-icon" sizes="180x180" href="branding/apple-touch-icon.png"></head>',1)
  hero_end = page.index('</section>',page.index('<section class="hero')) + len('</section>')
  page = page[:hero_end]+direct_answer+page[hero_end:]
  page = page.replace('<meta name="robots"', '<meta property="og:title" content="'+e(title_meta)+'"><meta property="og:description" content="'+e(description)+'"><meta property="og:type" content="website"><meta property="og:locale" content="ko_KR"><meta name="robots"',1)
 (out/'index.html').write_text(page)
 keyword_rows = ''.join('| '+k['keyword']+' | #'+k['section']+' | '+k['condition']+' | '+k['status']+' |\n' for k in version_plan['keywords'])
 menu_text = ' → '.join('모하모아' if key=='mohamoa' else menu_labels[key] for key in profile['menu'])
 (out/'PROJECT.md').write_text('# '+ident+' · '+label+'\n\n상태: 실제 상담 접수 연결 / 도메인공개 전 noindex.\n\n'+'## 버전별 작성값\n\n- 대표 질문: '+profile['question']+'\n- 직접 답: '+profile['answer']+'\n- title: '+title_meta+'\n- H1: '+re.sub('<[^>]+>',' ',title).strip()+'\n- 메타 설명: '+description+'\n- 메뉴 순서: '+menu_text+'\n- 본문 순서: '+' → '.join(profile['order'])+'\n- 강조 영역: #'+profile['focus']+'\n- 직접 답변 위치: '+('#focus' if ident in extra_variants else '#version-answer')+' 및 FAQ\n- 자료 확인일: 2026-10-01\n- 공개 도메인·canonical: 확인 필요\n- 검색 수요·검색량: 후보 / 확인 필요\n- 독립 사이트의 고유 가치 검수: 미완료\n- 전화 연결: tel:16005184\n- 서버 ctx: 호반써밋첨단3지구\n- sourceVariant: '+ident+'\n\n## 검색어 후보와 실제 답변 위치\n\n후보는 공식 사실에서 추출했습니다. 실제 연관검색어·검색량·순위는 확인 필요입니다. 강조 영역에 해당하는 후보를 우선 검토하며 아래 목록을 HTML에 나열하지 않습니다.\n\n| 후보 검색어 | 본문 위치 | 답변·조건 | 확인 상태 |\n|---|---|---|---|\n'+keyword_rows+'\n## 공통 제작·공개 절차\n\n../../TEN_VERSION_WORKFLOW.md, ../../LIVE_RESERVATION_GUIDE.md, ../../SEARCH_INDEXING_HANDOFF.md를 읽습니다. SEO는 제목·본문·URL, AEO는 직접 답·FAQ, GEO는 독립적으로 이해되는 사실·비교·출처·기준일에 적용합니다. 색인·검색 노출·AI 인용은 미확인 상태입니다.\n\n같은 사실과 상담 경로를 공유하므로 디자인·문장·순서 차이만으로 독립 색인 적합성을 주장하지 않습니다. 버전별 독자 가치와 중복 처리 검토 후 도메인별 공개 설정을 진행합니다.\n')
 if editorial:
  brief_path = out/'PROJECT.md'
  brief = brief_path.read_text()
  brief = brief.replace('상태: 실제 상담 접수 연결 / 도메인공개 전 noindex.','상태: 기존 사이트 수정 초안 / 실제 상담 접수 연결 / 로컬 noindex 유지.')
  brief = brief[:brief.index('## 검색어 후보와 실제 답변 위치')]
  brief = brief.replace('자료 확인일: 2026-10-01','자료 확인일: 2026-10-07').replace('공개 도메인·canonical: 확인 필요','예정 공개 URL: '+editorial['url']+' / 로컬 canonical 해당 없음').replace('독립 사이트의 고유 가치 검수: 미완료','고유 비교 내용: '+editorial['analysis_title'])
  brief += '\n## 분양 페이지별 입력 명세\n\n최우선 기준: ../../SALE_PAGE_PRIORITY.md. 한국어 / 모하모아 운영 / 기존 공개 사이트의 수정 초안. 현재 빌드의 noindex를 유지하며 배포·색인 요청은 실행하지 않는다.\n\n'
  brief += '핵심 독자: '+editorial['reader']+'\n\n## 사실과 근거\n\n| 사실·범위 | 공식 원문 | 자료 발행일 | 확인일 | 조건 |\n|---|---|---|---|---|\n'
  for ref in editorial['refs']:
   brief += '| '+ref['label']+' | '+official+ref['path']+' | '+ref.get('published','확인 필요')+' | 2026-10-07 | '+ref['condition']+' |\n'
  brief += '\n미확인: 현재 잔여 동·호수, 최신 판매 조건, 예정 시설 개통·개교, 방문 가능 시간. 공식 자료나 계약 조건이 바뀌면 다시 확인한다.\n\n## 검색어·답변 연결\n\n조사 원문과 설정은 ../SEARCH_RESEARCH_20261007.md를 따른다. 검색량·순위를 추정하지 않는다.\n\n| 검색 표현 | 조사 또는 후보 | 의도 | 실제 답변 위치 | 적용 조건 |\n|---|---|---|---|---|\n'
  for term in editorial['terms']:
   brief += '| '+term['text']+' | '+term['status']+' | '+editorial['intent']+' | #'+term['section']+' | '+term['condition']+' |\n'
  brief += '\n## SEO 작성값과 링크\n\n목표: Google·네이버·Bing의 정보 검색. title·H1·메타 설명은 위 작성값과 동일하며 og:title은 title에 맞춘다. 내부 링크는 이 페이지의 평면·비용·위치·예약 영역으로 연결한다. 같은 의도는 같은 본문 영역에 묶고 중복 페이지를 추가하지 않는다. 현재 경쟁 순위·검색량은 확인 필요. 로컬 canonical은 해당 없음; 운영 URL과 기존 canonical은 배포 단계에서 확인·보존한다.\n\n## 질문별 직접 답변과 근거\n\n| 질문 | 본문에 표시한 답 | 근거 | 위치 |\n|---|---|---|---|\n'
  for q,a,path in variant_faq:
   brief += '| '+q+' | '+a+' | '+(official+path+' / 확인일 2026-10-07' if path else '기존 예약·계산 기능 / 서버 전송 범위 확인')+' | #faq |\n'
  brief += '\n## AEO·GEO 구현\n\n대표 질문과 직접 답은 첫 이미지 바로 다음 정보 영역에 있다. FAQ는 이 버전의 질문을 골라 화면·JSON-LD에 같은 답을 제공한다. 공식 자료에 근거한 사실과 자체 비교·계산을 구분한다. 검색어·FAQ 개수는 고정하지 않는다.\n\n## 공개·기능 검증\n\n로컬 HTML·독립 배포 폴더의 링크와 이미지, FAQ 일치, 가격 수정 금지, 메뉴와 ctx를 scripts/verify_concepts.py --version '+ident+'로 검증한다. PC·모바일 실행 결과는 ../SALE_REVISION_REPORT_20261007.md에 기록한다. 예약·동의 버전·보관 정책·알림 서버는 변경하지 않는다. 구현 / 수집 요청 / 색인 / 검색 노출 / AI 인용은 각각 별도 상태로 기록한다.\n'
  if 'sections' in editorial:
   brief+='\n## 全本文 수정 명세 — 2026-10-07 보완\n\n첫 답변뿐 아니라 일곱 정보 영역과 첫 화면·FAQ를 새로 작성했다. 공통 가격 데이터·원본 도면·예약 컨트롤은 보존한다.\n\n| 영역 | 제목 | 독자 질문 | 초기 HTML에 보이는 직접 답 | 공식 근거·확인일 |\n|---|---|---|---|---|\n'
   for key,m in editorial['sections'].items():
    brief+='| #'+key+' | '+m['title']+' | '+m['question']+' | '+m['answer']+' | '+ ' / '.join(official+p for p,_ in SECTION_REFS[key])+' / 2026-10-07 |\n'
   brief=brief.replace('全本文','전체 본문')
  brief_path.write_text(brief)
(BASE/'data.js').write_text('window.HOBAN_DATA = '+json.dumps(data,ensure_ascii=False)+';\n')
chooser_cards = ''.join('<a href="'+ident+'/"><span>'+ident+'</span><h2>'+label+'</h2><p>'+(extra_variants[ident]['kicker'] if ident in extra_variants else {'01':'포레스트 그린 · 전체 단지 이미지','02':'네이비·샌드 · 설명과 이미지 분할','03':'아이보리·브론즈 · 밝은 갤러리'}[ident])+'</p><b>시안 보기 ↗</b></a>' for ident,label,*_ in variants)
(BASE/'index.html').write_text('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>호반써밋 첨단3지구 · 디자인 시안 10종</title><link rel="stylesheet" href="review.css"></head><body><header><p>MOHAMOA / DESIGN COLLECTION</p><h1>호반써밋 첨단3지구<br />디자인 시안 10종</h1><p>이미지와 정보 구성, 우리 가족의 집을 고르는 서로 다른 시작.</p></header><main class="review-grid">'+chooser_cards+'</main><footer>디자인 비교용 noindex 시안입니다. 01~10 모두 실제 상담 접수에 연결됩니다.</footer></body></html>')
(BASE/'_headers').write_text('/*\n  X-Robots-Tag: noindex\n  X-Content-Type-Options: nosniff\n')
print('Built concept '+(args.version or '01–10'))
for ident, *_ in variants:
 if args.version and ident != args.version: continue
 out = ROOT / 'dist' / 'hoban' / ident
 out.mkdir(parents=True, exist_ok=True)
 page = (BASE / ident / 'index.html').read_text().replace('../../styles.css','styles.css').replace('../../script.js','script.js').replace('../assets/','assets/')
 for name in ['concepts.css','variants.css','reservation-config.js','consent-policy.js','budget-math.js','data.js','concepts.js']:
  page = page.replace('../'+name,name)
  shutil.copy2(BASE/name,out/name)
 for name in ['styles.css','script.js']: shutil.copy2(ROOT/name,out/name)
 shutil.copytree(BASE/'assets',out/'assets',dirs_exist_ok=True,ignore=shutil.ignore_patterns('*concept*','GENERATED_IMAGE_PROMPTS.md'))
 for unused in list((out/'assets').glob('*concept*')) + [out/'assets'/'GENERATED_IMAGE_PROMPTS.md']:
  if unused.is_file(): unused.unlink()
 if (BASE/ident/'branding').exists(): shutil.copytree(BASE/ident/'branding',out/'branding',dirs_exist_ok=True)
 shutil.copy2(BASE/'_headers',out/'_headers')
 (out/'index.html').write_text(page)
 (out/'robots.txt').write_text('User-agent: *\nAllow: /\n# Draft: noindex in HTML and HTTP headers.\n')
 (out/'404.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="robots" content="noindex"><title>페이지 없음</title><h1>페이지를 찾을 수 없습니다.</h1><a href="/">홈으로</a></html>')
shutil.copy2(BASE/'index.html',ROOT/'dist'/'hoban'/'index.html')
shutil.copy2(BASE/'review.css',ROOT/'dist'/'hoban'/'review.css')
print('Standalone draft bundle: '+(args.version or '01–10'))
