# -*- coding: utf-8 -*-
"""Editorial design briefs. These are review alternatives, not indexable sites."""
import html

VARIANTS = [
 dict(id='04', label='파노라마 단지형', theme='clay', image='rendered-exterior-02.png',
      kicker='두 블록, 서로 다른 주택형', copy='A7과 A8을 나란히 살펴보세요.<br />우리 가족에게 맞는 공간을 찾는 시작입니다.',
      title='호반써밋 첨단3지구 | A7·A8 블록 비교', description='호반써밋 첨단3지구 A7·A8의 위치, 세대수, 주택형과 입주 예정 시기를 비교합니다. 공식 단지배치도와 평면도도 함께 확인하세요.',
      focus='두 블록을 한눈에 비교하세요', question='A7과 A8은 무엇이 다른가요?',
      answer='A7은 84A·84B형 356세대, A8은 117A·117B·135형 449세대입니다. 사업지와 입주 예정 시기도 다릅니다.', link='overview', action='블록별 사업개요 보기', metric='A7 / A8', detail='두 블록 비교', order=['overview','arrangement','types','premium','location','directions','cost','faq','sources']),
 dict(id='05', label='미드나이트 자금형', theme='midnight', image='rendered-exterior-01.png',
      kicker='분양가와 자금 계획을 함께', copy='마음에 드는 집을 찾았다면,<br />계약부터 입주까지 필요한 금액도 살펴보세요.',
      title='호반써밋 첨단3지구 | 분양가·납부계획', description='모집공고의 주택형별 분양가와 계약금 5%·중도금 60%·잔금 35%를 정리했습니다. 공식 가격을 선택해 필요한 자금을 계산하세요.',
      focus='주택형별 가격부터 확인하세요', question='주택형별 분양가는 얼마인가요?',
      answer='분양가는 주택형과 층에 따라 다릅니다. 아래 표는 2026년 6월 5일 모집공고의 공급금액이며 발코니 확장과 유상옵션 비용은 별도입니다.', link='cost', action='필요 자금 계산하기', metric='5 / 60 / 35', detail='공고 기준 납부 비율 (%)', order=['cost','overview','types','premium','arrangement','location','directions','faq','sources']),
 dict(id='06', label='화이트 평면형', theme='white', image='rendered-exterior-02.png',
      kicker='다섯 가지 평면, 우리 집의 기준', copy='84A부터 135형까지.<br />면적과 방 배치를 비교해 우리 가족의 집을 골라보세요.',
      title='호반써밋 첨단3지구 | 주택형·면적 비교', description='84A·84B·117A·117B·135형의 전용면적과 공급면적을 비교합니다. 공식 평면도에서 확장형·비확장형과 방·거실 배치를 살펴보세요.',
      focus='같은 숫자라도 면적은 다릅니다', question='84·117·135는 정확한 면적인가요?',
      answer='주택형 이름의 숫자는 전용면적을 줄여 쓴 표기입니다. 정확한 전용면적과 공용부분을 포함한 공급면적은 아래 표에서 확인할 수 있습니다.', link='types', action='평면도 선택하기', metric='5 TYPES', detail='공식 주택형', order=['types','overview','arrangement','premium','cost','location','directions','faq','sources']),
 dict(id='07', label='세이지 생활권형', theme='sage', image='rendered-exterior-01.png',
      kicker='집과 함께 살펴볼 생활권', copy='장보기, 병원 방문, 아이의 학교까지.<br />첨단 생활권의 시설과 계획을 구분해 살펴보세요.',
      title='호반써밋 첨단3지구 | 교육·교통·생활시설', description='첨단 생활권의 롯데마트·첨단종합병원·국립광주과학관과 단지 주변 학교·교통 계획을 구분해 정리했습니다. 공식 입지 지도를 함께 확인하세요.',
      focus='지금 있는 시설과 앞으로의 계획', question='입지 지도에 있는 시설을 모두 바로 이용할 수 있나요?',
      answer='아닙니다. 생활권의 기존 시설과 학교·도시철도·연결도로 계획이 함께 표시돼 있습니다. 예정 연도와 실제 이용 가능 시기는 구분해야 합니다.', link='location', action='입지 지도 크게 보기', metric='LIFE / PLAN', detail='생활시설과 예정 시설 구분', order=['location','overview','premium','arrangement','types','directions','cost','faq','sources']),
 dict(id='08', label='샌드 커뮤니티형', theme='sand', image='rendered-exterior-02.png',
      kicker='집 안의 공간, 단지 안의 일상', copy='평면도만큼 중요한 단지 안의 시설.<br />A8블록의 커뮤니티 계획을 함께 살펴보세요.',
      title='호반써밋 첨단3지구 | A8 커뮤니티·단지 안내', description='A8 모집공고의 피트니스·골프연습장·작은도서관·에듀센터·게스트하우스 계획과 확인할 이용 조건을 정리했습니다. 블록별 단지배치도도 제공합니다.',
      focus='A8블록에 계획된 커뮤니티 시설', question='A8블록에는 어떤 커뮤니티 시설이 계획돼 있나요?',
      answer='A8 모집공고에는 피트니스, 골프연습장, 작은도서관, 에듀센터, 게스트하우스 등이 포함돼 있습니다. 운영 방식과 이용료는 확정된 안내를 확인해야 합니다.', link='premium', action='시설 계획 살펴보기', metric='A8 COMMUNITY', detail='A8 모집공고 기준', order=['premium','arrangement','overview','types','location','directions','cost','faq','sources']),
 dict(id='09', label='라이트 방문형', theme='light', image='rendered-exterior-01.png',
      kicker='모델하우스에서 직접 확인하세요', copy='보고 싶은 주택형을 먼저 고르고,<br />모델하우스에서 공간을 직접 만나보세요.',
      title='호반써밋 첨단3지구 | 모델하우스 방문 준비', description='광주 서구 마륵동 모델하우스 주소와 방문 준비 사항을 안내합니다. 관심 주택형과 질문을 정리하고 방문 희망 날짜·시간을 신청하세요.',
      focus='방문 전에 확인하면 좋은 것들', question='모델하우스 방문은 어떻게 준비하나요?',
      answer='관심 주택형을 고른 뒤 방문 희망 날짜와 시간을 신청해 주세요. 모하모아 담당자의 연락을 받아 시간을 확인한 후 모델하우스로 방문하시면 됩니다.', link='directions', action='모델하우스 위치 확인', metric='MODEL HOUSE', detail='광주 서구 마륵동 164-11', order=['directions','types','overview','premium','arrangement','location','cost','faq','sources']),
 dict(id='10', label='차콜 선택형', theme='charcoal', image='rendered-exterior-02.png',
      kicker='우리 가족의 기준으로 고르는 집', copy='면적, 비용, 생활권.<br />중요한 것부터 확인하고 선택해 보세요.',
      title='호반써밋 첨단3지구 | 내 집 선택 가이드', description='주택형, 자금 계획, 출퇴근과 학교 계획, 방문 준비까지 집을 고를 때 확인할 항목을 정리했습니다. 필요한 자료로 바로 이동할 수 있습니다.',
      focus='무엇을 먼저 확인하고 싶으세요?', question='집을 고를 때 어떤 자료부터 보면 좋을까요?',
      answer='공간이 중요하면 평면도, 예산이 중요하면 분양가와 납부계획, 생활권이 중요하면 입지 지도를 먼저 확인해 보세요. 방문 전 궁금한 점을 정리하면 상담에 도움이 됩니다.', link='types', action='평면도부터 살펴보기', metric='YOUR CHOICE', detail='공간 · 비용 · 생활권', order=['overview','types','cost','location','premium','arrangement','directions','faq','sources']),
]

def focus_section(v, data):
    esc = html.escape
    cells = lambda values: ''.join('<td>'+str(value)+'</td>' for value in values)
    def table(headers, rows, caption):
        return '<div class="table-scroll"><table class="focus-table"><caption>'+caption+'</caption><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+cells(r)+'</tr>' for r in rows)+'</tbody></table></div>'
    source = 'https://hobansummit-kjcd.co.kr/'
    ident = v['id']
    if ident == '04':
        body = table(['확인할 내용','A7블록','A8블록'],[
          ('사업지','광주 북구 월출동','전남 장성군 진원면'),('전체 세대수','356세대','449세대'),
          ('주택형','84A · 84B','117A · 117B · 135'),('건물 규모','지하 1층~지상 20층 · 5개동','지하 1층~지상 18~20층 · 6개동'),
          ('입주 예정','2028년 9월','2028년 10월')], 'A7·A8 사업지·주택형·공급 규모 비교')
        body += '<p class="focus-note">세대수는 전체 공급 규모입니다. 현재 남아 있는 세대수와는 다르며, 정확한 입주일은 추후 안내됩니다.</p>'
        refs = [('sub/planning.php','사업개요'),('images/gonggo7bl_01_v2.pdf','A7 모집공고'),('images/gonggo8bl_01_v2.pdf#page=11','A8 모집공고')]
    elif ident == '05':
        rows = []
        for u in data['units']:
            low, high = u['prices'][0]['won'], u['prices'][-1]['won']
            rows.append((u['block']+' · '+u['id']+'형',f'{low//10000:,}~{high//10000:,}만원',f'{low*5//10000000:,}만원' if low*5 % 10000000 == 0 else f'{low*.05/10000:,.0f}만원'))
        body = table(['주택형','공고 기준 분양가 범위','최저가 기준 전체 계약금 5%'], rows, '주택형별 가격 범위와 최저가 기준 계약금')
        body += '<p class="focus-note">전체 계약금은 분양가의 5%입니다. 1차 계약금 1,000만원을 납부한 뒤 나머지는 공고상 계약 후 30일 이내에 납부합니다. 표의 계약금은 최저가로 계산한 비교값이며, 선택한 층의 금액은 계산기에서 확인해 주세요.</p>'
        refs = [('images/gonggo7bl_01_v2.pdf#page=8','A7 공급금액'),('images/gonggo8bl_01_v2.pdf#page=12','A8 공급금액')]
    elif ident == '06':
        body = table(['주택형','전용면적','공급면적'], [(u['block']+' · '+u['id']+'형', f'{u["exclusive_area"]:.4f}㎡', f'{u["supply_area"]:.4f}㎡') for u in data['units']], '모집공고 기준 전용면적·공급면적 비교')
        body += '<div class="focus-pair"><div><h3>전용면적</h3><p>세대 안에서 주거용으로 사용하는 면적입니다. 주택형을 비교할 때 같은 기준으로 살펴보세요.</p></div><div><h3>공급면적</h3><p>전용면적에 계단·복도 등 주거 공용면적을 더한 값입니다. 발코니 확장 면적이나 계약면적과는 구분합니다.</p></div></div>'
        refs = [('images/gonggo7bl_01_v2.pdf','A7 모집공고'),('images/gonggo8bl_01_v2.pdf#page=11','A8 면적표')]
    elif ident == '07':
        body = table(['구분','시설·계획','확인할 내용'],[
          ('생활시설','롯데마트 첨단점 · 첨단종합병원 · 국립광주과학관','이용 경로 · 운영시간 · 휴무일'),
          ('교육 계획','단지 주변 초·중·고 · 유치원 부지','개교 시기 · 실제 배정학교'),
          ('교통 계획','도시철도 2호선 2단계 · 상무지구~첨단산단 도로 · 진입도로','최신 일정 · 단지 출입구 기준 실제 경로'),
          ('산업 생활권','광주첨단과학국가산업단지 · 국가AI데이터센터 등 지도상 위치','본인 직장까지 출퇴근 경로')], '생활시설과 예정 시설의 확인 기준')
        body += '<p class="focus-note">첨단역·지스트역·신용역은 지도에 쓰인 가칭입니다. 지도만으로 도보권이나 트리플 역세권, 학교 배정을 판단하지 않습니다.</p>'
        refs = [('sub/location.php','입지 지도·계획의 기준 시점')]
    elif ident == '08':
        body = '<div class="community-list">'+''.join('<article><span>'+str(i).zfill(2)+'</span><div><h3>'+name+'</h3><p>'+copy+'</p></div></article>' for i,(name,copy) in enumerate([
          ('피트니스 · 골프연습장','운동시설의 규모와 장비, 이용 시간과 비용을 확인해 보세요.'),
          ('작은도서관 · 에듀센터','운영 방식과 프로그램, 이용 대상은 추후 안내를 확인해 주세요.'),
          ('게스트하우스','예약 방법과 이용 가능 인원, 별도 요금 여부를 확인해 주세요.')],1))+'</div>'
        body += '<p class="focus-note">A8 모집공고의 시설 계획을 기준으로 정리했습니다. A7에도 같은 시설이 설치된다는 뜻은 아니며 운영 조건을 확정적으로 안내하지 않습니다.</p>'
        refs = [('images/gonggo8bl_01_v2.pdf#page=53','A8 부대복리시설 계획')]
    elif ident == '09':
        body = '<ol class="visit-steps"><li><strong>관심 주택형 고르기</strong><p>평면도를 보면서 방·거실 배치, 확장과 옵션에 대해 궁금한 점을 적어보세요.</p></li><li><strong>방문 날짜·시간 신청하기</strong><p>방문예약에서 이름과 연락처, 방문을 원하는 날짜·시간을 입력해 주세요.</p></li><li><strong>담당자 연락 후 방문하기</strong><p>방문 시간과 모델하우스 운영 여부, 주차 안내를 확인한 뒤 방문해 주세요.</p></li></ol><div class="visit-address"><span>모델하우스</span><strong>광주 서구 마륵동 164-11</strong><p>사업지가 아니라 모델하우스 주소로 이동해 주세요. 공식 안내 기준 운영시간은 오전 10시~오후 5시 30분입니다.</p><button class="primary" data-open-booking>방문 희망 일시 신청</button></div>'
        refs = [('sub/contact.php','모델하우스 오시는 길')]
    else:
        body = '<div class="decision-grid">'+''.join('<a href="#'+key+'"><span>'+str(i).zfill(2)+'</span><h3>'+title+'</h3><p>'+copy+'</p><b>'+label+' ↗</b></a>' for i,(key,title,copy,label) in enumerate([
          ('types','우리 가족에게 맞는 공간','정확한 면적과 방·거실 배치를 비교해 보세요.','평면도 비교'),
          ('cost','계약부터 입주까지의 비용','확장·옵션·기타 비용을 더하고 필요한 현금을 계산해 보세요.','자금 계산'),
          ('location','매일 오가는 생활권','직장과 생활시설의 위치, 학교·교통 계획을 구분해 보세요.','입지 확인'),
          ('directions','직접 보고 싶은 주택형','자료만으로 알기 어려운 점을 정리하고 방문 시간을 신청해 주세요.','방문 준비')],1))+'</div>'
        refs = [('sub/planning.php','사업개요'),('sub/unit_7bl.php','A7 세대안내'),('sub/unit_8bl.php','A8 세대안내')]
    return '<section id="focus" class="focus-section section-wrap"><div class="focus-heading"><p class="eyeline">'+esc(v['kicker'])+'</p><h2>'+esc(v['focus'])+'</h2><h3>'+esc(v['question'])+'</h3><p>'+esc(v['answer'])+'</p></div>'+body+'<p class="source-note">확인일 2026.10.01 · '+ ' · '.join('<a href="'+source+path+'" target="_blank" rel="noopener">'+label+' ↗</a>' for path,label in refs)+'</p></section>'
