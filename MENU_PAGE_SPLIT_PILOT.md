# 1번 메뉴별 상세페이지 로컬 시안

작업일: 2026-10-21. 최신 사용자 범위는 **1번에 먼저 적용해 로컬에서 확인**이다. 2~10번은 변경하지 않았으며 Git push·운영 배포·색인 제출은 하지 않았다. 이후 확대는 1번 검토 후 번호별 작성 → 빌드 → 검증 → 화면 확인 순서로 진행한다.

## 원문을 가져온 위치

`references/menu-pages-20261021/`에는 시로코 원문, 경복궁 상세 품질 기준, 명소 상세 표준, 한국어 작성 기준, 모하모아 AGENTS·페이지 컨텍스트·색인 대상 페이지·호반 상세 명세의 **원문 전체**를 변경 없이 복사했다. `manifest.json`은 원본 절대 경로와 SHA-256, 복사 파일을 연결한다. 원문을 함축한 가이드로 대체하지 않았다. 경복궁 실제 원고는 `gyeongbokgung-126508-full.json`으로 별도 보존했다. 원래 프로젝트 파일은 수정하지 않았다.

원문 보관과 적용 범위는 구분한다. 시로코의 구체적 행동·장면·이유 연결, 경복궁의 주제별 사실·예외 구분과 실제 상세 URL, 모하모아의 분양 블록·공고·가격 조건·정확한 head 검증을 적용했다. 관광지의 사실·해요체·사진 수·일정·요금·혼잡 10분 고정 예약 문구를 이 단지의 검증된 사실이나 정책으로 가져오지 않았다. 이 프로젝트의 SALE_PAGE_PRIORITY.md와 KOREAN_COPY_GUIDE.md, 기존 예약·개인정보 계약이 우선한다.

## 생성 구조

| 역할 | 로컬 경로 | 예정 공개 canonical |
|---|---|---|
| 메인 | /concepts/01/ | https://mohamoa-cheomdan.com/ |
| 사업개요 | /concepts/01/overview/ | https://mohamoa-cheomdan.com/overview/ |
| 입지환경 | /concepts/01/location/ | https://mohamoa-cheomdan.com/location/ |
| 프리미엄 | /concepts/01/premium/ | https://mohamoa-cheomdan.com/premium/ |
| 단지배치 | /concepts/01/site-plan/ | https://mohamoa-cheomdan.com/site-plan/ |
| 평면타입 | /concepts/01/floorplan/ | https://mohamoa-cheomdan.com/floorplan/ |
| 분양가 | /concepts/01/price/ | https://mohamoa-cheomdan.com/price/ |
| 오시는 길 | /concepts/01/visit/ | https://mohamoa-cheomdan.com/visit/ |

메인 이미지·소개와 예약 기능을 유지하고, 기존 일곱 상세 영역의 정보는 각 상세에 보존했다. 메인에는 직접 답과 상세 이동 링크를 제공한다. 1번 메뉴에 분양가를 추가했으며 첫 메뉴 사업개요·마지막 모하모아는 유지했다. 내부 메뉴는 fragment가 아닌 실제 URL로 이동한다. 기존 `/#overview` 등은 메인의 해당 요약 ID를 유지해 연결이 끊기지 않게 했다. fragment는 서버 리디렉션 대상으로 처리하지 않는다.

페이지마다 초기 HTML의 head에 title·description·robots·canonical·og:title·og:description·og:url을 하나씩 출력한다. H1은 하나이며 상세 주제와 같다. WebPage·BreadcrumbList와 화면 FAQ에 일치하는 FAQPage를 같은 데이터에서 생성한다. 특수 FAQ 태그를 순위 상승 필수 조건으로 취급하지 않는다.

`concepts/routes/01.json`은 URL·메타 명세, `concepts/editorial/01.json`은 본문 원본이다. `scripts/menu_pages.py`가 기존 빌드 후 메뉴·메타·본문·사이트맵·PROJECT.md를 생성한다. 다른 번호는 routes 설정이 없어 기존 원페이지 구조를 유지한다. 생성된 HTML만 고치는 방식이 아니다.

## 로컬 실행

빌드에 Pillow·BeautifulSoup4가 필요하며 requirements.txt에 기록했다.

```sh
python3 scripts/build_concepts.py --version 01
python3 scripts/verify_concepts.py --version 01
python3 -m http.server 4173 --bind 127.0.0.1
```

메인: http://127.0.0.1:4173/concepts/01/

독립 번들은 `dist/hoban/01/`이다. 해당 폴더를 루트로 서빙한 검수 서버는 http://127.0.0.1:4175/이며, 실제 배포의 루트 경로·자산 포함을 확인하기 위한 서버다. 로컬 Origin에서 실제 예약 접수 허용 여부와 운영 DB·알림 수신 검증은 별개다.

## 사이트맵과 공개 정책

8개 canonical URL을 담은 sitemap.xml을 로컬 페이지 묶음과 독립 번들에 생성했다. **운영 제출 전 후보 파일**이며 robots에는 아직 제출용 사이트맵 주소를 광고하지 않는다. 로컬 HTML의 noindex와 번들의 X-Robots-Tag:noindex를 유지한다. canonical에 예정 공개 URL이 있다는 사실은 운영에서 그 경로가 존재하거나 색인됐다는 뜻이 아니다.

운영 반영 때는 현재 운영 URL·기존 헤더·소유 확인 값을 보존하고, 실제 공개 200·정상 본문·색인 허용·정확한 canonical을 검증한 URL만 운영 사이트맵으로 제출한다. 초안/noindex URL은 운영 사이트맵에서 제외한다. SEARCH_INDEXING_HANDOFF.md의 7개 점검과 계정별 제출 결과를 기록하기 전에는 검색 등록 완료라고 하지 않는다. 이 로컬 빌더는 검토용이며 공개 noindex를 해제하는 옵션을 제공하지 않는다.

## 기능·원고 보존과 검증

- 같은 예약 HTML·필수/선택 동의·고정 단지 ctx·sourceVariant 01·전화 링크·서버 endpoint를 보존했다. 8개 페이지의 팝업이 동일한지 비교했다.
- 원래 `script.js`, 동의 정책, 예약 설정, Supabase 함수·DB·Secrets는 변경하지 않았다.
- 원래 concepts.js는 평면·계산기가 항상 함께 있다고 가정했다. 1번 전용 multipage.js는 해당 요소가 있을 때만 실행하도록 바꿨다. 다른 버전의 원본 클라이언트는 보존했다.
- 초기 HTML의 각 head 태그 개수·위치·값, 단일 H1, 중복 ID 없음, 실제 메뉴 URL·자산·FAQ와 JSON-LD 일치·8개 사이트맵 URL을 로컬/독립 번들에서 확인했다.
- 일반 브라우저·Googlebot 각각 8개 URL·2개 서버, 총 32개 초기 HTML 응답의 HTTP 200과 동일한 제목을 확인했다. 없는 경로는 두 서버 모두 404다. `http-results.json`에 기록했다.
- 브라우저에서 메뉴 이동 시 실제 URL·title·H1·canonical 변경, 평면 135 선택의 이미지 변경, 분양가 135 기준층의 78,700만원·readonly, 예약 폼 표시를 확인했다. 새 예약은 제출하지 않았다.
- PC CSS 너비 1440·모바일 390에서 8개 URL의 문서 가로 넘침 없음, 상세 소개 PC20px·모바일18px을 확인했다. 실제 폰·모든 브라우저 호환성 확인은 아니다.
- 2~10번 HTML의 SHA를 작업 전과 비교해 변경되지 않았음을 확인했다. `protected-02-10-before.json` 참조.
- 시로코처럼 자료 소개보다 독자에게 필요한 정보를 직접 전달하도록 1번의 입지·커뮤니티·방문 설명 일부를 수정했다. 사실 기준일·예정 조건·출처를 유지했고 미래 시세·거리·학교 배정·운영 상태를 새로 추측하지 않았다. 경복궁의 미완료 항목을 합격 예문으로 간주하지 않았다.

증거는 `references/menu-pages-20261021/`에 저장한다. 원문 보관, 코드 구현, 로컬 HTTP/화면, 운영 배포, 실제 색인, 검색 유입·AI 인용을 별도로 기록한다. 이번 상태는 **1번 로컬 시안**이다. 2~10 확대·Git push·Cloudflare 반영·GSC/네이버/Bing 요청·실제 AI 인용 측정은 미실행이다.

## 2026-10-21 팝업 ‘오늘 하루 보지 않기’ — 1번 한정

사용자 요청으로 1번의 메인·7개 상세 팝업에 체크박스와 닫기 버튼을 추가했다. 체크한 뒤 닫으면 한국 시간(Asia/Seoul, UTC+9) 다음 자정까지 같은 브라우저·같은 Origin·같은 버전의 자동 팝업을 숨긴다. 메뉴 이동·새로고침에도 유지한다. 체크하지 않고 닫으면 다음 페이지에서는 기존처럼 자동으로 열린다. 수동 방문예약 버튼은 숨김 설정과 무관하게 폼을 연다. 수동으로 열어 체크를 해제하고 닫으면 숨김 설정을 해제한다.

만료 시각은 localStorage의 `hoban:01:popup-hidden-until`에 숫자로만 저장한다. 이름·전화번호·동의값을 저장하지 않는다. 이 체크박스는 예약 form 밖에 있어 접수 payload·개인정보 동의와 섞이지 않는다. 저장소 접근이 차단돼도 팝업 닫기와 수동 예약은 작동하도록 처리했다. 저장이 허용되지 않는 브라우저에서 페이지 간 지속성을 보장하는 것은 아니다. 다른 기기·Origin은 별도의 브라우저 설정이다.

빌더가 처음부터 닫힌 팝업 HTML을 생성하고, 1번 전용 클라이언트가 저장한 만료 시각을 확인한 뒤 필요할 때만 자동으로 열어 순간적으로 나타나는 현상도 방지한다. 닫기 버튼·상단 X·Escape·배경 클릭은 같은 숨김 저장 규칙을 사용한다. 원래 공통 script.js와 2~10번 클라이언트는 수정하지 않았다.

검증: 체크→닫기→모바일 메뉴로 평면 페이지 이동에서 자동 팝업 없음, 새로고침에서도 없음, 하단 방문예약 버튼으로 폼 다시 열림을 실제 브라우저에서 확인했다. 별도 Node 검증으로 한국 시간 자정 직전/직후·연도 변경·만료·잘못된 저장값을 확인했다. 기존 8개 경로·메타·가격 계산·팝업 동일성·동의 정책 검증을 통과했다. 예약 전송은 하지 않았다.

**확대 대기:** 사용자가 1번 시안을 오케이한 뒤에만 2~10번에 순서대로 적용한다. 이 기록은 확대 승인이나 Git push·운영 배포 승인이 아니다.

## 2026-10-21 확대 완료: 01~10

사용자가 GPT-6.1 Sol·Medium 병렬 작업을 승인하여 02~10에도 적용했다. 해당 승인 전의 ‘01만 적용, 나머지 보류’ 기록보다 이 절을 우선한다. 세 작업자가 02~04/05~07/08~10 routes 원본을 분담하고 통합 단계에서 공통 빌더·팝업을 적용했다.

- concepts/routes/01~10.json: 각 버전의 기존 원고와 질문에 맞는 한국어 title·description·H1 및 소유 도메인 예정 canonical.
- 각 번호 홈+7개 상세: overview/location/premium/site-plan/floorplan/price/visit. 80개 로컬 HTML과 80개 독립 배포 HTML.
- 기존 메뉴의 상대순서와 마지막 모하모아 유지. 분양가 링크 추가. 내부·관련 메뉴는 실제 상세 URL이며 화면과 JSON-LD FAQ가 일치한다.
- 팝업의 오늘 하루 숨김은 번호별 키로 한국 시간 다음 자정까지 적용. 다른 메뉴로 이동해도 유지하며 방문예약 수동 버튼은 정상 작동한다. 테스트 후 숨김 선택값은 모두 해제했다.
- 예약 폼 원문은 변경 전 해시와 10종 모두 일치한다. ctx·sourceVariant·endpoint·동의·보관기간·전화 연결을 변경하지 않았다. 서버/DB 변경·실제 접수·외부 알림 전송은 실행하지 않았다.

### 검증 결과

| 범위 | 결과·증거 |
|---|---|
| 빌드·정적 검증 | build_concepts.py 전체 / verify_concepts.py 전체 통과. 160개 HTML의 제목·H1·canonical·메뉴·자산·FAQ·사이트맵·팝업 및 25개 가격·동의 일치 확인 |
| 로컬 HTTP | 80개 URL HTTP 200. references/menu-pages-20261021/all-http.json |
| PC·모바일 | 실제 CSS 폭 1440·390에서 각각 80개, 총160회. 가로 넘침·로딩 완료 이미지 오류 없음. references/menu-pages-20261021/all-responsive.json |
| 팝업 | 10종 모두 체크·닫기→다른 메뉴 진입 후 자동 표시 안 됨, 수동 방문예약 열기 통과. all-popup-results.json |
| 상호작용 | 10종 평면도 135 선택 후 이미지 변경 확인. 10번 PC 메뉴 클릭→분양가 title 변경, 135 기준층 78,700만원 읽기 전용·잔금 275,450,000원. 02 모바일 메뉴 클릭→입지환경 상세 진입 |
| 날짜 경계 | popup-preference.js의 한국 자정 전후·연말·만료·잘못된 값 확인 |

새 공식 자료 조사나 본문 전체 보강은 이 구조 작업의 완료 범위가 아니다. 로컬 noindex 유지. Git push·운영 배포·검색 등록은 실행하지 않았다. 운영 서버의 기존 원페이지 URL을 바꾸기 전 noindex·canonical·사이트맵·배포 설정 검수는 별도로 수행한다.

## 분양계산기 공통 메뉴 추가

2026-10-21 사용자 요청으로 01~10 모두 분양가 다음에 ‘분양계산기’를 추가했다. 기존 /price/는 가격표·납부 조건 안내를 유지하고, 입력과 계산 탭은 /calculator/로 이동했다. 메뉴·관련 링크·홈 요약·페이지 메타·canonical·사이트맵과 PROJECT.md를 생성한다. 총90개 로컬 및90개 독립 HTML이다. 공통 소개는 concepts/calculator-page.json이며 기존7개 본문 모델·가격원본·예약/동의는 보존했다.

전체 빌드·정적 검증 통과. 10종 계산기를 CSS 1440/390에서 확인했고 넘침 없음, 135형 기준층 선택 시78,700만원 갱신 및readonly 확인. 1번 모바일 메뉴 클릭으로 계산기 진입 확인. 증거: references/menu-pages-20261021/calculator-checks.json. 운영 배포·검색 등록·실제 상담 제출은 미실행이다.
