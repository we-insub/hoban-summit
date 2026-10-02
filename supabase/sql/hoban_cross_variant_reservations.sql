CREATE OR REPLACE FUNCTION public.submit_hoban_summit_consented(p_id uuid, p_name text, p_phone text, p_visit_at timestamp with time zone, p_submission_key text, p_notifications_enabled boolean, p_consent jsonb, p_interest text, p_variant text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SET search_path TO ''
AS $function$
DECLARE existing public.consultation_requests; content text;
BEGIN
 IF p_consent->>'privacyConsent' IS DISTINCT FROM 'true'
 OR p_consent->>'adultConsent' IS DISTINCT FROM 'true'
 OR COALESCE(p_consent->'policy'->>'version','') NOT IN ('hoban-consent-2026-10-01-v1','hoban-consent-2026-10-01-v2')
 THEN RAISE EXCEPTION 'consent_required'; END IF;
 IF (p_consent->>'phoneAdConsent'='true' OR p_consent->>'smsAdConsent'='true') AND p_consent->>'marketingConsent' IS DISTINCT FROM 'true'
 THEN RAISE EXCEPTION 'marketing_consent_required'; END IF;
 IF p_interest IS NULL OR p_interest NOT IN ('','84A','84B','117A','117B','135')
 OR p_variant IS NULL OR p_variant NOT IN ('01','02','03','04','05','06','07','08','09','10') THEN RAISE EXCEPTION 'invalid_selection'; END IF;
 content := '호반써밋 첨단3지구 방문 상담 신청' || chr(10) ||
 '관심 주택형: ' || COALESCE(NULLIF(p_interest,''),'미선택') || chr(10) ||
 '시안: ' || p_variant || chr(10) || '방문 희망 일시: ' ||
 to_char(p_visit_at AT TIME ZONE 'Asia/Seoul','YYYY-MM-DD HH24:MI') || ' (한국 시간)';
 PERFORM pg_advisory_xact_lock(hashtextextended(p_phone,0));
 PERFORM pg_advisory_xact_lock(hashtextextended(p_submission_key,1));
 PERFORM pg_advisory_xact_lock(hashtextextended(p_id::text,2));
 SELECT * INTO existing FROM public.consultation_requests WHERE id=p_id;
 IF FOUND THEN
  IF existing.ctx <> '호반써밋첨단3지구' OR existing.visitor_name <> p_name
  OR existing.phone <> p_phone OR existing.visit_at <> p_visit_at
  OR existing.consultation_content <> content OR existing.privacy_consent_snapshot IS DISTINCT FROM p_consent
  THEN RAISE EXCEPTION 'request_conflict'; END IF;
  RETURN jsonb_build_object('id',p_id,'is_new',false);
 END IF;
 IF (SELECT count(*) FROM public.consultation_requests WHERE ctx='호반써밋첨단3지구' AND phone=p_phone AND position(chr(10) || '시안: ' || p_variant || chr(10) in consultation_content)>0 AND created_at>now()-interval '1 hour') >= 3
 OR (SELECT count(*) FROM public.consultation_requests WHERE submission_key=p_submission_key AND created_at>now()-interval '1 hour') >= 30
 THEN RAISE EXCEPTION 'rate_limit'; END IF;
 IF p_visit_at <= now() THEN RAISE EXCEPTION 'past_visit'; END IF;
 INSERT INTO public.consultation_requests
 (id,ctx,model_house_id,visitor_name,phone,visit_at,consultation_content,submission_key,notification_status,
 privacy_consent,privacy_consent_at,privacy_consent_version,privacy_consent_snapshot,retention_ends_at)
 VALUES (p_id,'호반써밋첨단3지구',
 CASE WHEN p_interest IN ('84A','84B') THEN (SELECT id FROM public.model_houses WHERE slug='cheomdan3-a7-hoban-summit' ORDER BY id LIMIT 1) ELSE NULL END,
 p_name,p_phone,p_visit_at,content,p_submission_key,
 CASE WHEN p_notifications_enabled THEN 'pending' ELSE 'awaiting_configuration' END,
 true,now(),p_consent->'policy'->>'version',p_consent,p_visit_at+interval '90 days');
 IF p_consent->>'marketingConsent'='true' THEN
 INSERT INTO public.consultation_marketing_contacts
 (id,ctx,visitor_name,phone,expires_at,phone_ad_consent,sms_ad_consent,consent_version,consent_snapshot)
 VALUES (p_id,'호반써밋첨단3지구',p_name,p_phone,now()+interval '3 years',
 (p_consent->>'phoneAdConsent')::boolean,
 (p_consent->'policy'->>'version'='hoban-consent-2026-10-01-v2' AND coalesce(p_consent->>'smsAdConsent'='true',false)),
 p_consent->'policy'->>'version',p_consent);
 END IF;
 RETURN jsonb_build_object('id',p_id,'is_new',true);
END;
$function$;
