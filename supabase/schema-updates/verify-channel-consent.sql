BEGIN;
DO $$
DECLARE test_id uuid:=gen_random_uuid(); n integer;
BEGIN
 INSERT INTO public.consultation_marketing_contacts
 (id,ctx,visitor_name,phone,consented_at,expires_at,phone_ad_consent,consent_version,consent_snapshot)
 VALUES (test_id,'호반써밋첨단3지구','검증','00000000000',now(),now()+interval '3 years',true,'qa-rollback',
 '{"marketingConsent":true,"phoneAdConsent":true}'::jsonb);
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=test_id;
 IF n<>1 THEN RAISE EXCEPTION 'valid phone rejected'; END IF;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','sms') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'legacy phone used for sms'; END IF;
 UPDATE public.consultation_marketing_contacts SET sms_ad_consent=true,sms_ad_consented_at=now(),
 sms_ad_confirmation_due_at=now()+interval '2 years',
 consent_snapshot=consent_snapshot||'{"smsAdConsent":true,"policy":{"marketing":{"sms":"검증용 동의 문구"}}}'::jsonb
 WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','sms') WHERE id=test_id;
 IF n<>1 THEN RAISE EXCEPTION 'explicit sms rejected'; END IF;
 UPDATE public.consultation_marketing_contacts SET sms_ad_withdrawn_at=now() WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','sms') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'withdrawn sms allowed'; END IF;
 UPDATE public.consultation_marketing_contacts SET expires_at=now()-interval '1 second' WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'expired allowed'; END IF;
 UPDATE public.consultation_marketing_contacts SET expires_at=consented_at+interval '4 years' WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'overlong retention allowed'; END IF;
 UPDATE public.consultation_marketing_contacts SET expires_at=consented_at+interval '3 years',
 phone_ad_confirmation_due_at=now()-interval '1 second' WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'overdue confirmation allowed'; END IF;
 UPDATE public.consultation_marketing_contacts SET phone_ad_confirmation_due_at=now()+interval '2 years',
 consent_snapshot='{"marketingConsent":true,"phoneAdConsent":false}'::jsonb WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'missing phone evidence allowed'; END IF;
 UPDATE public.consultation_marketing_contacts SET consent_snapshot='{"marketingConsent":true,"phoneAdConsent":true}'::jsonb,
 withdrawn_at=now() WHERE id=test_id;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','phone') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'withdrawn marketing allowed'; END IF;
 SELECT count(*) INTO n FROM public.consultation_advertising_targets('호반써밋첨단3지구','invalid') WHERE id=test_id;
 IF n<>0 THEN RAISE EXCEPTION 'unknown channel allowed'; END IF;
END $$;
ROLLBACK;
