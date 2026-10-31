# 2026-10-30 최신본 받기 → 빌드 → Cloudflare 배포 → 검색 콘솔·애널리틱스 7일 성과

전달 커밋: `967a385` (되돌리기 기준점: 태그 `before-persona-rewrite-20261031`, 방법은 ROLLBACK_20261031.md) (저장소 https://github.com/we-insub/hoban-summit, 브랜치 main)

이번 전달본: 번호마다 독자·말투가 다른 새 본문(해요체 5·합니다체 5, 번호별 검수 `python3 scripts/audit_copy.py`), 하단 방문상담 배너(누르면 모하모아식 예약 팝업, 로드 시 자동 팝업 없음), 계산기 메뉴(비용·평수·청약 가점·대출)와 실거래가 메뉴, 계산 결과 이미지·PDF 저장, 번호별 본문·제목·메타 정리. 분양계산기 페이지 앞부분에는 공고 분양가 기준 주택형별 가격 요약 표(분양가·계약금·중도금·잔금·발코니 확장비, 자료 확인일·공고 출처 표시)가 번호별 제목·설명과 함께 들어갑니다. 표 숫자는 source-data.json과 cost-presets.ts의 공고 데이터에서만 만들며 임의로 바꾸지 마세요. 각 번호는 메인+12개 상세(overview/location/premium/site-plan/floorplan/price/calculator/visit + pyeong-converter/subscription-score/loan-calculator).

| 번호 | 도메인 | 번호 | 도메인 |
|---|---|---|---|
| 01 | mohamoa-cheomdan.com | 06 | mohamoa-floorplan.com |
| 02 | mohamoa-homeplan.com | 07 | mohamoa-neighborhood.com |
| 03 | mohamoa-hometour.com | 08 | mohamoa-community.com |
| 04 | mohamoa-blockguide.com | 09 | mohamoa-visit.com |
| 05 | mohamoa-homebudget.com | 10 | mohamoa-homechoice.com |

## 1. 터미널 명령 (기존 작업 폴더에서)

```sh
git status --short
git pull --ff-only
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm ci
npm run build:calculator
for n in 01 02 03 04 05 06 07 08 09 10; do
  python3 scripts/build_concepts.py --version $n && python3 scripts/verify_concepts.py --version $n || break
done
```

검토용 확인: `python3 -m http.server 4173` 후 http://127.0.0.1:4173/concepts/01/ ~ 10/ (각 번호 독립 사이트는 `dist/hoban/NN`).

## 2. 공개 설정 (배포 전에 꼭)

기본 빌드는 **검토용 noindex**(HTML robots meta + `_headers`의 X-Robots-Tag)입니다. 이대로 배포하면 구글이 색인하지 않습니다. 운영 공개 모드(noindex 해제, robots.txt Sitemap 줄, 사이트맵 주석)는 아직 빌더에 구현돼 있지 않습니다. `PARTNER_INDEXNOW_20261023.md` 2번대로 빌더(`scripts/build_concepts.py`, `scripts/menu_pages.py`)에 운영 모드를 구현하고 다시 빌드·검증하세요. 생성된 HTML만 고치지 마세요. canonical은 각 번호의 실제 도메인 URL이어야 합니다. 예약 endpoint·ctx·동의·서버 Secrets는 바꾸지 않습니다.

## 3. Cloudflare Pages 배포

기존 Pages 프로젝트에 번호별로 올립니다(새 프로젝트·도메인 구매 금지).

```sh
npx wrangler login
npx wrangler pages project list        # 번호별 기존 프로젝트명 확인
cat > deploy-projects.local <<'EOF'      # 저장소에 커밋되지 않는 파일(.gitignore)
01 <프로젝트명>
02 <프로젝트명>
03 <프로젝트명>
04 <프로젝트명>
05 <프로젝트명>
06 <프로젝트명>
07 <프로젝트명>
08 <프로젝트명>
09 <프로젝트명>
10 <프로젝트명>
EOF
scripts/deploy_pages.sh                  # 계획만 출력(업로드 없음)
scripts/deploy_pages.sh --go             # 실제 업로드. 빌드가 noindex면 중단됨
scripts/deploy_pages.sh --go 03 05       # 일부 번호만
```

운영 공개 모드로 빌드한 뒤에만 `--go`가 통과합니다. 의도적으로 noindex 상태를 올리려면 `--allow-noindex`를 붙입니다.

## 4. 배포 후 확인

```sh
python3 scripts/indexnow_submit.py            # 점검만(전송 안 함): 사이트맵 URL 200·title/H1/canonical/robots·키 파일
for d in mohamoa-cheomdan.com mohamoa-homeplan.com mohamoa-hometour.com mohamoa-blockguide.com mohamoa-homebudget.com mohamoa-floorplan.com mohamoa-neighborhood.com mohamoa-community.com mohamoa-visit.com mohamoa-homechoice.com; do
  echo "== $d"; curl -sI "https://$d/" | grep -iE "^HTTP|x-robots-tag"; curl -s "https://$d/robots.txt" | head -3
done
python3 scripts/indexnow_submit.py --submit   # 점검이 모두 ready인 번호만 Bing·네이버 전송
```

그 뒤 `SEARCH_INDEXING_HANDOFF.md`의 배포 후 점검 결과를 `DEPLOYMENT_STATUS.md`에 01~10별로 기록합니다.

## 5. 동업자 AI(컴퓨터 유즈)에게 줄 지시문 — Search Console·애널리틱스 7일 성과

```text
01~10 도메인(mohamoa-cheomdan.com, mohamoa-homeplan.com, mohamoa-hometour.com, mohamoa-blockguide.com, mohamoa-homebudget.com, mohamoa-floorplan.com, mohamoa-neighborhood.com, mohamoa-community.com, mohamoa-visit.com, mohamoa-homechoice.com)의 Google Search Console과 Google Analytics(GA4) 상태를 확인하고 최근 7일 성과를 표로 정리해 주세요. 브라우저는 컴퓨터 유즈로 조작하되 로그인은 내가 하고, 비밀번호·인증코드는 입력하지 마세요.

[Search Console]
1. 도메인마다 속성이 등록돼 있는지 확인합니다(도메인 속성 또는 URL 접두어 속성). 이미 있으면 설정을 바꾸지 마세요.
2. 없으면 도메인 속성으로 추가합니다. 소유권 확인은 Cloudflare DNS TXT 레코드로 진행합니다(Cloudflare 로그인은 내가 합니다). 인증 뒤 해당 도메인의 sitemap.xml을 제출하고 처리 상태를 기록합니다.
3. 각 속성의 ‘실적’에서 기간을 최근 7일로 두고 클릭수·노출수·CTR·평균 게재순위, 상위 검색어 3개, 상위 페이지 3개를 읽습니다. 색인 생성 현황(색인됨/색인 안 됨 개수)과 사이트맵 상태도 적습니다.
4. 새로 등록했거나 아직 데이터가 없으면 ‘데이터 없음(신규·집계 지연)’이라고 쓰고 수치를 추정하지 마세요. 색인 요청은 메인 URL만, URL 검사에서 라이브 테스트가 통과한 번호에 한해 진행하고 결과를 따로 기록합니다.

[Analytics(GA4)]
1. 계정에 도메인별 속성·웹 스트림이 있는지 확인합니다. 없으면 번호별로 속성과 웹 스트림(해당 https 도메인)을 만들고 측정 ID(G-…)를 기록합니다.
2. 사이트에 추적 코드를 넣는 작업은 하지 마세요. 개인정보·동의 정책(방문 통계 동의, 예약 동의)과 맞물려 있어 측정 ID만 보고하고 내 승인을 받은 뒤 빌더에 반영합니다.
3. 데이터가 수집되고 있으면 최근 7일 사용자·세션·조회수·평균 참여 시간·상위 페이지 3개·주요 유입 채널을 읽습니다. 태그가 없거나 수집 전이면 ‘수집 안 됨’으로 씁니다.

[결과 표] DEPLOYMENT_STATUS.md에 아래 두 표를 번호 01~10 순서로 기록하고 확인일(오늘 날짜)과 어떤 화면에서 읽었는지 함께 적습니다.
표1 Search Console: 번호 | 도메인 | 속성 상태(기존/신규/실패) | 소유권 확인 | 사이트맵 제출·처리 | 클릭수 | 노출수 | CTR | 평균 순위 | 색인됨/안 됨 | 상위 검색어 | 비고
표2 Analytics: 번호 | 도메인 | 속성·스트림 상태 | 측정 ID | 태그 설치 여부 | 사용자 | 세션 | 조회수 | 평균 참여 시간 | 상위 페이지 | 비고

계정 생성, 약관 동의, 권한 부여, DNS 변경, 유료 결제가 필요하면 하기 전에 내게 확인하세요. 실행하지 않은 항목을 완료로 쓰지 말고, 순위·색인·노출을 보장하는 표현은 쓰지 마세요.
```
