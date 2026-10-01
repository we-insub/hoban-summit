# 호반써밋 첨단3지구 인수인계

이 저장소는 호반써밋 시안 1·2·3 전용입니다. 기존 챔피언스시티 프로젝트와 분리한 공개 복사본입니다. 먼저 README.md와 AGENTS.md를 읽습니다.

## 수정·검증

공통 문구는 scripts/build_concepts.py, 팝업 HTML은 templates/reservation-template.html에서 수정합니다. CSS·기능·데이터는 README의 원본 목록을 따릅니다. 빌드 후 verify_concepts.py와 PC·모바일 화면으로 확인합니다. SQL이나 함수 변경 없이 단순 복사만으로 운영 DB가 새로 생성되지는 않습니다.

메뉴·예약 검증·동의·ctx는 유지합니다. 이름 한글 1~6자, 전화번호 11자리 자동 하이픈, 과거 방문 금지, 필수·선택 동의 구분이 있습니다. 동의 수정은 화면·서버의 문구와 버전을 함께 검토합니다. 실제 정보·검색량·순위를 만들어 넣지 않습니다.

## 운영 예약 연결

공개 버전은 concepts/reservation-config.js의 previewMode가 true입니다. 운영 준비 후 본인이 접근 가능한 모하모아 Supabase의 공개 anon 키와 호반 전용 함수 URL을 넣고 previewMode를 false로 바꿉니다. `service_role` 키와 Slack Webhook을 이 파일에 넣지 않습니다.

```js
window.RESERVATION_CONFIG = {
  previewMode: false,
  url: "https://YOUR_PROJECT.supabase.co/functions/v1/hoban-summit-reservation",
  anonKey: "YOUR_PUBLIC_ANON_KEY"
};
```

- 서버 함수: supabase/functions/hoban-summit-reservation
- 서버 저장 ctx: `호반써밋첨단3지구`
- 접수 테이블: public.consultation_requests
- RPC: public.submit_hoban_summit_consented
- 서버 Secret: SLACK_HOBAN_WEBHOOK_URL, RESERVATION_ALLOWED_ORIGINS
- SUPABASE_URL·SUPABASE_SERVICE_ROLE_KEY는 서버 환경에서 사용합니다.

운영 URL의 정확한 Origin을 허용 목록에 추가하고 기존 Origin은 보존합니다. 별도 호반 Slack 채널을 원하면 SLACK_HOBAN_WEBHOOK_URL을 설정합니다. 기존 코드에는 공통 SLACK_RESERVATION_WEBHOOK_URL fallback이 있으므로 실제 수신 채널을 확인합니다. 비밀값은 서버 Secrets에만 저장합니다. 호반 ctx를 챔피언스시티 ctx로 바꾸지 않습니다.

`supabase/hoban-consultation.sql`은 기존 상담 테이블·동의·홍보 연락처 스키마를 전제로 하는 **참고 사본**입니다. 새 DB 초기화 파일이 아니며 기존 운영 DB에 무조건 재실행하지 않습니다. 기존 프로젝트의 테이블·RPC·권한과 배포 함수 상태를 먼저 확인합니다. 이 저장소를 공개한 작업에서 DB 변경·함수 배포·실예약 테스트는 하지 않았습니다.

상담정보 보관·동의·Slack 사본 처리 등의 운영 점검은 CONSENT_OPERATIONS.md를 읽습니다. 연결 완료 후 합성 테스트로 저장 ctx·관심 주택형·시안·동의와 알림을 검증합니다.

## Cloudflare Pages

동일 저장소에서 선택한 시안을 배포합니다.

| 항목 | 설정 |
|---|---|
| 저장소 | we-insub/hoban-summit |
| 빌드 명령 | python3 scripts/build_concepts.py |
| 출력 디렉터리 | dist/hoban/01 또는 02 또는 03 |

빌드 환경에서 Python 3 사용 가능 여부를 확인합니다. 초기 배포는 noindex 초안입니다. 실제 도메인 연결 후 canonical·사이트맵·robots·HTML robots 및 _headers의 X-Robots-Tag를 원본/빌더에서 함께 수정합니다. 현재 빌더는 공개 모드 옵션이 없으므로 문서를 읽었다는 이유로 색인 설정이 자동 전환되지는 않습니다.

## 구글·네이버

SEARCH_INDEXING_HANDOFF.md를 따라 실제 도메인별 소유권 확인·사이트맵 제출·URL 요청·결과 확인을 진행합니다. 세 시안은 현재 같은 콘텐츠의 디자인 선택지이므로 대표 버전 선정과 중복 처리부터 결정합니다.
