# 동업자 전달 · 10개 상세페이지 검수본 · 2026-10-19

사용자 확정: Codex는 로컬 검수 후 GitHub에 푸시한다. 동업자가 최신 소스를 pull한 뒤 운영 작업과 merge하고 Cloudflare에 업로드·배포한다. 이번 푸시를 운영 배포 완료로 보고하지 않는다.

## 반영할 변경

- 각 `concepts/editorial/01.json`~`10.json`: 기존 title·description·질문·자료를 유지하며 H1 주제와 필요한 한국어 문장만 보완했다. 함축·요약하지 않았다.
- `scripts/page_contract.py`: 초기 head에 canonical·OG URL/이미지와 기존 메타의 정합성을 검사하고 H1 주제·공통 날짜를 출력한다. 실제 head 위치·개수·150자 설명·문장 끝·정본·OG 일치 검사가 빌드에서 실행된다.
- `concepts/page-dates.json`: `page_updated_at`은 2026-10-19, `deployed_at`은 null이다. 배포 준비 시 실제 배포일을 설정한다. 자료 확인일 `records`는 해당 자료를 실제 다시 검증했을 때만 갱신한다. 공고 발행일·입주 예정일은 치환하지 않는다.
- `scripts/build_concepts.py`, `scripts/verify_concepts.py`: 새 계약 연결, title·URL 중복 차단, 기존 아이콘 재압축 방지와 PROJECT 기록. 기존 검사 관문은 유지한다.
- `scripts/test_page_contract.py`, `scripts/qa_page.cjs`: 의미 있는 메타 실패 사례·날짜 보존 회귀검사와 로컬 브라우저 검수 도구.

## pull·merge 후 보존할 운영 변경

실제 운영 HTML/자산을 2026-10-19에 대조했으며, 이전 GitHub main에는 아래 운영 변경이 없었다. 이번 검수본은 이 내용을 임의로 복구하거나 덮어쓰는 배포본이 아니다.

1. 10개 실제 도메인의 기존 canonical·index/follow·robots.txt·sitemap.xml·소유권 확인 메타와 공개 헤더.
2. title/og:title의 기존 아이콘 접두사, 자산 해시/캐시 처리, Cloudflare 플랫폼 통계 설정.
3. 전화 상담 탭의 실제 `tel:16005184` 링크. 이전 main의 전화 모드 버튼으로 되돌리지 않는다.
4. `concepts.js`의 `dialog.dataset.mode`, 모드 전환/폼 재열기 시 `dialog.scrollTop=0`, 이름 입력의 `focus({preventScroll:true})`.
5. `.modal-call` 버튼 스타일, booking 모드의 폼 간격·스크롤 관련 CSS, 기존 `.topic-guide` 스타일.
6. 예약 endpoint·공개 설정·서버 ctx·동의 버전·동의 내용·알림 연결·검증된 가격 데이터와 이미지 원본.

운영 빌더에 canonical·OG URL/이미지 출력 코드가 따로 있다면 `apply_contract`와 중복 실행하지 않도록 한 곳에서 생성한다. 사용자에게 보이는 기존 title 접두사를 유지하는 경우 원본 title/OG와 검사 입력도 같은 최종 값을 쓰도록 통합한다. 중복 메타를 허용하도록 검사를 끄지 않는다.

## 로컬 검수와 운영 배포를 분리

현재 `dist/hoban/01`~`10`은 **검토용 noindex 번들**이다. 이 폴더를 그대로 운영에 올리지 않는다. 운영 정본과 merge한 뒤 기존 공개 빌드 절차에서 HTML robots·HTTP X-Robots-Tag·robots.txt·canonical·사이트맵을 함께 확인한다. 새 후보에는 기존 파일·기능·헤더·리다이렉트도 보존한다. 파일 일부만 담은 빈 폴더로 배포하지 않는다.

원고 검수·build·verify·PC1440/모바일390·320 검수는 01→10 순서로 실행했다. 결과·수정 전후·검수 범위·HTML SHA는 `concepts/PAGE_AUDIT_20261019.md`와 JSON에 있다. 실제 소스가 merge로 바뀌면 영향받는 검사를 다시 실행한다. 이전 SHA의 통과를 새 merge 결과의 통과로 대신하지 않는다.

```sh
python3 scripts/build_concepts.py --version 01
python3 scripts/verify_concepts.py --version 01
python3 scripts/test_page_contract.py
python3 -m http.server 4187 --bind 127.0.0.1
```

나머지 버전도 02→10으로 각각 확인한다. PIL이 필요하면 기존 빌드용 Python 환경을 사용한다. npm 스크립트는 이 저장소에 없다. 브라우저 도구는 Playwright와 설치된 Chrome을 사용하며 `PLAYWRIGHT_MODULE` 환경변수로 모듈 경로를 지정할 수 있다.

공개 후보의 초기 HTML 전수 검사 후 운영에서는 각 도메인 root의 HTTP·메타·링크와 PC·모바일 변경 화면을 확인한다. 운영 10개 root/robots/sitemap은 수정 전 기준선에서 모두 200·정본 일치였으며 이 결과는 새 배포의 검증 결과가 아니다. Googlebot 비교는 01·09 표본만 실행했다. 실제 색인·Google 선택 canonical·검색 성과·AI 인용은 확인하지 않았다.

공식 자료 전체를 오늘 새로 확인한 작업은 아니다. 과거 자료 확인일을 배포일로 일괄 치환하지 않는다. GA4 설치를 새로 추가하지 않았으며 운영 통계의 동의 상태별 실제 전송 검증은 별도 미실행이다.
