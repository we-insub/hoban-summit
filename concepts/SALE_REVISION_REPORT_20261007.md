# 01~10 분양 규칙 적용·검수 결과

확인일: 2026-10-07. 작업 기준: AGENTS.md → SALE_PAGE_PRIORITY.md. 하위 에이전트를 사용하지 않고 01 수정·빌드·검수 후 02로 넘어가 10까지 순서대로 진행했다. 최종 공통 빌더·아이콘·근거 링크 검증도 같은 번호 순서로 실행했다.

## 실제 수정

- 버전별 질문과 직접 답변을 첫 이미지 다음 정보 영역에 배치했다. 초기 HTML에 답·근거·조건이 들어간다.
- 단지 위치, 자금 납부 예시, 평면, 블록 비교, 가격, 면적, 생활권, 커뮤니티, 방문 준비, 선택 기준으로 독자의 질문을 구분했다. 공식 사실은 임의로 변형하지 않는다.
- title·메타 설명·og:title과 FAQ 화면·JSON-LD를 각 버전의 질문에 맞춰 생성한다. FAQ·검색어 개수를 맞추는 규칙을 제거했다.
- 공식 공고의 25개 가격과 다섯 주택형의 전용·공급면적을 대조했다. 공고일 2026-06-05와 실제 확인일을 구분했다. 가격을 변경한 작업은 아니다.
- 확인된 자동완성 표현과 공식 자료 기반 편집 후보를 분리했다. Trends 관련 검색어·네이버 제안은 데이터가 부족했으며 검색량과 순위를 만들지 않았다.
- 자체 비교 설명에 필요한 대상·판단 기준을 넣고 사업지/모델하우스, 계획/현재 시설, 주택형/층별 가격, 별도 비용을 구분했다.
- 기존 디자인·이미지·메뉴 첫/끝 고정·예약 기능을 유지했다. 번호별 자체 도형 파비콘 SVG·96 PNG·ICO 16/32/48·Apple 180 PNG를 생성해 head와 독립 빌드 폴더에 연결했다.

## 버전별 확인

| 번호 | 중심 질문·의도 | FAQ 수 | 로컬·독립 HTML/자산/링크 | PC | 모바일 390·320px | 팝업·동의 | 화면 증거 |
|---|---|---:|---|---|---|---|---|
| 01 | 단지 정보·위치 확인 | 5 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/01-pc.png) · [모바일](research/20261007/screenshots/01-mobile-390.png) |
| 02 | 납부 시점별 자금 계획 | 5 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/02-pc.png) · [모바일](research/20261007/screenshots/02-mobile-390.png) |
| 03 | 주택형·평면 구조 확인 | 5 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/03-pc.png) · [모바일](research/20261007/screenshots/03-mobile-390.png) |
| 04 | 블록별 차이 비교 | 4 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/04-pc.png) · [모바일](research/20261007/screenshots/04-mobile-390.png) |
| 05 | 분양가 범위·총 비용 비교 | 5 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/05-pc.png) · [모바일](research/20261007/screenshots/05-mobile-390.png) |
| 06 | 전용·공급면적 정의와 주택형 비교 | 4 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/06-pc.png) · [모바일](research/20261007/screenshots/06-mobile-390.png) |
| 07 | 생활시설 위치와 예정 시설 구분 | 4 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/07-pc.png) · [모바일](research/20261007/screenshots/07-mobile-390.png) |
| 08 | A8 시설 종류·배치·이용 조건 확인 | 4 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/08-pc.png) · [모바일](research/20261007/screenshots/08-mobile-390.png) |
| 09 | 모델하우스 위치·방문 절차 확인 | 4 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/09-pc.png) · [모바일](research/20261007/screenshots/09-mobile-390.png) |
| 10 | 자료 비교 순서와 방문 질문 정리 | 6 | 통과 | 통과 | 통과 | 통과 | [PC](research/20261007/screenshots/10-pc.png) · [모바일](research/20261007/screenshots/10-mobile-390.png) |

PC 검수의 실제 CSS 표시 폭은 01 1422px, 02~10 1600px이며 최종 10번 직접 답 화면은 1440px이다. IAB의 90% 표시 배율을 확인해 모바일 검수에서는 실제 CSS 폭 390px와 320px를 사용했다. 두 폭 모두 document.scrollWidth가 viewport 폭을 넘지 않았다. 넓은 비교표는 해당 표 영역 안에서 스크롤한다.

화면 캡처는 일부 검수 시점의 증거이며 전체 페이지와 모든 기기에서의 시각 QA를 대신하지 않는다. 근거 링크 추가 이후의 최종 직접 답 화면은 [10번 PC](research/20261007/screenshots/10-answer-pc.png)에 보관했다.

## 기능 보존·검증 범위

모든 버전에서 팝업의 방문예약 폼과 필수 수집 동의, 한글 6자 이름·숫자 하이픈 전화번호 입력 패턴을 확인했다. 날짜는 기존 datetime-local 및 과거 금지 로직을 유지했다. 실제 예약은 제출하지 않았으며 DB 저장·Telegram/Slack 도착을 이번 작업에서 재시험한 상태는 아니다. 전화는 기존 tel:16005184, sourceVariant는 각 번호, ctx는 호반써밋첨단3지구를 유지한다. 서버의 동의 버전·보관 정책·알림 코드를 변경하지 않았다.

135 기준층 가격 78,700만원과 117B 평면도 전환을 브라우저에서 확인했다. 검증 스크립트는 25개 가격 계산·잘못된 대출/음수 입력 처리, 화면/FAQ 구조화 데이터 일치, 메뉴/본문 순서, 단일 H1·중복 ID·자산 경로, PNG/ICO 규격과 동의 정책 일치를 확인했다. 직접 답 영역에 해당 버전의 공식 근거가 있는지도 확인했다.

## 원본·빌더·출력·인수인계

- 원본: editorial/01.json~10.json, version-plan.json, source-data.json.
- 빌더: ../scripts/build_concepts.py --version NN. 해당 번호와 dist/hoban/NN만 생성한다. 재빌드해도 문구·근거·아이콘이 유지된다.
- 검증: ../scripts/verify_concepts.py --version NN.
- 페이지 명세: 01/PROJECT.md~10/PROJECT.md의 기본값·SEO·사실·검색 표현·질문/직접 답/근거 표.
- 조사: SEARCH_RESEARCH_20261007.md 및 research/20261007의 원문·가격/면적 대조 결과·빌드 로그·HTTP/브라우저 결과.

## 공개·검색 상태

구현과 로컬 검수 완료. 기존 운영 도메인에는 배포하지 않았다. Git commit/push하지 않았다. 검토용 noindex를 유지했고 공개 canonical·robots·사이트맵·검색 소유권 등록을 변경하지 않았다. 로컬 HTML·아이콘의 HTTP 200 확인은 운영 도메인 검증이 아니다.

수집 요청 / 실제 색인 / 검색 노출·클릭 / AI 출처 채택: 이번 작업에서 확인 또는 실행하지 않았다. 공통 사실과 상담 경로가 있는 10개 사이트이며 제목·디자인·순서·설명 보완만으로 독립 색인 적합성이나 스팸 정책 통과를 보장하지 않는다. 배포 전 SEARCH_INDEXING_HANDOFF.md와 기존 도메인의 canonical·중복 처리 방침을 별도로 검토한다.
