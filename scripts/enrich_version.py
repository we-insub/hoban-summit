# -*- coding: utf-8 -*-
"""Apply one reviewed source set to one version; build/QA remains explicitly sequential."""
import argparse,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def apply(ident):
 p=ROOT/f'concepts/editorial/{ident}.json';d=json.loads(p.read_text());shared=json.loads((ROOT/'concepts/hoban-enrichment.json').read_text())
 if d.get('copy_review_revision'):raise SystemExit('Reviewed Korean copy is protected. Edit editorial/NN.json directly; do not re-import the initial enrichment over it.')
 for k,m in shared['sections'].items():d['sections'][k].update(copy.deepcopy(m))
 if ident=='02':d['sections']['types']['answer']='주택형과 층을 선택하면 해당 공고의 공급금액이 채워집니다. 발코니 확장비는 옵션 탭에 별도로 표시되며, 선택 체크를 해야 총액에 더해집니다. 다른 유상옵션은 계약 자료에서 확인한 금액을 입력해야 합니다.'
 d['sections']['cost']['intro']='주택형·층별 공고 금액과 별도 비용, 납부 조건을 나눠 안내합니다. 자금 계산은 분양계산기 메뉴에서 이용할 수 있습니다.'
 d['enrichment_revision']='2026-10-22';d['enrichment_source']='../research/20261021/mohamoa-reports-full.json'
 if ident=='01':
  d['sections']['location']['answer']='호반써밋 첨단3지구 A7·A8은 첨단 생활권 북쪽의 서로 다른 부지에 있습니다. 롯데마트·첨단종합병원·국립광주과학관은 남쪽 기존 생활권의 시설이며, 단지 주변 학교 부지와 도시철도 2호선·연결도로는 계획 사항으로 구분됩니다. 원하는 주택형이 있는 블록에서 통학·장보기·출퇴근 경로를 비교할 수 있습니다.'
  d['sections']['premium']['answer']='A7은 운동시설·작은도서관·주민카페를, A8은 운동시설과 함께 게스트하우스·스마트에듀센터 등을 안내합니다. 84㎡는 A7, 117·135㎡는 A8이므로 원하는 면적이 있는 블록의 시설을 비교해야 합니다. 시설은 설치 계획이며 운영시간·이용료는 별도입니다.'
 if ident=='03':d['sections']['location']['cards'][0]['text']='자녀의 책상과 침대를 놓을 위치, 가족이 거실을 사용하는 시간을 함께 생각하면 공부 공간과 공용 공간의 관계를 비교하기 쉽습니다.'
 if ident=='09':d['sections']['cost']['answer']=d['sections']['cost']['answer'].replace('아래 계산기는','분양계산기 메뉴는')
 if ident=='07':
  blocks=d['sections']['location']['details'];d['sections']['location']['details']=[blocks[i] for i in [1,2,3,0,4]]
 if ident=='08':
  blocks=d['sections']['premium']['details'];d['sections']['premium']['details']=[blocks[i] for i in [2,1,0,3]]
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 route=ROOT/f'concepts/routes/{ident}.json';r=json.loads(route.read_text())
 for page in r['pages']:
  k=page['section']
  if k=='calculator':page['description']='공고 기준 주택형·층별 분양가에 발코니 확장과 선택 옵션을 더해 필요한 자금을 계산합니다. 취득세 일반세율 추정과 대출 상환 조건별 모의 DSR도 확인할 수 있습니다.'
  if k=='premium':page['description']='A7의 운동시설·작은도서관·주민카페와 A8의 게스트하우스·스마트에듀센터 계획을 비교합니다. 주택형이 있는 블록의 시설 구성과 위치를 함께 안내합니다.'
  if k=='cost':page['description']='2026년 6월 5일 공고의 25개 타입·층별 공급금액과 발코니 확장비를 비교합니다. 84A 기준층 공급금액 5억 4,300만원과 확장비 919만원의 합산 예시, 별도 비용과 납부 조건을 안내합니다.'
 r['changed_at']='2026-10-22';route.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(ident+': full source paragraphs, page FAQs and original narration attached')
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--version',required=True);apply(parser.parse_args().version)
