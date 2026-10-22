# 동업자용: 01~10 최신본 배포 후 IndexNow·색인 요청 (2026-10-23)

도메인을 가진 동업자가 진행한다. 이 저장소를 `git pull`한 뒤 README.md → AGENTS.md → PARTNER_UPDATE_20261022.md → SEARCH_INDEXING_HANDOFF.md 순서로 읽고 아래를 진행한다.

## 현재 상태 (2026-10-23 확인)

- 실제 도메인 01~10은 예전 단일 페이지 버전이다. 제목이 이모지 버전이고 /overview/, /price/, /calculator/ 등 상세 페이지는 404다.
- 이 저장소의 최신 빌드는 메인+8개 상세 페이지 구조이며 로컬 검토용 noindex(HTML robots meta, `_headers`의 X-Robots-Tag) 상태다.

| 번호 | 도메인 |
|---|---|
| 01 | mohamoa-cheomdan.com |
| 02 | mohamoa-homeplan.com |
| 03 | mohamoa-hometour.com |
| 04 | mohamoa-blockguide.com |
| 05 | mohamoa-homebudget.com |
| 06 | mohamoa-floorplan.com |
| 07 | mohamoa-neighborhood.com |
| 08 | mohamoa-community.com |
| 09 | mohamoa-visit.com |
| 10 | mohamoa-homechoice.com |

## 순서

1. **빌드·검증:** `npm ci` → `npm run build:calculator` → 01~10 각각 `python3 scripts/build_concepts.py --version NN` → `python3 scripts/verify_concepts.py --version NN`. 모두 통과해야 한다. 빌드하면 각 `dist/hoban/NN/`에 IndexNow 키 파일(`<키>.txt`)이 생긴다.
2. **운영 공개 설정:** noindex 해제는 생성된 HTML만 고치지 말고 빌더(`scripts/build_concepts.py`, `scripts/menu_pages.py`)에서 HTML robots meta, `_headers`의 X-Robots-Tag, robots.txt(Sitemap 줄 포함), sitemap.xml 주석을 운영 모드로 생성하게 바꾼다. canonical은 각 번호의 실제 도메인 URL이어야 한다. 서버 Secrets·Edge Functions·예약/동의 정책·ctx는 바꾸지 않는다.
3. **Cloudflare 배포:** `dist/hoban/01`~`10`을 각 번호의 도메인에 배포한다. 키 파일도 함께 올라가야 한다.
4. **최신본 매칭 점검:** `python3 scripts/indexnow_submit.py` (인자 없이 실행하면 점검만 한다). 번호마다 사이트맵의 모든 URL이 HTTP 200인지, 실제 title·H1·canonical·robots가 로컬 dist와 같은지, noindex가 없는지, 키 파일이 응답하는지 확인한다. SKIP이 나온 번호는 표시된 원인을 고쳐 재배포하고 다시 점검한다.
5. **Bing·네이버 전송:** 점검이 모두 ready인 번호만 `python3 scripts/indexnow_submit.py --submit`으로 보낸다(한 번호만은 `--version NN`). 매칭되지 않은 번호는 스크립트가 자동으로 건너뛴다. 결과는 `concepts/indexnow-log.jsonl`에 남는다.
6. **구글:** IndexNow를 지원하지 않는다. Search Console에서 도메인별 sitemap.xml을 다시 제출하고, 메인 URL은 URL 검사(실제 URL 테스트) 후 색인 생성을 요청한다. 네이버 서치어드바이저·Bing 웹마스터 도구에도 도메인별 사이트맵을 제출한다.
7. **기록:** `DEPLOYMENT_STATUS.md`에 01~10 각각 실제 URL, HTTP 200, 매칭 결과, noindex 여부, canonical, 사이트맵 제출 상태(구글·Bing·네이버), IndexNow 응답 코드(200/202 등), 확인일을 적는다. 전송·요청한 것과 실제 색인된 것은 구분하고, 실행하지 않은 항목은 미실행으로 남긴다.
