# 상담 DB·동의·보관기간 운영 기록

2026-10-01. 실제 모하모아 Supabase 프로젝트에 반영했습니다. GitHub commit·push는 사용자 요청으로 보류합니다. 01~10 운영 연결은 LIVE_RESERVATION_GUIDE.md를 함께 읽습니다.

## 저장 컬럼

| 테이블 | 컬럼 | 의미 |
|---|---|---|
| consultation_requests | privacy_consent / privacy_consent_at | 필수 개인정보 수집·이용 동의와 시각(기존) |
| consultation_requests | privacy_consent_version / privacy_consent_snapshot | 실제 고지 문구·버전·체크값(기존) |
| consultation_requests | adult_consent | 만 14세 이상 확인. 증거 없는 기존 건은 NULL |
| consultation_requests | retention_ends_at | 예약 보관 만료일(기존) |
| consultation_marketing_contacts | marketing_consent / consented_at | 홍보 목적 개인정보 이용 동의와 시각 |
| consultation_marketing_contacts | expires_at | 홍보 보관 만료일(기존) |
| consultation_marketing_contacts | phone_ad_consent / phone_ad_consented_at | 광고성 전화 동의와 시각 |
| consultation_marketing_contacts | sms_ad_consent / sms_ad_consented_at | 광고성 문자 동의와 시각 |
| consultation_marketing_contacts | withdrawn_at | 홍보 이용 동의 철회(기존) |
| consultation_marketing_contacts | phone_ad_withdrawn_at / sms_ad_withdrawn_at | 채널별 철회 시각 |
| consultation_marketing_contacts | phone_ad_confirmation_due_at / sms_ad_confirmation_due_at | 채널별 2년 주기 수신동의 확인 안내 기한 |
| consultation_marketing_contacts | phone_ad_confirmation_sent_at / sms_ad_confirmation_sent_at | 실제 확인 안내 발송 시각 |
| consultation_marketing_contacts | consent_version / consent_snapshot | 선택 동의 문구·버전·체크값(기존) |

예약과 홍보 연락처를 분리합니다. 기존 전화 동의를 문자 동의로 전환하지 않았습니다. 전화 동의 시각도 기존 동의 증거가 있는 건만 가져왔습니다.

## 현재 연결

- 호반 01~10 팝업은 홍보 이용·광고성 전화·광고성 문자를 각각 선택하도록 수정했습니다. 선택 동의 없이 예약 가능합니다.
- 정책은 hoban-consent-2026-10-01-v2입니다. 모하모아 DB의 호반 RPC와 Edge Function에 반영했습니다. 과거 v1 폼은 호환하고 문자 동의는 부여하지 않습니다.
- ctx는 호반써밋첨단3지구입니다. 챔피언스시티 서버와 정책은 보존합니다. 공통 DB 컬럼은 두 단지가 사용할 수 있지만 챔피언스시티의 기존 폼에는 문자 체크박스를 임의로 추가하지 않았습니다.
- 01~10과 전달 저장소 모두 같은 모하모아 운영 접수 연결을 사용합니다. 강제 미리보기는 제거했고 재빌드한 독립 배포 폴더에도 적용합니다.
- Slack 알림에 문자 동의 여부를 추가했습니다. 실제 예약·알림·문자·전화 발송 테스트는 하지 않았습니다.

## 보관·파기

예약은 방문 희망 일시 + 최대 90일로 저장합니다. 완료·취소가 더 빠르면 기존 트리거가 그 시점 + 90일과 기존 만료일 중 더 이른 날짜로 제한합니다. 목적 달성으로 불필요해지거나 유효한 삭제 요청이 있으면 더 일찍 파기합니다.

홍보 정보는 고지한 동의일부터 최대 3년입니다. 법이 모든 상담정보를 일괄 3년 또는 5년 보관하도록 허용하는 것은 아닙니다. 필요성이 없어지거나 철회하면 먼저 파기합니다. 연장은 새 고지·동의가 필요하며, 정기 확인 안내로 보관기간을 연장하지 않습니다.

기존 champions-consent-retention 작업이 매시간 만료·철회 홍보 연락처와 보관 만료된 동의 예약을 삭제합니다. 만료 시각부터 홍보 대상 조회에서 제외됩니다. 수집동의 증거가 없는 기존 예약은 보관기간을 추측해 채우지 않았으며 별도 정리가 필요합니다. Slack·내려받은 명단·업체 사본은 DB 삭제로 지워지지 않으므로 별도 파기 절차를 운영해야 합니다.

## 발송 시스템 구현 기준

서버에서만 consultation_advertising_targets(p_ctx,p_channel)를 호출합니다. 채널은 phone 또는 sms입니다. 홍보 이용·채널별 동의 증거·철회·만료·정기 확인 안내 기한을 검사하며, 일반 사용자와 익명 사용자는 호출할 수 없습니다. 실제 발송 직전에 다시 조회합니다. 기존 예약 테이블이나 다운로드 명단으로 조건을 우회하지 않습니다.

채널 철회는 해당 *_withdrawn_at에 실제 시각을 저장하며 동의값을 false로 처리합니다. 홍보 이용 철회는 withdrawn_at을 설정하고 파기합니다. 동일 번호의 여러 신청 건에도 수신거부를 함께 반영해야 합니다. 실제 안내 후에만 *_confirmation_sent_at과 다음 확인 기한을 기록하고, 원 동의일부터 2년마다인 주기를 늦추지 않습니다. 기한 경과 시 내부 대상 조회는 보수적으로 발송을 차단합니다. 확인 안내는 재동의나 보관기간 연장이 아닙니다.

광고성 문자에는 광고 표시·발신자 정보·무료 수신거부 등 매체별 필수 요건을 적용합니다. 별도 야간 동의가 없으므로 오후 9시~오전 8시 광고성 문자 발송을 허용하지 않습니다. 상담 회신과 추가 홍보를 구분합니다. 발송 업체·관리자 발송 화면·일괄 철회 화면은 아직 연결하지 않았습니다.

제3자 홍보 업체는 미정입니다. 제공 동의를 받은 것으로 처리하지 않습니다. 업체명·목적·항목·기간·거부권 고지와 별도 동의 후 제공하도록 별도 작업합니다.

## 검증

DB 컬럼 11개 추가와 서버 전용 권한을 확인했습니다. 롤백 테스트로 전화만 동의·문자만 동의·철회·만료·3년 초과·확인 기한 초과·증거 없음·잘못된 채널 차단을 검증했습니다. 호반 v2 문자 저장, v1 호환, 선택 미동의 예약, 만료일 계산, 동일 요청 재처리도 검증했습니다. 가상 데이터는 모두 롤백했고 외부 알림을 보내지 않았습니다.

두 테이블의 RLS를 유지합니다. 새 함수는 SECURITY INVOKER이며 search_path를 고정합니다. 보안 점검의 기존 private 함수 search_path·rls_auto_enable 권한 경고는 이번 변경 범위 밖으로, 전체 보안 검증 완료를 의미하지 않습니다. [점검 설명](https://supabase.com/docs/guides/database/database-linter?lint=0011_function_search_path_mutable)

## 공식 근거

확인일 2026-10-01. [개인정보 보호법 제21조](https://www.law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1034516739), [정보통신망법 제50조](https://law.go.kr/lsLinkCommonInfo.do?chrClsCd=010202&lsJoLnkSeq=1030434423), [시행령 제62조의3](https://www.law.go.kr/LSW/lsSideInfoP.do?docCls=jo&joBrNo=03&joNo=0062&lsiSeq=288033&urlMode=lsScJoRltInfoR).
