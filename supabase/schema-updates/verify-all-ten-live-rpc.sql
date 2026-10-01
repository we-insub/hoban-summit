BEGIN;
DO $$
DECLARE n int; ident text; rid uuid; p text; stamp timestamptz; c jsonb; row_data public.consultation_requests;
BEGIN
 FOR n IN 1..10 LOOP
  ident=lpad(n::text,2,'0'); rid=gen_random_uuid(); p='00000001'||lpad(n::text,3,'0'); stamp=now()+interval '1 day';
  c=jsonb_build_object('privacyConsent',true,'adultConsent',true,'marketingConsent',n%2=0,
   'phoneAdConsent',n%2=0,'smsAdConsent',n%2=0,
   'policy',jsonb_build_object('version','hoban-consent-2026-10-01-v2','marketing',jsonb_build_object('sms','검증용 동의 문구')));
  PERFORM public.submit_hoban_summit_consented(rid,'검증',p,stamp,rid::text,false,c,'135',ident);
  SELECT * INTO row_data FROM public.consultation_requests WHERE id=rid;
  IF row_data.ctx IS DISTINCT FROM '호반써밋첨단3지구'
   OR row_data.privacy_consent IS DISTINCT FROM true OR row_data.adult_consent IS DISTINCT FROM true
   OR row_data.privacy_consent_snapshot IS DISTINCT FROM c
   OR row_data.retention_ends_at IS DISTINCT FROM stamp+interval '90 days'
   OR position('시안: '||ident in row_data.consultation_content)=0
   THEN RAISE EXCEPTION 'variant % request failed',ident; END IF;
  IF n%2=0 THEN
   IF NOT EXISTS(SELECT 1 FROM public.consultation_marketing_contacts WHERE id=rid AND marketing_consent AND phone_ad_consent AND sms_ad_consent AND expires_at=consented_at+interval '3 years')
    THEN RAISE EXCEPTION 'variant % marketing failed',ident; END IF;
  ELSE
   IF EXISTS(SELECT 1 FROM public.consultation_marketing_contacts WHERE id=rid)
    THEN RAISE EXCEPTION 'variant % optional refused but saved',ident; END IF;
  END IF;
  IF (public.submit_hoban_summit_consented(rid,'검증',p,stamp,rid::text,false,c,'135',ident)->>'is_new') IS DISTINCT FROM 'false'
   THEN RAISE EXCEPTION 'variant % duplicate request failed',ident; END IF;
 END LOOP;
END $$;
ROLLBACK;
