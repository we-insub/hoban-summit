# 10개 상세페이지 검수 · 2026-10-19

## 소스와 요청 범위

사용자가 지정한 `we-insub/hoban-summit`을 기존 체크아웃 부재로 새로 clone한 뒤 `git pull --ff-only origin main`을 실행했다. HEAD와 origin/main은 `2d7a84657f607c44358369f7666586a21154244a`로 일치했다. 원격에는 main만 있다. GitHub 최신 main과 실제 운영 파일이 동일하다는 뜻은 아니다.

대상은 기존 한국어 모델하우스 정보 페이지 01~10이다. 기존 목적·독자·질문·메뉴 위치·URL은 각 editorial JSON과 PROJECT.md를 유지한다. 새로운 페이지·언어·색인 신청·자동 일정은 만들지 않았다. 페이지별 editorial JSON 전체를 실제 읽었으며 원고를 요약하거나 함축하지 않았다. 변경 전후 문장 전체와 읽은 범위·원고/HTML SHA는 [검수 원장](PAGE_AUDIT_20261019.json)에 보존했다.

01 원고 읽기 → 수정 → 해당 번호 build → verify → 브라우저·화면 확인 후 02로 넘어가 같은 순서로 10까지 진행했다. 하위 에이전트는 사용하지 않았다.

## 검수 결과의 구분

아래 6행은 사용자가 이번 대화에서 풀어 설명한 요구를 보고하기 위한 구분이다. 별도로 발견하지 못한 과거의 '확정 6개 계약' 원문이라고 주장하지 않는다. 최상위 9개 페이지 항목을 함께 대조했다.

| 구분 | 실제 확인·수정 범위 | 결과 |
|---|---|---|
| 검색 의도·title·H1 | 기존 질문과 title 유지, 단지명 H1 안에 페이지별 주제 행 추가, 본문 질문과 대조 | 로컬 통과 |
| description·OG·언어 | 설명은 80~97자 완전한 문장. 기존 본문 소개 보존. OG 제목·설명·기존 이미지·한국어 locale 및 실제 head 개수/위치 | 로컬 통과 |
| 정본·색인·발견 경로 | 로컬 canonical도 운영 URL 선언, 초안 noindex 유지. 운영 10개 root/robots/sitemap의 HTTP·정본 별도 대조 | 운영 기준선 확인, 변경 미배포 |
| 본문·FAQ·출처 | 10개 원고 전체 직접 읽기. 생성 HTML 7개 영역·FAQ/JSON-LD·출처·가격 데이터·앵커 대조 | 원고/구조 통과. 공식 사실 전체 최신 재조사는 미실행 |
| 한국어·화면·기능 | 한국어 MD·시로코 전문과 비교. 모든 페이지 PC1440/모바일390·320 첫 화면·직답·푸터 캡처, DOM·이미지·가로넘침·메뉴·계산기 | 명시한 로컬 범위 통과 |
| 날짜·자동 검사 | 공통 날짜 정본, 초기 HTML time 출력, 업데이트/운영 배포/자료 확인 분리. 메타 구조 검사 빌드 연결과 실패 사례·날짜 회귀검사 | 로컬 통과 |

## 페이지별 결과

| 번호 | 운영 URL | 설명 길이 | 보강한 H1 주제 | 원고·빌드·기능·화면 | 운영 반영 |
|---|---|---:|---|---|---|
| 01 | https://mohamoa-cheomdan.com/ | 80 | 위치·주택형·모델하우스 안내 | 로컬 통과 | 미배포 |
| 02 | https://mohamoa-homeplan.com/ | 86 | 계약금·중도금·잔금 계산 | 로컬 통과 | 미배포 |
| 03 | https://mohamoa-hometour.com/ | 91 | 84·117·135형 평면도 안내 | 로컬 통과 | 미배포 |
| 04 | https://mohamoa-blockguide.com/ | 90 | A7·A8 위치·규모·입주 비교 | 로컬 통과 | 미배포 |
| 05 | https://mohamoa-homebudget.com/ | 97 | 주택형·층별 분양가 비교 | 로컬 통과 | 미배포 |
| 06 | https://mohamoa-floorplan.com/ | 89 | 전용·공급면적과 평면 비교 | 로컬 통과 | 미배포 |
| 07 | https://mohamoa-neighborhood.com/ | 91 | 생활시설·학교·교통 계획 | 로컬 통과 | 미배포 |
| 08 | https://mohamoa-community.com/ | 92 | A8 커뮤니티 시설·배치 안내 | 로컬 통과 | 미배포 |
| 09 | https://mohamoa-visit.com/ | 86 | 모델하우스 위치·방문예약 안내 | 로컬 통과 | 미배포 |
| 10 | https://mohamoa-homechoice.com/ | 88 | 주택형·예산·생활권 선택 가이드 | 로컬 통과 | 미배포 |

## 날짜 정본과 동작

`concepts/page-dates.json`의 `page_updated_at`은 이번 수정일 `2026-10-19`이다. `deployed_at`은 실제 배포하지 않았으므로 null이다. `records`는 기존 자료 확인일 기록인 `2026-10-01`·`2026-10-07`을 보존한다. 실제로 검증한 자료의 기록을 갱신하고 번호별 빌드를 실행하면 해당 표시가 초기 HTML에서 함께 바뀐다. 페이지 업데이트일을 변경해도 자료 확인일·공고 발행일·입주 예정일은 바뀌지 않는다. 브라우저의 오늘 날짜나 JS 후처리를 사용하지 않는다.

이번 구현은 정적 빌드의 공통 정본이다. HTML 재빌드 없이 백단에서 날짜를 바꾸는 서비스는 구현하지 않았다. 하루가 바뀔 때 저절로 자료 확인일을 바꾸거나 미배포 상태를 배포 완료로 표시하지 않는다.

자료 확인일 전부를 2026-10-19로 바꾸지 않았다. 오늘 공식 사업개요·오시는 길·A7/A8 유니트 페이지를 추가 참고했지만, PDF 모든 표·지도·시설 운영의 최신 전수 재확인은 하지 않았다. 새 검증이 없는 원본 기록은 유지했다.

## 한국어 감수와 보존

대상 프로젝트의 AGENTS.md, SALE_PAGE_PRIORITY.md, KOREAN_COPY_GUIDE.md, KEYWORD_CONTENT_GUIDE.md, SEO_AEO_GEO_CONTEXT.md, TEN_VERSION_WORKFLOW.md, 관련 버전·디자인·인수인계 문서와 원고를 읽었다. 사용자 지정 한국어 비교 기준은 `/Users/matowe/Desktop/애드센스/docs/writing/locales/kr.md`, 공통 규칙·승인 예문, `/Users/matowe/Desktop/한국라이브나우/시로코.md` 전문을 읽었다. 날짜 의미는 `한국라이브나우/docs/COMMON-DATE-MANAGEMENT.md`와 대조했다. 다른 프로젝트의 서버 구현을 이 정적 사이트에 적용했다고 주장하지 않는다.

시로코는 문체 비교 기준으로 사용했다. 태국 사실·여행 경험·로맨틱 표현, 문서에 포함된 다른 프로젝트의 Muse 지휘 명령은 적용하지 않았다. 내부 작성 지시나 자료를 해설하는 문장을 고객의 선택·방문·비용 확인과 연결했다. 구체적인 변경 전후는 JSON 원장의 `before_after`에 전체 보존했다.

기존 질문·공식 사실·가격·주소·면적·입주 예정일·이미지·출처·동의/예약 endpoint·ctx·전화 연결을 유지했다. 기존 아이콘은 재압축으로 바뀌지 않게 원본 바이트를 보존했고 이후 빌드도 기존 아이콘을 재사용한다. 계산기/예약 서버는 변경하지 않았으며 실제 예약도 제출하지 않았다.

## 검증 명령과 증거

이 저장소에는 package.json과 npm check/test/build가 없다. 기존 정식 명령 `python3 scripts/build_concepts.py --version NN`, `python3 scripts/verify_concepts.py --version NN`을 번호별로 실행했다. 가격 합계·음수/초과 대출·FAQ 일치·원본 보존·동의 정책 대조를 유지했다.

추가 검사 `python3 scripts/test_page_contract.py`는 중복 description, head 밖 robots, canonical 누락을 실패시키고 페이지 업데이트일 변경 시 자료 확인일·공고 발행일·입주 예정일 보존을 확인한다. 빌드 내부 `verify_contract`는 메타 개수/위치·설명 길이/문장 끝·정본/OG 일치·H1 주제를 검사한다. 전체 editorial title·URL 중복도 빌드에서 차단한다. 자동 검사는 한국어 직접 감수나 최신 사실 재조사를 대신하지 않는다.

최종 PROJECT 기록과 아이콘 보존 보강 뒤 01→10 재빌드·verify를 실행해 HTML SHA가 앞서 화면 검수한 것과 같음을 확인했다. 문서만 달라진 상태를 새 화면 검수로 부풀리지 않았다.

증거 위치:

`/Users/matowe/.codex/visualizations/2026/10/19/01a1541d-8c93-7281-b9e3-6658a3b1584b`

`page-qa/NN-browser.json`과 각 폭별 hero·answer·footer PNG에 로컬 증거가 있다. 모든 페이지의 PC·모바일 첫 화면 이미지를 직접 대조했다. 실제 기기/CWV 측정이나 본문 모든 구간의 수동 화면 전수 검수를 했다고 주장하지 않는다.

동업자도 Git pull 후 확인할 수 있도록 `concepts/review-20261019/`에 10개 페이지의 PC1440 첫 화면·모바일390 첫 화면·모바일390 날짜 푸터, 총 30개 캡처를 복사했다. 320px 및 직답 영역 전체 증거는 위 로컬 증거 폴더에 있고, 브라우저 결과값은 Git에 포함한 JSON 원장에도 있다.

운영 기준선은 `source-baseline/baseline.json`, 01~10 HTML, `discovery-browser.json`, `googlebot-sample.json`에 있다. 기본 Python UA의 robots/sitemap 요청은 403이었다. Mozilla/5.0 표본 정상 확인 후 그 UA로 각 10개를 한 번 확인해 20개 리소스가 모두 200이며 canonical과 sitemap loc가 맞음을 확인했다. 01·09 Googlebot 표본은 200, index/follow, 정본 일치, X-Robots-Tag 없음이다. Google 선택 canonical·정식 색인·노출·AI 인용은 미확인이다.

GA4는 Git 소스와 확보한 운영 HTML에서 설치를 확인하지 못했다. 운영 HTML에는 Cloudflare beacon이 있다. 새 추적 설치나 동의 정책 확대는 하지 않았다. 통계의 동의 상태별 실제 전송 검증은 미실행이다.

## Git과 운영 인수인계

초기에는 대상 AGENTS.md의 `GitHub commit/push is on hold until explicitly requested.`에 따라 커밋·푸시를 보류했다. 이후 사용자가 이 대화에서 “검수해서 로컬 띄워서 검수한다음에 깃 푸시해”라고 명시했다. 이 작업은 검수본의 커밋·푸시까지 승인됐으며 운영 배포는 사용자가 지정한 동업자가 맡는다. 다른 작업의 Git 보류 규칙을 영구 해제한 것은 아니다.

운영 배포 미실행: 사용자가 Cloudflare는 동업자가 관리하며 동업자가 Git pull·merge 후 업로드·배포할 예정이라고 확정했다. 이 채팅의 배포 범위는 GitHub 푸시까지다. 앞서 확인한 현재 Cloudflare 계정에도 대상 10개 프로젝트가 없으므로 다른 계정이나 프로젝트에 새로 배포하지 않았다.

운영본에는 기존 GitHub에 없는 공개 설정·소유권 메타·해시 자산·예약폼 스크롤/전화 버튼 개선·일부 CSS가 있다. 차이 파일을 증거 폴더에 저장했다. 운영의 날짜·기능을 검토용 noindex 초안으로 덮어쓰지 않았다. 동업자의 운영 정본 merge·공개 후보 검증·실제 배포·변경 후 운영 PC·모바일 확인은 별도 단계다. [동업자용 인수인계](../PARTNER_REVIEW_HANDOFF_20261019.md)를 함께 전달한다.

이 문서는 실제 작업 결과 기록이다. 적용 대상 MD의 원문을 요약·대체하는 새 규칙 문서가 아니다.
