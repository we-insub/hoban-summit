# 01~10 공통 운영 연결

2026-10-01. 사용자 요청에 따라 10종 모두 실제 예약 접수 모드로 통일했습니다. 이전 문서의 ‘04~10 강제 미리보기’, ‘전달 저장소의 예약 연결 비어 있음’ 설명보다 이 문서가 우선합니다. 2026-10-01 사용자의 후속 요청으로 GitHub 반영 보류를 해제했습니다. 웹사이트 배포와 도메인 구매는 별도입니다.

## 공통 동작

모든 버전은 같은 예약 팝업·입력 검증·동의 정책·비용 계산·전화 연결 코드를 사용합니다. 이름은 한글 1~6자, 전화번호는 숫자 11자리와 자동 하이픈, 방문 일시는 한국 시간 기준 미래 일시만 허용합니다. 선택 홍보·전화·문자 동의 없이 예약할 수 있습니다.

예약 제출 → 모하모아 Supabase 저장 → Slack 알림 순서입니다. ctx는 서버에서 호반써밋첨단3지구로 고정합니다. 상담 내용에 시안 01~10과 관심 주택형을 기록합니다. Slack 알림이 실패해도 이미 저장한 예약은 유지합니다. 동일 요청 재처리 시 중복 접수·알림을 방지합니다. 실제 Slack 수신 채널은 서버의 SLACK_HOBAN_WEBHOOK_URL 또는 공통 fallback 설정을 따릅니다.

## 연결 파일

- concepts/reservation-config.js: 실제 모하모아 호반 Edge Function URL, 공개 anon 키, previewMode=false를 공통 사용합니다.
- scripts/build_concepts.py: 04~10의 강제 미리보기 덮어쓰기를 제거했습니다. 재빌드해도 운영 접수 모드를 유지합니다.
- dist/hoban/01~10: 각 폴더에 공통 연결 파일과 예약·동의·계산기 스크립트를 함께 복사합니다.
- 공개 anon 키는 서버 비밀 키가 아닙니다. service_role·Slack Webhook은 서버 Secret에만 보관합니다.
- DB 동의·기간 컬럼은 CONSULTATION_DATA_GUIDE.md를 따릅니다.

## 도메인별 배포 순서

1. 선택한 버전의 dist/hoban/번호 폴더를 배포합니다. `python3 scripts/build_concepts.py`로 10종을 다시 생성할 수 있습니다.
2. 실제 도메인의 정확한 Origin을 서버 RESERVATION_ALLOWED_ORIGINS에 추가합니다. www 사용 여부에 따라 각각 등록합니다. 기존 주소를 지우지 않습니다.
3. 실제 HTTPS 페이지에서 예약 팝업, 입력 검증, 동의, 계산기, 전화 연결을 확인합니다. 접수 DB의 ctx·시안 번호와 Slack 수신 채널을 확인합니다.
4. 도메인별 canonical·사이트맵·robots·소유권 검증·공개 noindex 해제는 SEARCH_INDEXING_HANDOFF.md를 따릅니다. 현재 로컬 비교 페이지와 배포 전 파일의 noindex는 유지합니다.

현재 10개 도메인의 구매·배포·Origin 등록·검색 등록은 완료하지 않았습니다. 이 작업은 10개 버전의 예약 기능을 운영 서버에 연결하는 작업입니다. 문자 발송 업체나 자동 광고 전화 발송을 연결한 것은 아닙니다.

## 검증 기록

- 로컬·독립 배포 파일 10종의 공통 실제 연결, 팝업·문자 동의, 시안 번호, 자산·앵커·FAQ 일치·읽기 전용 가격·계산기 검증 통과.
- 실제 모하모아 RPC에서 01~10을 각각 가상 입력으로 저장하고 ctx·시안 번호·필수 동의·선택 동의·보관 만료일·동일 요청 재처리를 확인 후 전부 롤백했습니다.
- 배포된 Edge Function에서 10번의 잘못된 문자 동의를 HTTP 400으로 거부하는 것을 확인했습니다.
- 실제 고객 예약, Slack 알림, 문자·전화 발송은 검증 중 전송하지 않았습니다. 실제 운영 도메인에서의 접수·Slack 수신 확인은 배포 후 수행해야 합니다.


## 2026-10-02: mohamoa-cheomdan 도메인 허용 기록

- 운영 도메인: `https://mohamoa-cheomdan.com`.
- Developer는 서버 Secrets를 수정할 수 없으므로 관리자가 호반 전용 Edge Function 기본 Origin 목록에 위 주소만 추가했습니다. `RESERVATION_ALLOWED_ORIGINS`의 기존 값과 Slack Secrets는 수정하지 않았습니다.
- 배포 함수: `hoban-summit-reservation`, ACTIVE version 4, JWT 검증 유지. ctx·동의 정책·DB 저장·Slack 코드는 그대로입니다.
- 검증: 새 Origin OPTIONS 204와 정확한 Access-Control-Allow-Origin, 빈 POST 입력 400(기존 403 차단 해제), 기존 모하모아 Origin 204, 미허용 Origin 403.
- 실제 예약 저장·Slack 발송 테스트는 실행하지 않았습니다. 동업자가 실제 공개 페이지에서 동의한 테스트로 확인해야 합니다. www 또는 다른 도메인은 자동 허용하지 않습니다.
- 공개 저장소 재배포로 설정이 되돌아가지 않도록 함수 원본에도 반영했습니다. 이번 변경은 GitHub commit/push하지 않았습니다. 재배포 전 최신 운영 함수와 로컬 원본의 허용 목록을 비교합니다.


## 2026-10-02: 10개 공개 도메인과 동일 번호의 개별 신청

사용자가 전달한 mohamoa-cheomdan/homeplan/hometour/blockguide/homebudget/floorplan/neighborhood/community/visit/homechoice.com의 HTTPS Origin 10개를 모두 허용했습니다. www 주소는 별도 확인·등록 대상입니다. 기존 Origin과 서버 Secrets·Slack Webhook은 보존했습니다. 호반 Edge Function ACTIVE version 5, verify_jwt=true입니다.

- 같은 전화번호여도 01~10에서 각각 새로운 requestId로 접수하면 개별 예약으로 저장합니다. ctx는 호반써밋첨단3지구로 유지하고 상담 내용에 시안 번호를 기록합니다.
- 같은 requestId와 같은 입력을 재전송하면 기존 id를 반환하고 새 예약·Slack 알림을 만들지 않습니다. 같은 requestId로 시안·입력값을 바꾸면 request_conflict입니다. 테스트 프로그램도 신규 신청마다 새 UUID를 만들어야 합니다.
- 기존 전체 사이트 합산 전화번호 3건/시간 제한을 단지·전화번호·시안별 3건/시간으로 변경했습니다. 동일 IP의 전체 접수 제한은 30건/시간입니다. 제한을 해제한 것은 아닙니다.
- 실제 RPC에서 같은 가상 전화번호로 01~10 신규 접수, ctx·필수 동의·만료일 저장, 동일 UUID 재전송, 변경된 시안 충돌, 시안별 4번째 접수 차단, IP별 31번째 접수 차단을 검증하고 롤백했습니다. 테스트 데이터와 새 Slack 메시지는 남기지 않았습니다.
- 운영 도메인 10개 모두 OPTIONS 204 및 정확한 Allow-Origin, 빈 POST 400을 확인했습니다. 빈 POST는 필수 입력 검증 도달을 뜻하며 실제 예약 접수 성공을 뜻하지 않습니다. 미허용 Origin은 403을 유지했습니다.
- 실제 공개 HTML 및 연결 스크립트에서 01~10 각 sourceVariant, 올바른 호반 endpoint, previewMode=false를 확인했습니다.
- 기존 01 접수 한 건은 ctx·필수 동의·v2 문구·보관 만료일 저장 및 notification_status=sent를 확인했습니다. 선택 홍보·전화·문자 동의는 false였습니다. sent는 Slack의 성공 응답을 서버에서 기록한 상태이며 채널에서 메시지가 정확히 한 건인지 직접 확인한 것은 아닙니다.
- DB 변경 원본: supabase/sql/hoban_cross_variant_reservations.sql. 서버 migration: hoban_cross_variant_reservation_limits. 원본과 전달 저장소에 반영하되 GitHub commit/push는 보류했습니다.

2026-10-02: 사용자의 명시적 요청에 따라 위 서버 원본·SQL·운영 검증 기록과 색인·제목·파비콘 지침을 GitHub에 커밋·푸시합니다. 이 기록은 파비콘 생성·색인 등록·새 Slack 수신 검증을 추가로 완료했다는 뜻이 아닙니다.
