-- Add channel-specific consent controls without treating old telephone consent as SMS consent.
ALTER TABLE public.consultation_marketing_contacts
 ADD COLUMN marketing_consent boolean NOT NULL DEFAULT false,
 ADD COLUMN phone_ad_consented_at timestamptz,
 ADD COLUMN phone_ad_withdrawn_at timestamptz,
 ADD COLUMN phone_ad_confirmation_sent_at timestamptz,
 ADD COLUMN phone_ad_confirmation_due_at timestamptz,
 ADD COLUMN sms_ad_consent boolean NOT NULL DEFAULT false,
 ADD COLUMN sms_ad_consented_at timestamptz,
 ADD COLUMN sms_ad_withdrawn_at timestamptz,
 ADD COLUMN sms_ad_confirmation_sent_at timestamptz,
 ADD COLUMN sms_ad_confirmation_due_at timestamptz;
ALTER TABLE public.consultation_requests ADD COLUMN adult_consent boolean;

UPDATE public.consultation_requests SET adult_consent =
 CASE WHEN privacy_consent_snapshot->>'adultConsent'='true' THEN true
      WHEN privacy_consent_snapshot->>'adultConsent'='false' THEN false ELSE NULL END WHERE privacy_consent_snapshot IS NOT NULL;
UPDATE public.consultation_marketing_contacts SET
 marketing_consent = coalesce(consent_snapshot->>'marketingConsent'='true',false),
 phone_ad_consented_at = CASE WHEN phone_ad_consent AND consent_snapshot->>'phoneAdConsent'='true' THEN consented_at ELSE NULL END,
 phone_ad_confirmation_due_at = CASE WHEN phone_ad_consent AND consent_snapshot->>'phoneAdConsent'='true' THEN consented_at+interval '2 years' ELSE NULL END;
-- SMS remains false for every legacy record, regardless of telephone consent.

CREATE FUNCTION public.normalize_consultation_channel_consent() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path='' AS $$
BEGIN
 IF TG_OP='INSERT' THEN
  NEW.marketing_consent=coalesce(NEW.consent_snapshot->>'marketingConsent'='true',false);
  IF NEW.phone_ad_consent AND NEW.consent_snapshot->>'phoneAdConsent'='true' THEN
   NEW.phone_ad_consented_at=NEW.consented_at;
   NEW.phone_ad_confirmation_due_at=NEW.consented_at+interval '2 years';
  END IF;
  -- Future trusted submission endpoints must supply explicit SMS consent and its displayed policy.
  IF NEW.sms_ad_consent AND NEW.consent_snapshot->>'smsAdConsent'='true'
     AND nullif(NEW.consent_snapshot#>>'{policy,marketing,sms}','') IS NOT NULL THEN
   NEW.sms_ad_consented_at=NEW.consented_at;
   NEW.sms_ad_confirmation_due_at=NEW.consented_at+interval '2 years';
  ELSE
   NEW.sms_ad_consent=false;
   NEW.sms_ad_consented_at=NULL;
   NEW.sms_ad_confirmation_due_at=NULL;
  END IF;
 END IF;
 IF NEW.withdrawn_at IS NOT NULL THEN NEW.marketing_consent=false; END IF;
 IF NEW.phone_ad_withdrawn_at IS NOT NULL THEN NEW.phone_ad_consent=false; END IF;
 IF NEW.sms_ad_withdrawn_at IS NOT NULL THEN NEW.sms_ad_consent=false; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER consultation_channel_consent_before_write
 BEFORE INSERT OR UPDATE ON public.consultation_marketing_contacts
 FOR EACH ROW EXECUTE FUNCTION public.normalize_consultation_channel_consent();
REVOKE ALL ON FUNCTION public.normalize_consultation_channel_consent() FROM PUBLIC,anon,authenticated;

CREATE FUNCTION public.normalize_consultation_adult_consent() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path='' AS $$
BEGIN
 NEW.adult_consent=CASE WHEN NEW.privacy_consent_snapshot->>'adultConsent'='true' THEN true
 WHEN NEW.privacy_consent_snapshot->>'adultConsent'='false' THEN false ELSE NULL END;
 RETURN NEW;
END $$;
CREATE TRIGGER consultation_adult_consent_before_write
 BEFORE INSERT OR UPDATE OF privacy_consent_snapshot ON public.consultation_requests
 FOR EACH ROW EXECUTE FUNCTION public.normalize_consultation_adult_consent();
REVOKE ALL ON FUNCTION public.normalize_consultation_adult_consent() FROM PUBLIC,anon,authenticated;

-- Internal service-only selector. Recheck immediately before each actual send.
CREATE FUNCTION public.consultation_advertising_targets(p_ctx text,p_channel text)
 RETURNS TABLE(id uuid,ctx text,visitor_name text,phone text,expires_at timestamptz)
 LANGUAGE sql STABLE SECURITY INVOKER SET search_path='' AS $$
 SELECT m.id,m.ctx,m.visitor_name,m.phone,m.expires_at
 FROM public.consultation_marketing_contacts m
 WHERE m.ctx=p_ctx AND m.marketing_consent AND m.withdrawn_at IS NULL
 AND m.consent_snapshot->>'marketingConsent'='true'
 AND m.expires_at>now() AND m.expires_at<=m.consented_at+interval '3 years'
 AND CASE p_channel
 WHEN 'phone' THEN m.phone_ad_consent AND m.phone_ad_withdrawn_at IS NULL
  AND m.consent_snapshot->>'phoneAdConsent'='true' AND m.phone_ad_consented_at IS NOT NULL
  AND m.phone_ad_confirmation_due_at>now()
 WHEN 'sms' THEN m.sms_ad_consent AND m.sms_ad_withdrawn_at IS NULL
  AND m.consent_snapshot->>'smsAdConsent'='true' AND m.sms_ad_consented_at IS NOT NULL
  AND nullif(m.consent_snapshot#>>'{policy,marketing,sms}','') IS NOT NULL
  AND m.sms_ad_confirmation_due_at>now()
 ELSE false END
 $$;
REVOKE ALL ON FUNCTION public.consultation_advertising_targets(text,text) FROM PUBLIC,anon,authenticated;
GRANT EXECUTE ON FUNCTION public.consultation_advertising_targets(text,text) TO service_role;
COMMENT ON COLUMN public.consultation_marketing_contacts.expires_at IS '현재 고지된 홍보 보관 만료일: 동의일부터 최대 3년. 법정 일괄 허용기간이 아님. 목적 달성·철회 시 먼저 파기.';
COMMENT ON COLUMN public.consultation_marketing_contacts.sms_ad_consent IS '명시적 광고성 문자 동의. 기존 광고성 전화 동의로 대체하거나 소급 설정하지 않음.';
COMMENT ON COLUMN public.consultation_marketing_contacts.phone_ad_confirmation_due_at IS '2년 주기 수신동의 확인 안내 기한. 안내는 재동의·보관기간 연장이 아님. 미처리 기한 경과 시 내부 대상 조회에서 제외.';
