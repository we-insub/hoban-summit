import { consentPolicy } from "./consent-policy.ts";
import { legacyConsentPolicy } from "./consent-policy-v1.ts";
const projectUrl = Deno.env.get("SUPABASE_URL")!;
const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const webhook = Deno.env.get("SLACK_HOBAN_WEBHOOK_URL") || Deno.env.get("SLACK_RESERVATION_WEBHOOK_URL") || "";
const defaultOrigins = ["null", "http://127.0.0.1:4173", "http://localhost:4173",
  "https://www.xn--9t4b2d84gm5j2ziyqd.kr", "https://xn--9t4b2d84gm5j2ziyqd.kr",
  "https://mohamoa.com", "https://www.mohamoa.com"];
const origins = new Set([...defaultOrigins, ...(Deno.env.get("RESERVATION_ALLOWED_ORIGINS") || "").split(",").map(x => x.trim()).filter(Boolean)]);
const dbHeaders = { apikey: serviceKey, Authorization: `Bearer ${serviceKey}`, "Content-Type": "application/json" };

Deno.serve(async (req: Request) => {
  const origin = req.headers.get("origin");
  const headers: Record<string, string> = {
    "Content-Type": "application/json", "Cache-Control": "no-store", Vary: "Origin",
    "Access-Control-Allow-Headers": "authorization, apikey, content-type",
    "Access-Control-Allow-Methods": "POST, OPTIONS"
  };
  if (origin && !origins.has(origin)) return new Response('{"error":"허용되지 않은 사이트입니다."}', {status:403,headers});
  if (origin) headers["Access-Control-Allow-Origin"] = origin;
  const reply = (status: number, body: unknown) => new Response(JSON.stringify(body), {status,headers});
  if (req.method === "OPTIONS") return new Response(null, {status:204,headers});
  if (req.method !== "POST") return reply(405, {error:"POST 요청만 지원합니다."});
  let saved = false;
  let reservationId: string | undefined;
  try {
    const raw = await req.text();
    if (new TextEncoder().encode(raw).length > 4096) return reply(413,{error:"입력 내용이 너무 깁니다."});
    const data = JSON.parse(raw);
    const name = typeof data.name === "string" ? data.name.trim() : "";
    const formattedPhone = typeof data.phone === "string" ? data.phone : "";
    const phone = formattedPhone.replace(/-/g, "");
    const visit = typeof data.visitDateTime === "string" ? data.visitDateTime : "";
    const requestId = data.requestId;
    const interest = typeof data.interest === "string" ? data.interest : "";
    const variant = typeof data.sourceVariant === "string" ? data.sourceVariant : "";
    if (!["", "84A", "84B", "117A", "117B", "135"].includes(interest) || !/^(0[1-9]|10)$/.test(variant)) return reply(400,{error:"주택형과 페이지 정보를 확인해주세요."});
    if (data.privacyConsent !== true || data.adultConsent !== true)
      return reply(400,{error:"필수 개인정보 수집·이용 동의와 만 14세 이상 여부를 확인해주세요."});
    const selectedPolicy = data.consentVersion === legacyConsentPolicy.version ? legacyConsentPolicy : consentPolicy;
    if (data.consentVersion !== selectedPolicy.version)
      return reply(409,{error:"동의 안내가 변경되었습니다. 페이지를 새로고침해주세요."});
    const smsAdConsent = selectedPolicy === consentPolicy ? data.smsAdConsent : false;
    if (typeof smsAdConsent !== "boolean" || (smsAdConsent && !data.marketingConsent))
      return reply(400,{error:"문자 수신 동의 내용을 확인해주세요."});
    if (typeof data.marketingConsent !== "boolean" || typeof data.phoneAdConsent !== "boolean"
      || (data.phoneAdConsent && !data.marketingConsent))
      return reply(400,{error:"선택 동의 내용을 확인해주세요."});
    const consent = {privacyConsent:true,adultConsent:true,marketingConsent:data.marketingConsent,
      phoneAdConsent:data.phoneAdConsent,...(selectedPolicy === consentPolicy ? {smsAdConsent} : {}),policy:selectedPolicy};
    if (data.website) return reply(400,{error:"입력을 확인해주세요."});
    if (!/^[가-힣]{1,6}$/.test(name))
      return reply(400,{error:"이름은 한글로 최대 6자까지 입력해주세요."});
    if (!/^[0-9]{3}-[0-9]{4}-[0-9]{4}$/.test(formattedPhone))
      return reply(400,{error:"전화번호는 000-0000-0000 형식으로 입력해주세요."});
    if (typeof requestId !== "string" || !/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(requestId))
      return reply(400,{error:"예약 요청 번호가 올바르지 않습니다."});
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(visit))
      return reply(400,{error:"방문 일시를 선택해주세요."});
    const visitISO = visit + ":00+09:00";
    const date = new Date(visitISO);
    // Reject impossible dates that JavaScript would silently roll into the next month.
    const roundTrip = new Date(date.getTime() + 9*60*60*1000).toISOString().slice(0,16);
    if (roundTrip !== visit || date.getTime() <= Date.now())
      return reply(400,{error:"방문 희망 일시는 현재 이후로 선택해주세요. (한국 시간)"});
    const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
    const digest = await crypto.subtle.digest("SHA-256",new TextEncoder().encode(serviceKey + ":" + ip));
    const submissionKey = Array.from(new Uint8Array(digest)).map(x => x.toString(16).padStart(2,"0")).join("");
    const result = await fetch(projectUrl + "/rest/v1/rpc/submit_hoban_summit_consented",{
      method:"POST",headers:dbHeaders,
      body:JSON.stringify({p_id:requestId,p_name:name,p_phone:phone,p_visit_at:visitISO,
        p_submission_key:submissionKey,p_notifications_enabled:Boolean(webhook),p_consent:consent,p_interest:interest,p_variant:variant})
    });
    if (!result.ok) {
      const failure = await result.json();
      if (failure.message?.includes("rate_limit")) return reply(429,{error:"예약 요청이 많습니다. 잠시 후 다시 시도해주세요."});
      if (failure.message?.includes("request_conflict")) return reply(409,{error:"입력 내용이 변경되었습니다. 새로 제출해주세요."});
      if (failure.message?.includes("past_visit")) return reply(400,{error:"방문 일시는 현재 이후로 선택해주세요."});
      throw new Error("database_save_failed");
    }
    const row = await result.json();
    reservationId = row.id;
    saved = true;
    if (row.is_new && webhook) {
      let notificationStatus = "failed";
      try {
        const slack = await fetch(webhook,{
          method:"POST",headers:{"Content-Type":"application/json"},
          signal:AbortSignal.timeout(5000),
          body:JSON.stringify({
            text:"새 방문 상담 예약 · 호반써밋첨단3지구",
            blocks:[
              {type:"header",text:{type:"plain_text",text:"호반써밋 첨단3지구 방문 상담 예약"}},
              {type:"section",text:{type:"plain_text",
                text:`이름: ${name}\n전화번호: ${formattedPhone}\n방문 희망: ${visit.replace("T"," ")} (한국 시간)\n홍보 이용 동의: ${data.marketingConsent ? "동의" : "미동의"}\n광고성 전화 수신: ${data.phoneAdConsent ? "동의" : "미동의"}\n광고성 문자 수신: ${smsAdConsent ? "동의" : "미동의"}\n관심 주택형: ${interest || "미선택"}\n시안: ${variant}\nctx: 호반써밋첨단3지구\n접수번호: ${row.id}`}}
            ]
          })
        });
        if (slack.ok && (await slack.text()).trim() === "ok") notificationStatus = "sent";
      } catch { /* Booking remains saved if Slack is unavailable. */ }
      try {
        await fetch(projectUrl + "/rest/v1/consultation_requests?id=eq." + row.id,{
          method:"PATCH",headers:dbHeaders,
          body:JSON.stringify({notification_status:notificationStatus,
            notified_at:notificationStatus === "sent" ? new Date().toISOString() : null})
        });
      } catch { /* pending rows can be reviewed by the operator. */ }
    }
    return reply(200,{ok:true,id:row.id});
  } catch (error) {
    if (saved) return reply(200,{ok:true,id:reservationId});
    if (error instanceof SyntaxError || error instanceof RangeError) return reply(400,{error:"입력 내용을 확인해주세요."});
    // Never log contact details, request bodies, or server credentials.
    console.error("Consultation submission failed");
    return reply(503,{error:"접수하지 못했습니다. 잠시 후 다시 시도해주세요."});
  }
});
