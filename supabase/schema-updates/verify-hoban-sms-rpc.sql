BEGIN;
DO $$
DECLARE r uuid:=gen_random_uuid(); legacy uuid:=gen_random_uuid(); noad uuid:=gen_random_uuid(); c jsonb; n int;
BEGIN
 c='{"privacyConsent":true,"adultConsent":true,"marketingConsent":true,"phoneAdConsent":false,"smsAdConsent":true,"policy":{"version":"hoban-consent-2026-10-01-v2","marketing":{"sms":"검증용 명시적 문자 동의"}}}'::jsonb;
 PERFORM public.submit_hoban_summit_consented(r,'검증','00000000000',now()+interval '1 day',r::text,false,c,'84A','10');
 SELECT count(*) INTO n FROM public.consultation_requests WHERE id=r AND adult_consent AND privacy_consent AND privacy_consent_version='hoban-consent-2026-10-01-v2' AND retention_ends_at=visit_at+interval '90 days' AND ctx='호반써밋첨단3지구';
 IF n<>1 THEN RAISE EXCEPTION 'request consent/retention failed'; END IF;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','sms') WHERE id=r;
 IF n<>1 THEN RAISE EXCEPTION 'rpc sms consent not stored'; END IF;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=r;
 IF n<>0 THEN RAISE EXCEPTION 'sms consent used for phone'; END IF;
 PERFORM public.submit_hoban_summit_consented(r,'검증','00000000000',(SELECT visit_at FROM public.consultation_requests WHERE id=r),r::text,false,c,'84A','10');
 c='{"privacyConsent":true,"adultConsent":true,"marketingConsent":true,"phoneAdConsent":true,"policy":{"version":"hoban-consent-2026-10-01-v1"}}'::jsonb;
 PERFORM public.submit_hoban_summit_consented(legacy,'검증','00000000001',now()+interval '1 day',legacy::text,false,c,'','01');
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=legacy;
 IF n<>1 THEN RAISE EXCEPTION 'legacy phone compatibility failed'; END IF;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','sms') WHERE id=legacy;
 IF n<>0 THEN RAISE EXCEPTION 'legacy sms allowed'; END IF;
 c='{"privacyConsent":true,"adultConsent":true,"marketingConsent":false,"phoneAdConsent":false,"smsAdConsent":false,"policy":{"version":"hoban-consent-2026-10-01-v2"}}'::jsonb;
 PERFORM public.submit_hoban_summit_consented(noad,'검증','00000000002',now()+interval '1 day',noad::text,false,c,'','03');
 IF EXISTS(SELECT 1 FROM public.consultation_marketing_contacts WHERE id=noad) THEN RAISE EXCEPTION 'nonmarketing contact stored'; END IF;
END $$;
ROLLBACK;
