# 프로젝트 작업 AI 필수 지침

1번을 바탕으로 01~10을 만들거나 수정할 때 TEN_VERSION_WORKFLOW.md와 concepts/version-plan.json을 필수로 읽는다. PROJECT.md 10개를 생성·갱신하고 PC·모바일 메뉴의 첫 사업개요·마지막 모하모아를 유지한다. 중간 순서와 본문은 버전별 독자 질문에 맞춘다. 검색어는 후보·확인 상태와 실제 답변 위치를 기록한다. 순서 변경을 스팸 회피 수단이라고 보고하지 않는다.

추가 시안은 concepts/VARIANT_GUIDE.md, 상담·동의·보관기간 작업은 CONSULTATION_DATA_GUIDE.md와 LIVE_RESERVATION_GUIDE.md를 함께 읽는다. 01~10은 모두 같은 실제 예약 접수 기능을 사용한다. 버전별 미리보기 덮어쓰기를 다시 넣지 않는다. 2026-10-01 사용자가 최신 변경의 GitHub commit·push를 요청했다. 웹사이트 배포·도메인 결제·검색엔진 등록은 별도 작업이다.

## 새 페이지 생성·수정 시

작업 전에 아래 문서를 읽고 해당 작업 범위에 적용한다.

1. `KOREAN_COPY_GUIDE.md` — 자연스러운 한국어, 독자에게 필요한 문구.
2. `KEYWORD_CONTENT_GUIDE.md` — 약 20개 검색어 후보를 의도별로 묶고 본문·페이지에 연결.
3. `SEO_AEO_GEO_CONTEXT.md` — 페이지별 사실·출처·SEO·직접 답변·GEO 입력 명세.
4. 대상 단지·버전의 프로젝트 문서. 호반은 `concepts/README.md`, `concepts/WEBSITE_CONTENT_DELIVERABLE.md`, `concepts/DESIGN_STANDARD.md`를 읽는다.

공식 홈페이지의 해당 페이지와 지도·도면 이미지를 실제로 확인하고, 공식 강조 포인트·시설명·지역명·상품 특징을 추출해 제목·본문·FAQ에 적용한다. KEYWORD_CONTENT_GUIDE.md의 추출 표와 KOREAN_COPY_GUIDE.md의 고객용 문장 기준을 따른다. 현재 시설·예정 시설을 구분하고, 지도만으로 역세권·학군·거리·이동시간을 단정하지 않는다.

검색어 후보·적용 URL·본문 위치·확인 결과를 페이지 작업 기록에 남긴다. 확인하지 않은 검색량·순위·주소·가격은 만들지 않는다. 단어 순서만 바꾼 페이지를 양산하지 않는다. 사업지와 모델하우스 주소를 구분한다. 기존 기능·단지별 ctx·동의 정책·문의 연결을 보존한다.

## 공개·검색엔진 등록 시

`PARTNER_START_HERE.md`, `SEARCH_INDEXING_HANDOFF.md`와 `PARTNER_HANDOFF.md`를 먼저 읽는다. 실제 구매·소유한 도메인과 대표 공개 URL이 확인된 뒤 공개 설정을 적용한다. 검토용 noindex를 임의 해제하지 않는다. 생성 파일만 고치지 말고 빌더·원본·배포 설정에 반영한다. 실제 공개 응답의 noindex·canonical·robots·사이트맵을 검증한 뒤 구글·네이버 요청을 진행한다.

콘텐츠 구현, 수집 요청, 색인 결과, 노출·클릭, AI 인용을 별도 상태로 보고한다. 실행하지 않은 계정 등록이나 색인 확인을 완료라고 쓰지 않는다. 문서 자체는 실행 프로그램이 아니므로 작업 AI가 구현·검증·기록을 수행해야 한다.

## 2026-10-01 live reservation update

Read LIVE_RESERVATION_GUIDE.md. All variants 01-10 now use the same live reservation endpoint. Variant-specific preview overrides were removed. This supersedes previous preview-only notes. The user authorized the GitHub update on 2026-10-01. Website deployment and domain purchases are separate tasks.
