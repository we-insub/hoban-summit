"""Static, crawlable price summary for the 분양계산기 page. Facts come from source-data.json and the cost presets.

번호마다 독자가 달라 표의 구성도 다르다(VIEWS). 숫자·날짜·출처는 모두 공식 자료에서 읽은 값이고,
차액·남는 금액처럼 계산한 열은 표 아래 설명에 계산값임을 적는다.
"""
import json,re
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
VIEWS={'01':'standard','02':'payment','03':'compare','04':'blocks','05':'firsthome','06':'floors','07':'family','08':'steps','09':'cards','10':'checklist'}
def man(v): return f'{round(v):,}'
def load():
 src=json.loads((ROOT/'concepts/source-data.json').read_text())
 raw=(ROOT/'concepts/vendor/mohamoa-cost/cost-presets.ts').read_text()
 preset=json.loads(re.search(r'=(\{"cheomdan3[^\n]*\});?\s*$',raw.split('\n')[1].split('costPresets:Record<string,CostPreset>',1)[1]).group(1))['cheomdan3-a7-hoban-summit']
 balcony={t['label']:t['balconyAmount'] for b in preset['blocks'] for t in b['types']}
 return src,preset,balcony
def units(src,preset,balcony):
 c,i=preset['contractPercent'],preset['interimPercent'];out=[]
 for u in src['units']:
  prices={p['floor']:p['won']/10000 for p in u['prices']}
  base=prices['기준층'];deposit=round(base*c/100);interim=round(base*i/100)
  out.append(dict(id=u['id'],block=u['block'],area=u['exclusive_area'],supply=u['supply_area'],prices=prices,low=prices['1층'],base=base,
   deposit=deposit,interim=interim,balance=base-deposit-interim,balcony=balcony[u['id']],over85=u['exclusive_area']>85))
 return out
def table(caption,head,rows,cls=''):
 th=''.join(f'<th scope="col">{h}</th>' for h in head)
 return f'<div class="calc-summary-scroll"><table class="{cls}"><caption>{caption}</caption><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'
def row(first,cells,strong=None):
 tds=''.join(f'<td>{"<strong>"+c+"</strong>" if i==strong else c}</td>' for i,c in enumerate(cells))
 return f'<tr><th scope="row">{first}</th>{tds}</tr>'
def label(u): return f'{escape(u["id"])}형 ({u["block"]})'
def area(u): return f'{u["area"]:.2f}㎡<br><span>{"전용 85㎡ 초과" if u["over85"] else "전용 85㎡ 이하"}</span>'
def summary_html(ident,copy):
 src,preset,balcony=load();us=units(src,preset,balcony)
 c,i=preset['contractPercent'],preset['interimPercent'];view=VIEWS[ident]
 notice=src['notice_date'].replace('-','.');reviewed=preset['reviewedAt']
 cap=f'{notice} 모집공고 기준 · 단위: 만 원'
 blocks=preset['blocks']
 if view=='standard':
  body=''.join(row(label(u),[area(u),man(u['low']),man(u['base']),f'{man(u["deposit"])} · {man(u["interim"])} · {man(u["balance"])}',man(u['balcony'])],strong=2) for u in us)
  html=table(cap,['주택형(블록)','전용면적','1층 분양가','기준층 분양가','기준층 계약금·중도금·잔금','발코니 확장비(선택)'],body)
 elif view=='payment':
  body=''.join(row(label(u),[man(u['base']),man(u['deposit']),man(u['interim']),man(u['balance'])]) for u in us)
  html=table(cap,['주택형(블록)','기준층 분양가',f'계약금 {c}%',f'중도금 {i}%',f'잔금 {100-c-i}%'],body)
 elif view=='compare':
  small=min(us,key=lambda u:u['area'])
  ordered=sorted(us,key=lambda u:u['area'])
  body=''.join(row(label(u),[f'{u["area"]:.2f}㎡',man(u['base']),'기준' if u is small else '+'+man(u['base']-small['base']),man(u['balcony'])],strong=1) for u in ordered)
  html=table(cap+' · 크기순',['주택형(블록)','전용면적','기준층 분양가',f'{small["id"]}형과의 차액','발코니 확장비(선택)'],body)
 elif view=='blocks':
  parts=[]
  for b in blocks:
   mine=[u for u in us if u['block']==b['label']]
   body=''.join(row(f'{escape(u["id"])}형',[f'{u["area"]:.2f}㎡',man(u['low']),man(u['base']),man(u['balcony'])],strong=2) for u in mine)
   parts.append(f'<h4>{b["label"]} · {len(mine)}개 주택형</h4>'+table(f'{b["label"]} 모집공고 · 단위: 만 원',['주택형','전용면적','1층 분양가','기준층 분양가','발코니 확장비(선택)'],body))
  html=''.join(parts)
 elif view=='firsthome':
  mine=[u for u in us if u['area']<85]
  body=''.join(row(label(u),[f'{u["area"]:.2f}㎡',man(u['base']),man(u['deposit']),man(u['base']-u['deposit'])],strong=2) for u in mine)
  html=table(cap,['주택형(블록)','전용면적','기준층 분양가',f'계약금 {c}%','계약금 뒤 남는 금액'],body)
 elif view=='floors':
  floors=['1층','2층','3층','4층','기준층']
  body=''.join(row(label(u),[f'{u["area"]:.2f}㎡']+[man(u['prices'][f]) for f in floors]+['+'+man(u['base']-u['low'])]) for u in us)
  html=table(cap,['주택형(블록)','전용면적']+floors+['층 차액'],body)
 elif view=='family':
  ordered=sorted(us,key=lambda u:u['area'])
  body=''.join(row(label(u),[f'{u["area"]:.2f}㎡',f'{u["supply"]:.2f}㎡',man(u['base']),man(u['balcony']),'대상 여부 확인' if u['over85'] else '해당 없음'],strong=2) for u in ordered)
  html=table(cap+' · 면적 단위 ㎡',['주택형(블록)','전용면적','공급면적','기준층 분양가','발코니 확장비(선택)','농어촌특별세'],body)
 elif view=='steps':
  body=''.join(row(label(u),[man(u['base']),'1,000',man(u['deposit']-1000),man(u['interim']),man(u['balance'])]) for u in us)
  html=table(cap,['주택형(블록)','기준층 분양가','1차 계약금','2차 계약금(나머지)',f'중도금 {i}%',f'잔금 {100-c-i}%'],body)
 elif view=='cards':
  asks={'84A':'이 주택형의 층별 잔여 세대와 확장 선택 여부를 물어보세요.','84B':'84A와 구조가 어떻게 다른지 모형이나 도면으로 확인하세요.','117A':'발코니 확장 범위와 옵션 비용을 항목별로 물어보세요.','117B':'117A와 비교해 달라지는 구조와 금액을 확인하세요.','135':'확장비와 옵션, 납부 일정을 한꺼번에 확인하세요.'}
  items=''.join(f'<li><h4>{label(u)}</h4><dl><div><dt>기준층 분양가</dt><dd>{man(u["base"])}</dd></div><div><dt>발코니 확장비(선택)</dt><dd>{man(u["balcony"])}</dd></div></dl><p>{asks[u["id"]]}</p></li>' for u in us)
  html=f'<p class="calc-summary-caption">{cap}</p><ul class="calc-summary-cards">{items}</ul>'
 else:
  lo=min(u['base'] for u in us);hi=max(u['base'] for u in us);blo=min(u['balcony'] for u in us);bhi=max(u['balcony'] for u in us)
  items=[('공고 기준일',f'{notice}'),('분양가 기준 층','‘기준층’ 금액(1~4층은 별도 금액)'),('계약금 비율',f'분양가의 {c}% (1차 1,000만 원)'),('중도금 비율',f'분양가의 {i}%'),('잔금 비율',f'분양가의 {100-c-i}%'),('기준층 분양가 범위',f'{man(lo)} ~ {man(hi)}'),('발코니 확장비 범위(선택)',f'{man(blo)} ~ {man(bhi)}'),('세금·옵션·중도금 이자','분양가에 포함하지 않음')]
  body=''.join(f'<tr><th scope="row">{a}</th><td class="left">{b}</td></tr>' for a,b in items)
  html=table(cap,['비교 항목','이 단지의 공고 기준'],body,'checklist')
 links=' · '.join(f'<a href="{escape(b["source"])}" target="_blank" rel="noopener noreferrer">{escape(b["label"])} 모집공고 ↗</a>' for b in blocks)
 points=''.join(f'<li>{escape(p)}</li>' for p in copy['points'])
 return (f'<div class="calc-summary calc-summary-{view}"><h3>{escape(copy["table_title"])}</h3><p>{escape(copy["table_lead"])}</p>{html}'
  f'<ul class="calc-summary-points">{points}</ul>'
  f'<p class="calc-summary-note">{escape(copy["note"])} 발코니 확장·옵션·세금·중도금 이자·등기 비용은 별도이며, 계약할 동·호수의 실제 금액과 남은 물량은 공식 분양처에서 확인해야 합니다.</p>'
  f'<p class="calc-summary-source">자료 확인일 {reviewed} · 공고 기준 {notice} · {links}</p></div>')
