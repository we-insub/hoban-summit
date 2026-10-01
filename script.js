const menuToggle = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('.mobile-menu');
const scrollTopButton = document.querySelector('.scroll-top');
const reservationModal = document.querySelector('.reservation-modal');
const reservationForm = document.querySelector('.reservation-form');
const modalCloseButton = document.querySelector('.modal-close');

menuToggle.addEventListener('click', () => {
  const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
  menuToggle.setAttribute('aria-expanded', String(!isOpen));
  menuToggle.querySelector('.sr-only').textContent = isOpen ? '메뉴 열기' : '메뉴 닫기';
  mobileMenu.hidden = isOpen;
});

mobileMenu.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.querySelector('.sr-only').textContent = '메뉴 열기';
    mobileMenu.hidden = true;
  });
});

window.addEventListener('scroll', () => {
  scrollTopButton.classList.toggle('is-visible', window.scrollY > 500);
}, { passive: true });

scrollTopButton.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

const closeReservationModal = () => reservationModal.classList.remove('is-open');

modalCloseButton.addEventListener('click', closeReservationModal);

reservationModal.addEventListener('click', (event) => {
  if (event.target === reservationModal) closeReservationModal();
});

const reservationStatus = document.querySelector('.reservation-status');
const reservationSubmit = document.querySelector('.reservation-submit');
const consentPolicy = window.CONSENT_POLICY;
const renderConsent = (container, entries) => {
  entries.forEach(([label, value]) => {
    const paragraph = document.createElement('p');
    const strong = document.createElement('strong');
    strong.textContent = `${label}: `;
    paragraph.append(strong, document.createTextNode(value));
    container.append(paragraph);
  });
};
renderConsent(document.querySelector('#required-consent-details'), [
  ['처리자', `${consentPolicy.controller} · 사업자등록번호 ${consentPolicy.businessNumber}`],
  ['문의·동의 철회', consentPolicy.contact], ['목적', consentPolicy.required.purpose],
  ['항목', consentPolicy.required.items], ['보유기간', consentPolicy.required.retention],
  ['거부권', consentPolicy.required.refusal], ['처리 서비스', consentPolicy.processors]
]);
renderConsent(document.querySelector('#marketing-consent-details'), [
  ['목적', consentPolicy.marketing.purpose], ['항목', consentPolicy.marketing.items],
  ['보유기간', consentPolicy.marketing.retention], ['거부권', consentPolicy.marketing.refusal],
  ['광고성 전화', consentPolicy.marketing.phone], ...(consentPolicy.marketing.sms ? [['광고성 문자', consentPolicy.marketing.sms]] : []), ['문의·철회', consentPolicy.contact]
]);
const marketingInput = reservationForm.elements.marketingConsent;
const phoneAdInput = reservationForm.elements.phoneAdConsent;
const smsAdInput = reservationForm.elements.smsAdConsent;
const updatePhoneAdChoice = () => {
  phoneAdInput.disabled = !marketingInput.checked;
  if (!marketingInput.checked) phoneAdInput.checked = false;
  if (smsAdInput) { smsAdInput.disabled = !marketingInput.checked; if (!marketingInput.checked) smsAdInput.checked = false; }
};
marketingInput.addEventListener('change', updatePhoneAdChoice);
let pendingRequest = null;
let submitting = false;
const nameInput = reservationForm.elements.name;
const phoneInput = reservationForm.elements.phone;
const visitInput = reservationForm.elements.visitDateTime;
const cleanName = () => {
  nameInput.value = nameInput.value.normalize('NFC').replace(/[^가-힣]/g, '').slice(0, 6);
};
nameInput.addEventListener('input', (event) => { if (!event.isComposing) cleanName(); });
nameInput.addEventListener('compositionend', cleanName);
phoneInput.addEventListener('input', () => {
  const digitsBeforeCaret = phoneInput.value.slice(0, phoneInput.selectionStart).replace(/[^0-9]/g, '').length;
  const digits = phoneInput.value.replace(/[^0-9]/g, '').slice(0, 11);
  phoneInput.value = digits.length > 7 ? `${digits.slice(0, 3)}-${digits.slice(3, 7)}-${digits.slice(7)}`
    : digits.length > 3 ? `${digits.slice(0, 3)}-${digits.slice(3)}` : digits;
  let caret = 0;
  let seen = 0;
  while (caret < phoneInput.value.length && seen < digitsBeforeCaret) {
    if (/[0-9]/.test(phoneInput.value[caret])) seen++;
    caret++;
  }
  phoneInput.setSelectionRange(caret, caret);
});
const refreshVisitMinimum = () => {
  // datetime-local has no timezone. Always show and validate Korean time.
  const nextMinute = (Math.floor(Date.now() / 60000) + 1) * 60000;
  visitInput.min = new Date(nextMinute + 9 * 3600000).toISOString().slice(0, 16);
  visitInput.setCustomValidity(visitInput.value && visitInput.value < visitInput.min
    ? '방문 일시는 현재 이후로 선택해주세요. (한국 시간)' : '');
};
refreshVisitMinimum();
visitInput.addEventListener('focus', refreshVisitMinimum);
visitInput.addEventListener('input', refreshVisitMinimum);
setInterval(refreshVisitMinimum, 30000);

reservationForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submitting) return;
  refreshVisitMinimum();
  if (!reservationForm.reportValidity()) return;
  const values = new FormData(reservationForm);
  const payload = {
    name: String(values.get('name')).trim(),
    phone: String(values.get('phone')),
    visitDateTime: String(values.get('visitDateTime')),
    privacyConsent: values.get('privacyConsent') === 'on',
    adultConsent: values.get('adultConsent') === 'on',
    marketingConsent: values.get('marketingConsent') === 'on',
    phoneAdConsent: values.get('phoneAdConsent') === 'on',
    ...(consentPolicy.marketing.sms ? {smsAdConsent: values.get('smsAdConsent') === 'on'} : {}),
    consentVersion: consentPolicy.version,
    interest: String(values.get('interest') || ''),
    sourceVariant: String(window.RESERVATION_CONFIG?.sourceVariant || ''),
    website: String(values.get('website') || '')
  };
  reservationStatus.classList.remove('is-error');
  if (!/^[가-힣]{1,6}$/.test(payload.name) || !/^[0-9]{3}-[0-9]{4}-[0-9]{4}$/.test(payload.phone)) {
    reservationStatus.textContent = '이름은 한글 6자 이내, 전화번호는 숫자 11자리로 입력해주세요.';
    reservationStatus.classList.add('is-error');
    return;
  }
  const fingerprint = JSON.stringify(payload);
  if (window.RESERVATION_CONFIG?.previewMode) {
    reservationStatus.textContent = '시안에서 입력을 확인했습니다. 실제 예약·DB 저장·알림 전송은 하지 않았습니다.';
    alert(`이름: ${payload.name}\n전화번호: ${payload.phone}\n방문 일시: ${payload.visitDateTime.replace('T', ' ')}\n\n시안 확인용입니다. 실제 예약은 접수되지 않았습니다.`);
    return;
  }
  if (!pendingRequest || pendingRequest.fingerprint !== fingerprint) {
    pendingRequest = { fingerprint, id: crypto.randomUUID() };
  }
  submitting = true;
  reservationSubmit.disabled = true;
  reservationSubmit.textContent = '접수 중…';
  reservationStatus.textContent = '';
  try {
    const config = window.RESERVATION_CONFIG;
    const response = await fetch(config.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: config.anonKey, Authorization: `Bearer ${config.anonKey}` },
      body: JSON.stringify({ ...payload, requestId: pendingRequest.id }),
      signal: AbortSignal.timeout(20000)
    });
    const result = await response.json();
    if (!response.ok || !result.ok || !result.id) {
      if (response.status === 409) pendingRequest = null;
      throw new Error(result.error || '접수하지 못했습니다. 잠시 후 다시 시도해주세요.');
    }
    reservationForm.reset();
    updatePhoneAdChoice();
    pendingRequest = null;
    reservationStatus.textContent = '상담 예약 신청이 접수되었습니다. 방문 일정은 상담 후 확정됩니다.';
  } catch (error) {
    reservationStatus.classList.add('is-error');
    reservationStatus.textContent = error.name === 'TimeoutError' || error instanceof TypeError
      ? '접수 결과를 확인하지 못했습니다. 인터넷 연결을 확인하고 다시 눌러주세요.'
      : error.message;
  } finally {
    submitting = false;
    reservationSubmit.disabled = false;
    reservationSubmit.textContent = '예약';
  }
});
