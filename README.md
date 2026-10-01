# 호반써밋 첨단3지구

모하모아 모델하우스 홈페이지 시안 1~10과 동업자·작업 AI용 제작 지침입니다. 공개 소스 저장소이며 웹사이트 공개 배포·도메인 연결·검색엔진 등록은 별도입니다.

개발을 처음 하는 동업자는 [시작 안내와 GPT 복사용 지시문](PARTNER_START_HERE.md)을 먼저 읽으세요.

## 실행

Python 3와 Node.js가 필요합니다. 외부 패키지 설치는 필요하지 않습니다.

```sh
git clone https://github.com/we-insub/hoban-summit.git
cd hoban-summit
python3 scripts/build_concepts.py
python3 scripts/verify_concepts.py
python3 -m http.server 4173
```

http://127.0.0.1:4173/concepts/ 에서 선택합니다. `/concepts/01/`은 전체 이미지형, `/concepts/02/`는 네이비 분할형, `/concepts/03/`은 밝은 갤러리형입니다. 04~10은 단지·자금·평면·생활권·커뮤니티·방문·선택을 각각 강조합니다. [10종 구성표](concepts/VARIANT_GUIDE.md)를 확인하세요. 독립 배포본은 빌드 후 `dist/hoban/01`·`02`~`10`에 생성됩니다.

**로컬 01~10의 상담폼은 모두 실제 모하모아 운영 접수에 연결됩니다.** 공개 anon 키를 사용하며 서버 비밀키·Webhook·고객정보는 포함하지 않습니다. [운영 연결](LIVE_RESERVATION_GUIDE.md), [10종 생성 명세](TEN_VERSION_WORKFLOW.md), [인수인계](PARTNER_HANDOFF.md)를 읽습니다. 도메인 구매·웹사이트 배포·검색엔진 등록은 아직 진행하지 않았습니다.

## 동업자·작업 AI가 읽을 문서

1. [AGENTS.md](AGENTS.md): 작업 기본 지침
2. [PARTNER_HANDOFF.md](PARTNER_HANDOFF.md): 원본 수정, 운영 연결, Cloudflare 배포
3. [한국어 작성 기준](KOREAN_COPY_GUIDE.md), [검색어·콘텐츠 기준](KEYWORD_CONTENT_GUIDE.md), [SEO·AEO·GEO 템플릿](SEO_AEO_GEO_CONTEXT.md)
4. [디자인 기준](concepts/DESIGN_STANDARD.md), [공식 자료 검수](concepts/OFFICIAL_CONTENT_REVIEW.md), [콘텐츠 결과물](concepts/WEBSITE_CONTENT_DELIVERABLE.md)
5. [구글·빙·네이버 색인 인수인계](SEARCH_INDEXING_HANDOFF.md)

공식 정보 확인일: 2026-10-01. 열 시안은 같은 사실을 공유하는 디자인 선택용 초안입니다. HTML과 HTTP 헤더의 noindex를 유지하며, 공개 도메인 확정 후 실제 본문에 맞는 canonical·사이트맵·색인 설정을 적용합니다.

## 원본

- 공통 본문·메타·FAQ·HTML: `scripts/build_concepts.py`, `scripts/concept_variants.py`
- 예약 팝업 원본: `templates/reservation-template.html`
- 디자인·클라이언트: `concepts/concepts.css`, `concepts/concepts.js`, `script.js`
- 가격·면적: `concepts/source-data.json`
- 상담 공개 설정: `concepts/reservation-config.js`
- 동의: `concepts/consent-policy.js`와 `supabase/functions/hoban-summit-reservation/consent-policy.ts`

`concepts/01~10/index.html`과 `dist/`는 생성물입니다. 원본을 수정한 뒤 다시 빌드합니다.

이미지 원본·재생성 이력은 `concepts/assets/SOURCES.json`과 `EXTERIOR_REGENERATION.md`에 기록돼 있습니다. 공개 저장소라는 이유로 공식 브랜드 자료의 권리가 이전되는 것은 아닙니다. 사용 관계와 범위를 확인해 운영합니다.

## 2026-10-01 update

See CONSULTATION_DATA_GUIDE.md for the deployed consent v2 schema, RPC and Edge Function. This supersedes earlier notes stating the backend is not updated. All versions 01-10 now use the same live submission endpoint. The user authorized the GitHub update on 2026-10-01. Website deployment and domain purchases are separate tasks.

## 2026-10-01 live reservation update

Read LIVE_RESERVATION_GUIDE.md. All variants 01-10 now use the same live reservation endpoint. Variant-specific preview overrides were removed. This supersedes previous preview-only notes. The user authorized the GitHub update on 2026-10-01. Website deployment and domain purchases are separate tasks.
