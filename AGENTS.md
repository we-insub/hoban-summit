# 프로젝트 작업 AI 필수 지침

## 최우선: 분양 페이지 생성·페이지네이션 (2026-10-07)

사용자 제공 컨텍스트를 분양에 적용한 `SALE_PAGE_PRIORITY.md`를 작업 전에 가장 먼저 읽고 모든 페이지 생성·수정에 적용한다. 분양 단지 상세·입지·평면·비용·방문 안내·목록·목록 페이지네이션·01~10 버전이 대상이다. 원문은 `PAGE_CONTEXT_SOURCE.md`에 보존했다.

프로젝트 문서의 내용 작성 기준이 충돌하면 `SALE_PAGE_PRIORITY.md`를 우선한다. 사용자 후속 지시와 상위 지침은 그대로 따른다. 검색어·FAQ 수는 고정하지 않으며 기존 약 20개 후보는 검토 예시로 취급한다. 여행·공항·음식점·CPA 예시는 분양에 그대로 적용하지 않는다. 공개 승인·Git 보류·예약 및 개인정보 정책은 임의 변경하지 않는다.

페이지별 명세·공식 근거·검색어 조사·직접 답변 위치를 먼저 작성하고 원본·빌더·출력물에 적용해 검증한다. 자연스러운 한국어와 독자의 분양 의사결정에 필요한 사실·조건을 우선한다. MD 존재만으로 자동 적용·구현 완료라고 보고하지 않는다.


## 새 페이지 생성·수정 시

작업 전에 아래 문서를 읽고 해당 작업 범위에 적용한다.

1. `KOREAN_COPY_GUIDE.md` — 자연스러운 한국어, 독자에게 필요한 문구.
2. `KEYWORD_CONTENT_GUIDE.md` — 조사한 검색 표현을 의도별로 묶어 본문·페이지에 연결. 개수는 고정하지 않는다.
3. `SEO_AEO_GEO_CONTEXT.md` — 페이지별 사실·출처·SEO·직접 답변·GEO 입력 명세.
4. 대상 단지·버전의 프로젝트 문서. 호반은 `concepts/README.md`, `concepts/WEBSITE_CONTENT_DELIVERABLE.md`, `concepts/DESIGN_STANDARD.md`를 읽는다.

공식 홈페이지의 해당 페이지와 지도·도면 이미지를 실제로 확인하고, 공식 강조 포인트·시설명·지역명·상품 특징을 추출해 제목·본문·FAQ에 적용한다. KEYWORD_CONTENT_GUIDE.md의 추출 표와 KOREAN_COPY_GUIDE.md의 고객용 문장 기준을 따른다. 현재 시설·예정 시설을 구분하고, 지도만으로 역세권·학군·거리·이동시간을 단정하지 않는다.

검색어 후보·적용 URL·본문 위치·확인 결과를 페이지 작업 기록에 남긴다. 확인하지 않은 검색량·순위·주소·가격은 만들지 않는다. 단어 순서만 바꾼 페이지를 양산하지 않는다. 사업지와 모델하우스 주소를 구분한다. 기존 기능·단지별 ctx·동의 정책·문의 연결을 보존한다.

## 공개·검색엔진 등록 시

`SEARCH_INDEXING_HANDOFF.md`와 `PARTNER_HANDOFF.md`를 먼저 읽는다. 실제 구매·소유한 도메인과 대표 공개 URL이 확인된 뒤 공개 설정을 적용한다. 검토용 noindex를 임의 해제하지 않는다. 생성 파일만 고치지 말고 빌더·원본·배포 설정에 반영한다. 실제 공개 응답의 noindex·canonical·robots·사이트맵을 검증한 뒤 구글·네이버 요청을 진행한다.

콘텐츠 구현, 수집 요청, 색인 결과, 노출·클릭, AI 인용을 별도 상태로 보고한다. 실행하지 않은 계정 등록이나 색인 확인을 완료라고 쓰지 않는다. 문서 자체는 실행 프로그램이 아니므로 작업 AI가 구현·검증·기록을 수행해야 한다.

2026-10-01: Read concepts/VARIANT_GUIDE.md and CONSULTATION_DATA_GUIDE.md. GitHub commit/push is on hold until explicitly requested.

## 2026-10-01 live reservation update

Read LIVE_RESERVATION_GUIDE.md. All variants 01-10 now use the same live reservation endpoint. Variant-specific preview overrides were removed. This supersedes previous preview-only notes. GitHub commit/push remains on hold.

TEN_VERSION_WORKFLOW.md and concepts/version-plan.json are required for 01-10 builds. Generate all PROJECT.md briefs; first/last menu items and live booking behavior are fixed.

2026-10-02: Cloudflare 배포 후 SEARCH_INDEXING_HANDOFF.md의 「01~10 배포 후 필수 색인 점검」을 각 실제 도메인에 실행하고 DEPLOYMENT_STATUS.md에 10행 결과·확인일·증거를 기록한다. HTTP 200·GSC 라이브 색인 가능·robots 허용·HTML/헤더 noindex 없음·선언 canonical·사이트맵 제출/처리·색인 요청 상태를 각각 확인한다. 문서에 항목이 있다는 이유로 실행 완료로 보고하지 않는다.


## 2026-10-02 제목·파비콘 필수 작업

TITLE_FAVICON_GUIDE.md를 읽고 01~10 각각의 홈페이지 title·H1·og:title을 본문에 맞게 검수한다. 사이트 아이콘(파비콘)은 번호별 실제 SVG 원본·PNG·ICO·apple-touch-icon 파일을 생성하고 빌더에서 복사 및 head 링크를 구현한다. 각 배포 폴더에 포함해 Cloudflare에 업로드하고 실제 도메인의 이미지 응답·브라우저 표시를 확인한다. 지침만 작성하거나 제목을 바꾼 것을 아이콘 생성·업로드 완료로 보고하지 않는다. DEPLOYMENT_STATUS.md에 버전별 결과를 기록한다.

## 2026-10-07 01~10 직렬 수정

사용자가 01~10 직렬 작업을 지정했다. 각 버전의 editorial/NN.json과 PROJECT.md를 작성하고 `python3 scripts/build_concepts.py --version NN` → `python3 scripts/verify_concepts.py --version NN` → 해당 화면 검수 순서로 진행한 후 다음 버전을 수정한다. 동시에 여러 버전을 수정하거나 하위 에이전트로 나누지 않는다. 버전별 질문·사실·출처·검색 표현은 concepts/editorial/NN.json에 보존되며 빌더가 실제로 읽는다. 조사 원문은 concepts/SEARCH_RESEARCH_20261007.md, 이번 결과는 concepts/SALE_REVISION_REPORT_20261007.md를 참고한다.

## 2026-10-07 전체 본문 수정 보완

사용자가 01~10 전면 수정을 요청하면 한 번호의 실제 본문·FAQ·소개·공식 근거를 작성하고 빌드·검수한 뒤 다음 번호로 진행한다. 메타·첫 답변만 바뀐 상태를 전체 본문 수정으로 보고하지 않는다. `SALE_PAGE_PRIORITY.md` 7절과 `FULL_BODY_REVISION_20261007.md`를 참고하며 `concepts/editorial/NN.json`의 7개 `sections` 모델을 유지한다.
