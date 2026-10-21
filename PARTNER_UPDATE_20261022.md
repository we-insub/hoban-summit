# 2026-10-22 수정본 받기와 적용

이번 전달본에는 01~10 전체의 메뉴별 상세 URL, 보강한 본문·FAQ·출처, 자연스러운 한국어, 메인 title·H1·메타 설명·OG·첫 소개, 분양계산기와 기존 모하모아 음성이 포함됩니다. 예약 폼·ctx·동의와 서버 설정은 보존했습니다.

## 동업자 GPT에게 전달할 지시문

```text
저장소 https://github.com/we-insub/hoban-summit 의 최신 수정본을 적용해 주세요. 기존 작업 폴더와 변경 상태를 확인하고 로컬 변경을 보존한 뒤 git pull --ff-only로 받으세요. 충돌은 강제로 덮어쓰지 마세요.
AGENTS.md와 PARTNER_UPDATE_20261022.md를 먼저 읽고, 연결된 원문 지침을 읽어 진행하세요.
Python 3, Node.js 24, requirements.txt, package-lock.json의 의존성을 준비하세요. npm ci → npm run build:calculator를 실행한 뒤 01~10 각각 build_concepts.py --version NN → verify_concepts.py --version NN 순서로 빌드·검증하세요.
각 번호에 메인과 overview/location/premium/site-plan/floorplan/price/calculator/visit의 8개 상세가 있고 각 URL의 제목·메타·H1·canonical·사이트맵이 일치하는지 확인하세요. 오늘 하루 보지 않기와 수동 방문예약도 유지하세요.
결과를 먼저 로컬에서 보여 주세요. dist/hoban/NN이 해당 버전의 독립 사이트 폴더입니다. 이 빌드는 검토용 noindex입니다. 기존 운영 배포 설정을 보존하고 실제 도메인·상세 URL·canonical·사이트맵·HTML과 HTTP 헤더 robots를 점검하는 별도 공개 절차 없이 그대로 덮어 배포하지 마세요. Git pull만으로 Cloudflare 배포가 완료됐다고 보고하지 마세요.
예약 endpoint·호반써밋첨단3지구 ctx·sourceVariant·동의·보관기간·Telegram/Slack 서버 설정은 임의 변경하지 마세요. 실제 고객정보나 서버 비밀키를 Git에 넣지 마세요. 실제 예약 테스트는 사용자 동의한 테스트 데이터로 진행하고 DB와 알림 수신을 별도로 확인하세요.
SEARCH_INDEXING_HANDOFF.md의 버전별 배포 후 점검을 따르고 구현·배포·색인 요청·색인 결과를 각각 기록하세요.
```

## 터미널 실행

기존 저장소에서 실행합니다. 현재 Node.js 24로 검증했습니다.

```sh
git status --short
git pull --ff-only
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci
npm run build:calculator
python3 scripts/build_concepts.py
python3 scripts/verify_concepts.py
python3 -m http.server 4173
```

검토: http://127.0.0.1:4173/concepts/

전체 명령은 같은 빌더의 일괄 재생성입니다. 내용을 새로 수정할 때는 번호별 작성·빌드·검증 규칙을 따릅니다. dist/·node_modules/·.venv/는 커밋하지 않습니다.

## 원본과 검수 기록

- 본문: concepts/editorial/01.json~10.json
- URL·상세 메타: concepts/routes/01.json~10.json
- 메인 제목: HOME_TITLE_REVISION_20261022.md
- 본문·말투: NATURAL_KOREAN_REVISION_20261022.md
- 메뉴 분리·팝업: MENU_PAGE_SPLIT_PILOT.md의 최신 추가 기록
- 자료 보강: concepts/CONTENT_ENRICHMENT_20261022.md
- 페이지별 명세: concepts/01/PROJECT.md~10/PROJECT.md
- 공통 날짜 검증은 기존 page_contract.py를 보존했습니다. 자료 확인일·발행일은 그대로 두고 페이지 수정일만 2026-10-22로 기록했습니다. 운영 배포일은 미확인 상태를 유지했습니다.

과거 문서의 Git push 미실행 기록은 당시 작업 경계입니다. 이번 사용자가 수정본 전달을 위해 push를 명시 승인했습니다. 웹 운영 배포와 검색 등록은 이번 push와 별도입니다.

검수: 전달 저장소에서 01~10 번호별 빌드·검증, 20개 메인 출력의 승인 제목·H1·소개 일치, 날짜·중복 메타 회귀 검사 2건, 계산 수식 검증을 통과했습니다. 원문 보관 HTML/MD는 증거 SHA를 유지하기 위해 공백을 정리하지 않았습니다. 예약 설정·템플릿·동의·서버 코드의 기존 Git 버전과 동일성도 확인했습니다. 실제 예약·외부 알림 전송·운영 배포는 실행하지 않았습니다.
