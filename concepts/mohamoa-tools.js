/* 평수 변환기·청약 가점 계산기·대출 상환 계산기. Mohamoa 원본 계산식을 옮겼고 입력값은 브라우저 안에서만 쓰며 저장·전송하지 않는다. */
(() => {
  const el = (tag, attrs = {}, ...kids) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') node.className = v; else if (k.startsWith('on')) node.addEventListener(k.slice(2), v); else if (v !== false && v != null) node.setAttribute(k, v === true ? '' : v);
    }
    kids.flat().forEach(kid => node.append(kid instanceof Node ? kid : document.createTextNode(kid)));
    return node;
  };
  const field = (label, input, unit, note) => el('label', { class: 'pyeong-field' }, el('span', {}, label), el('div', {}, input, unit ? el('em', {}, unit) : ''), note ? el('small', {}, note) : '');


  // ---- 결과 저장 (PNG·PDF). 외부 라이브러리 없이 canvas로 그리며 저장하는 값은 사용자의 브라우저 밖으로 나가지 않는다. ----
  const WIDTH = 900, PAD = 48, FONT = '"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",sans-serif';
  const wrap = (ctx, text, maxWidth) => {
    const lines = []; let line = '';
    for (const char of text) { if (ctx.measureText(line + char).width > maxWidth && line) { lines.push(line); line = char === ' ' ? '' : char; } else line += char; }
    if (line) lines.push(line);
    return lines;
  };
  function renderResultCanvas(spec) {
    const canvas = document.createElement('canvas'), measure = canvas.getContext('2d');
    const rows = spec.rows || [], notes = spec.notes || [];
    measure.font = `400 22px ${FONT}`;
    const noteLines = notes.flatMap(note => wrap(measure, note, WIDTH - PAD * 2));
    const height = 190 + (spec.headline ? 150 : 0) + rows.length * 56 + (rows.length ? 24 : 0) + noteLines.length * 34 + 120;
    canvas.width = WIDTH; canvas.height = height;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fffaf1'; ctx.fillRect(0, 0, WIDTH, height);
    ctx.fillStyle = '#071a32'; ctx.fillRect(0, 0, WIDTH, 14);
    ctx.fillStyle = '#80591f'; ctx.font = `700 24px ${FONT}`; ctx.fillText('호반써밋 첨단3지구 계산 결과', PAD, 74);
    ctx.fillStyle = '#071a32'; ctx.font = `800 36px ${FONT}`;
    let y = 130;
    for (const line of wrap(ctx, spec.title, WIDTH - PAD * 2)) { ctx.fillText(line, PAD, y); y += 46; }
    y += 8;
    if (spec.headline) {
      ctx.fillStyle = '#10243b'; ctx.fillRect(PAD, y, WIDTH - PAD * 2, 124);
      ctx.fillStyle = '#c9a15f'; ctx.font = `700 22px ${FONT}`; ctx.fillText(spec.headline.label, PAD + 28, y + 42);
      ctx.fillStyle = '#f8fafc'; ctx.font = `800 ${spec.headline.value.length > 18 ? 34 : 52}px ${FONT}`; ctx.fillText(spec.headline.value, PAD + 28, y + 100);
      y += 150;
    }
    ctx.font = `500 26px ${FONT}`;
    for (const row of rows) {
      ctx.fillStyle = '#334155'; ctx.textAlign = 'left'; ctx.fillText(row.label, PAD, y + 34);
      ctx.fillStyle = '#071a32'; ctx.font = `700 26px ${FONT}`; ctx.textAlign = 'right'; ctx.fillText(row.value, WIDTH - PAD, y + 34);
      ctx.font = `500 26px ${FONT}`; ctx.textAlign = 'left';
      ctx.strokeStyle = '#e2d6bf'; ctx.beginPath(); ctx.moveTo(PAD, y + 50); ctx.lineTo(WIDTH - PAD, y + 50); ctx.stroke();
      y += 56;
    }
    y += rows.length ? 24 : 0;
    ctx.fillStyle = '#64748b'; ctx.font = `400 22px ${FONT}`;
    for (const line of noteLines) { ctx.fillText(line, PAD, y + 24); y += 34; }
    ctx.fillStyle = '#80591f'; ctx.font = `600 22px ${FONT}`;
    ctx.fillText('참고용 모의 계산입니다 · 호반써밋 첨단3지구 모델하우스 안내', PAD, height - 48);
    return canvas;
  }
  const saveBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  function buildSinglePagePdf(jpeg, imageWidth, imageHeight) {
    const pageWidth = 595, pageHeight = 842, margin = 40, drawWidth = pageWidth - margin * 2;
    const drawHeight = Math.min(pageHeight - margin * 2, (drawWidth * imageHeight) / imageWidth), drawY = pageHeight - margin - drawHeight;
    const encoder = new TextEncoder(), chunks = [], offsets = []; let length = 0;
    const push = data => { const bytes = typeof data === 'string' ? encoder.encode(data) : data; chunks.push(bytes); length += bytes.length; };
    const object = (id, body, stream) => { offsets[id] = length; push(`${id} 0 obj\n${body}`); if (stream) { push('\nstream\n'); push(stream); push('\nendstream'); } push('\nendobj\n'); };
    push('%PDF-1.4\n');
    object(1, '<< /Type /Catalog /Pages 2 0 R >>');
    object(2, '<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
    object(3, `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>`);
    const content = encoder.encode(`q ${drawWidth.toFixed(2)} 0 0 ${drawHeight.toFixed(2)} ${margin} ${drawY.toFixed(2)} cm /Im0 Do Q`);
    object(4, `<< /Length ${content.length} >>`, content);
    object(5, `<< /Type /XObject /Subtype /Image /Width ${imageWidth} /Height ${imageHeight} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>`, jpeg);
    const xrefAt = length;
    push(`xref\n0 6\n0000000000 65535 f \n${[1, 2, 3, 4, 5].map(id => `${String(offsets[id]).padStart(10, '0')} 00000 n \n`).join('')}`);
    push(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xrefAt}\n%%EOF\n`);
    const out = new Uint8Array(length); let position = 0;
    for (const chunk of chunks) { out.set(chunk, position); position += chunk.length; }
    return out;
  }
  const downloadImage = spec => renderResultCanvas(spec).toBlob(blob => { if (blob) saveBlob(blob, `${spec.filename}.png`); }, 'image/png');
  const downloadPdf = spec => {
    const canvas = renderResultCanvas(spec);
    canvas.toBlob(async blob => {
      if (!blob) return;
      const pdf = buildSinglePagePdf(new Uint8Array(await blob.arrayBuffer()), canvas.width, canvas.height);
      saveBlob(new Blob([pdf], { type: 'application/pdf' }), `${spec.filename}.pdf`);
    }, 'image/jpeg', 0.92);
  };
  // getSpec()가 null이면 저장 버튼을 잠근다.
  function exportButtons(getSpec) {
    const image = el('button', { type: 'button', onclick: () => { const spec = getSpec(); if (spec) downloadImage(spec); } }, '이미지 저장');
    const pdf = el('button', { type: 'button', onclick: () => { const spec = getSpec(); if (spec) downloadPdf(spec); } }, 'PDF 저장');
    const group = el('div', { class: 'result-export', role: 'group', 'aria-label': '계산 결과 저장' }, image, pdf);
    group.refresh = () => { const disabled = !getSpec(); image.disabled = disabled; pdf.disabled = disabled; };
    return group;
  }
  window.HobanResultExport = { renderResultCanvas, buildSinglePagePdf, exportButtons };

  // ---- 평수 변환 ----
  const sqmToPyeong = sqm => (sqm * 121) / 400;
  const pyeongToSqm = pyeong => (pyeong * 400) / 121;
  const fmt = (value, digits) => value.toFixed(digits).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
  const parsePositive = text => { const v = Number(String(text).replaceAll(',', '').trim()); return Number.isFinite(v) && v > 0 ? v : null; };

  function pyeong(root) {
    const areas = (root.dataset.areas || '59,74,84,102,114,135').split(',').map(Number);
    const sqm = el('input', { inputmode: 'decimal', 'aria-label': '제곱미터', value: '84' });
    const py = el('input', { inputmode: 'decimal', 'aria-label': '평', value: fmt(sqmToPyeong(84), 2) });
    const supply = el('input', { inputmode: 'decimal', placeholder: '예: 112.4', 'aria-label': '공급면적' });
    const quick = el('div', { class: 'pyeong-quick', role: 'group', 'aria-label': '자주 보는 전용면적' });
    const result = el('div', { class: 'pyeong-result', role: 'status', 'aria-live': 'polite' });
    const exporter = exportButtons(() => {
      const s = parsePositive(sqm.value), sp = parsePositive(supply.value);
      if (!s) return null;
      return { title: '아파트 평수 변환', headline: { label: '변환 결과', value: `${fmt(s, 2)}㎡ = ${fmt(sqmToPyeong(s), 2)}평` },
        rows: [{ label: '전용 기준 평수', value: `${fmt(sqmToPyeong(s), 1)}평` }, ...(sp ? [{ label: `공급면적 ${fmt(sp, 2)}㎡`, value: `약 ${fmt(sqmToPyeong(sp), 1)}평형` }] : [])],
        notes: ['1평 = 400/121㎡(약 3.3058㎡)로 계산했습니다.', '분양 광고의 평형은 대개 공급면적 기준이므로 해당 단지 모집공고의 공급면적으로 확인해 주세요.'], filename: `hoban-pyeong-${fmt(s, 1)}` };
    });
    const buttons = areas.map(area => { const b = el('button', { type: 'button', onclick: () => { sqm.value = String(area); fromSqm(); } }, area + '㎡'); quick.append(b); return [area, b]; });
    function render() {
      const s = parsePositive(sqm.value), sp = parsePositive(supply.value);
      buttons.forEach(([area, b]) => b.setAttribute('aria-pressed', String(s === area)));
      exporter.refresh();
      result.replaceChildren(el('p', { class: 'pyeong-result-label' }, '변환 결과'));
      if (!s) { result.append(el('strong', {}, '숫자를 입력해 주세요')); return; }
      result.append(el('strong', {}, `${fmt(s, 2)}㎡ = ${fmt(sqmToPyeong(s), 2)}평`), el('p', {}, `전용 기준 ${fmt(sqmToPyeong(s), 1)}평`));
      if (sp) result.append(el('p', {}, `공급면적 ${fmt(sp, 2)}㎡ ≈ `, el('b', {}, `${fmt(sqmToPyeong(sp), 1)}평형`)));
    }
    function fromSqm() { const s = parsePositive(sqm.value); py.value = s ? fmt(sqmToPyeong(s), 2) : ''; render(); }
    function fromPyeong() { const p = parsePositive(py.value); sqm.value = p ? fmt(pyeongToSqm(p), 2) : ''; render(); }
    sqm.addEventListener('input', fromSqm); py.addEventListener('input', fromPyeong); supply.addEventListener('input', render);
    root.replaceChildren(el('section', { class: 'pyeong-card', 'aria-label': '평수 변환기' },
      el('div', { class: 'pyeong-row' }, field('제곱미터', sqm, '㎡'), field('평', py, '평')), quick,
      el('div', { class: 'pyeong-field pyeong-supply' }, field('공급면적 입력 (선택)', supply, '㎡', '모집공고에 적힌 공급면적을 넣으면 아파트에서 부르는 평형도 함께 알려 드립니다.')),
      result, exporter,
      el('p', { class: 'pyeong-note' }, '※ 평수는 ㎡에 0.3025를 곱해 구합니다(1평 = 400/121㎡). 분양 광고에서 말하는 평형은 대개 공급면적을 평으로 바꾼 값이어서, 전용면적을 바꾼 평수보다 크게 나옵니다.')));
    render();
  }

  // ---- 청약 가점 ----
  const rangeLabel = year => (year === 1 ? '1년 미만' : `${year - 1}년 이상 ~ ${year}년 미만`);
  const homelessOptions = [{ label: '무주택자 아님 (주택 소유)', score: 0 }, ...Array.from({ length: 15 }, (_, i) => ({ label: rangeLabel(i + 1), score: (i + 1) * 2 })), { label: '15년 이상', score: 32 }];
  const dependentOptions = [...Array.from({ length: 6 }, (_, i) => ({ label: `${i}명`, score: 5 + i * 5 })), { label: '6명 이상', score: 35 }];
  const accountOptions = [{ label: '6개월 미만', score: 1 }, { label: '6개월 이상 ~ 1년 미만', score: 2 }, ...Array.from({ length: 14 }, (_, i) => ({ label: rangeLabel(i + 2), score: i + 3 })), { label: '15년 이상', score: 17 }];
  const MAX = { homeless: 32, dependents: 35, account: 17, total: 84 };

  function score(root) {
    const select = (options, label) => { const s = el('select', { 'aria-label': label }, options.map((o, i) => el('option', { value: i }, o.label))); s.addEventListener('change', render); return s; };
    const sh = select(homelessOptions, '무주택기간'), sd = select(dependentOptions, '부양가족 수'), sa = select(accountOptions, '청약통장 가입기간');
    const result = el('div', { class: 'score-result', role: 'status', 'aria-live': 'polite' });
    const parts = () => [['무주택기간', homelessOptions[sh.value], MAX.homeless], ['부양가족', dependentOptions[sd.value], MAX.dependents], ['청약통장', accountOptions[sa.value], MAX.account]];
    const exporter = exportButtons(() => {
      const rows = parts(), total = rows.reduce((sum, row) => sum + row[1].score, 0);
      return { title: '청약 가점 계산', headline: { label: '계산된 청약 가점', value: `${total} / ${MAX.total}점` },
        rows: rows.map(([name, option, max]) => ({ label: `${name} (${option.label})`, value: `${option.score} / ${max}점` })),
        notes: ['점수표만 적용한 참고용 계산입니다. 세부 인정 요건은 입주자모집공고와 청약홈에서 확인해 주세요.'], filename: `hoban-subscription-score-${total}` };
    });
    function render() {
      exporter.refresh();
      const rows = [['무주택기간', homelessOptions[sh.value].score, MAX.homeless], ['부양가족', dependentOptions[sd.value].score, MAX.dependents], ['청약통장', accountOptions[sa.value].score, MAX.account]];
      const total = rows.reduce((sum, row) => sum + row[1], 0);
      const bars = el('ul', {}, rows.map(([name, value, max]) => { const bar = el('i', {}); bar.style.width = `${(value / max) * 100}%`; return el('li', {}, el('span', {}, name), el('div', { class: 'score-bar', 'aria-hidden': 'true' }, bar), el('b', {}, `${value} / ${max}`)); }));
      result.replaceChildren(el('p', { class: 'score-result-label' }, '계산된 청약 가점'), el('strong', {}, `${total} `, el('span', {}, `/ ${MAX.total}점`)), bars);
    }
    const group = (title, note, control) => el('label', { class: 'score-field' }, el('span', {}, title, el('small', {}, note)), control);
    root.replaceChildren(el('section', { class: 'score-card', 'aria-label': '청약 가점 계산기' },
      el('div', { class: 'score-grid' }, group('무주택기간', '만 30세부터 센 기간, 30세 전에 혼인했다면 혼인신고일부터 · 최대 32점', sh), group('부양가족 수', '본인을 뺀 인원 · 최대 35점', sd), group('청약통장 가입기간', '최대 17점', sa)),
      el('p', { class: 'score-note' }, '※ 점수표만 적용한 참고용 계산입니다. 배우자 통장 가입기간의 반영 여부와 부양가족으로 인정되는 범위는 입주자모집공고와 청약홈(applyhome.co.kr)에서 확인해 주세요.'),
      result, exporter,
      el('p', { class: 'score-cta-text' }, '가점제로 당첨되는 점수는 단지와 주택형마다 다릅니다. 관심 단지의 분양 조건이 궁금하시면 방문 상담으로 문의해 주세요.'),
      el('div', { class: 'score-actions' }, el('a', { class: 'score-consult', href: 'tel:16005184' }, '전화 상담 1600-5184'))));
    render();
  }

  // ---- 대출 상환 ----
  const methodLabels = { annuity: '원리금균등', principal: '원금균등', bullet: '만기일시' };
  const methods = Object.keys(methodLabels);
  const limits = { maxPrincipal: 50_000_000_000, maxRate: 30, maxYears: 50 };
  const parseNumber = value => { const c = String(value).replace(/[,\s]/g, ''); if (!c || !/^\d*\.?\d+$/.test(c)) return null; const n = Number(c); return Number.isFinite(n) ? n : null; };
  function validate(i) {
    if (!(i.principal > 0)) return '대출금을 입력해 주세요.';
    if (i.principal > limits.maxPrincipal) return '대출금이 너무 큽니다. 500억 원 이하로 입력해 주세요.';
    if (!(i.annualRate >= 0) || i.annualRate > limits.maxRate) return `연 금리는 0~${limits.maxRate}% 범위로 입력해 주세요.`;
    if (!Number.isInteger(i.years) || i.years < 1 || i.years > limits.maxYears) return `대출 기간은 1~${limits.maxYears}년 사이의 정수로 입력해 주세요.`;
    if (!Number.isInteger(i.graceYears) || i.graceYears < 0) return '거치 기간은 0년 이상의 정수로 입력해 주세요.';
    if (i.method !== 'bullet' && i.graceYears >= i.years) return '거치 기간은 대출 기간보다 짧아야 합니다.';
    return null;
  }
  function calculate(input) {
    const months = input.years * 12, graceMonths = input.method === 'bullet' ? months : input.graceYears * 12, repay = months - graceMonths, rate = input.annualRate / 100 / 12;
    let balance = input.principal, first = 0, last = 0;
    const yearly = Array.from({ length: input.years }, (_, i) => ({ year: i + 1, principal: 0, interest: 0, total: 0, balance: 0 }));
    const level = repay > 0 ? (rate === 0 ? input.principal / repay : (input.principal * rate) / (1 - Math.pow(1 + rate, -repay))) : 0;
    for (let month = 1; month <= months; month += 1) {
      const interest = balance * rate;
      let paid = 0;
      if (month > graceMonths) { if (input.method === 'annuity') paid = level - interest; else if (input.method === 'principal') paid = input.principal / repay; }
      if (month === months) paid = balance;
      balance = Math.max(0, balance - paid);
      const row = yearly[Math.ceil(month / 12) - 1];
      row.principal += paid; row.interest += interest; row.total += paid + interest; row.balance = balance;
      if (month === graceMonths + 1 || (graceMonths >= months && month === 1)) first = paid + interest;
      if (month === months) last = paid + interest;
    }
    const totalInterest = yearly.reduce((s, r) => s + r.interest, 0);
    return { first, last, totalInterest, totalPayment: input.principal + totalInterest, yearly };
  }
  const won = value => {
    const man = Math.round(value / 10000); if (man === 0) return '0원';
    const eok = Math.floor(man / 10000), rest = man % 10000, parts = [];
    if (eok > 0) parts.push(`${eok.toLocaleString('ko-KR')}억`); if (rest > 0) parts.push(`${rest.toLocaleString('ko-KR')}만`);
    return `${parts.join(' ')}원`;
  };

  function loan(root) {
    let method = 'annuity';
    const principal = el('input', { inputmode: 'numeric', 'aria-label': '대출금', value: '300,000,000' });
    const rate = el('input', { inputmode: 'decimal', 'aria-label': '연 금리', value: '4' });
    const years = el('input', { inputmode: 'numeric', 'aria-label': '대출 기간', value: '30' });
    const grace = el('input', { inputmode: 'numeric', 'aria-label': '거치 기간', value: '0' });
    const quick = el('div', { class: 'pyeong-quick loan-wide', role: 'group', 'aria-label': '대출금 빠른 선택' });
    const quickButtons = [1, 2, 3, 4, 5].map(n => { const b = el('button', { type: 'button', onclick: () => { principal.value = (n * 100_000_000).toLocaleString('ko-KR'); render(); } }, n + '억'); quick.append(b); return [n * 100_000_000, b]; });
    const methodBox = el('div', { class: 'loan-methods', role: 'radiogroup', 'aria-label': '상환 방식' });
    const methodButtons = methods.map(key => { const b = el('button', { type: 'button', role: 'radio', onclick: () => { method = key; render(); } }, methodLabels[key]); methodBox.append(b); return [key, b]; });
    const out = el('div', {});
    let lastSpec = null;
    const exporter = exportButtons(() => lastSpec);
    principal.addEventListener('input', () => { const d = principal.value.replace(/[^\d]/g, ''); principal.value = d ? Number(d).toLocaleString('ko-KR') : ''; render(); });
    [rate, years, grace].forEach(i => i.addEventListener('input', render));
    function render() {
      const input = { principal: parseNumber(principal.value) ?? 0, annualRate: parseNumber(rate.value) ?? -1, years: parseNumber(years.value) ?? 0, graceYears: parseNumber(grace.value) ?? -1, method };
      quickButtons.forEach(([value, b]) => b.setAttribute('aria-pressed', String(input.principal === value)));
      methodButtons.forEach(([key, b]) => b.setAttribute('aria-checked', String(key === method)));
      const error = validate(input);
      out.replaceChildren(); lastSpec = null;
      if (error) { exporter.refresh(); out.append(el('p', { class: 'loan-error', role: 'alert' }, error)); return; }
      const results = Object.fromEntries(methods.map(key => [key, calculate({ ...input, method: key })]));
      const current = results[method];
      const monthly = method === 'principal' && current.first !== current.last ? `첫 달 ${won(current.first)} → 마지막 달 ${won(current.last)}` : won(current.first);
      lastSpec = { title: '대출 상환 계산', headline: { label: `${methodLabels[method]} ${method === 'bullet' ? '매달 이자' : '매달 상환액'}`, value: monthly },
        rows: [{ label: '대출금', value: won(input.principal) }, { label: '연 금리 · 기간', value: `연 ${input.annualRate}% · ${input.years}년${input.graceYears ? ` (거치 ${input.graceYears}년)` : ''}` }, { label: '총이자', value: won(current.totalInterest) }, { label: '총 상환액', value: won(current.totalPayment) }],
        notes: ['금리가 변하지 않는다고 가정한 참고용 계산입니다.', '실제 한도·금리·상환 조건은 금융기관 심사와 상품에 따라 달라집니다.'], filename: `hoban-loan-${methodLabels[method]}` };
      exporter.refresh();
      out.append(
        el('div', { class: 'pyeong-result loan-result', role: 'status', 'aria-live': 'polite' }, el('p', { class: 'pyeong-result-label' }, `${methodLabels[method]} · ${method === 'bullet' ? '매달 이자' : '매달 상환액'}`), el('strong', {}, monthly),
          el('dl', {}, el('div', {}, el('dt', {}, '총이자'), el('dd', {}, won(current.totalInterest))), el('div', {}, el('dt', {}, '총 상환액'), el('dd', {}, won(current.totalPayment))))),
        el('h3', { class: 'loan-subtitle' }, '방식별 총이자 비교'),
        el('ul', { class: 'loan-compare' }, methods.map(key => el('li', { class: key === method ? 'on' : false }, el('span', {}, methodLabels[key]), el('b', {}, won(results[key].totalInterest))))),
        el('h3', { class: 'loan-subtitle' }, '연도별 상환표'),
        el('div', { class: 'pyeong-table-wrap' }, el('table', { class: 'pyeong-table loan-table' },
          el('thead', {}, el('tr', {}, ['연차', '낸 원금', '낸 이자', '연간 합계', '남은 원금'].map(h => el('th', {}, h)))),
          el('tbody', {}, current.yearly.map(row => el('tr', {}, el('th', { scope: 'row' }, `${row.year}년차`), el('td', {}, won(row.principal)), el('td', {}, won(row.interest)), el('td', {}, won(row.total)), el('td', {}, won(row.balance))))))));
    }
    root.replaceChildren(el('section', { class: 'loan-card', 'aria-label': '대출 상환 계산기' },
      el('div', { class: 'loan-form' }, el('div', { class: 'pyeong-field loan-wide' }, field('대출금', principal, '원', '예: 잔금 대출 3억 원이면 300,000,000')), quick, field('연 금리', rate, '%'), field('대출 기간', years, '년'), field('거치 기간', grace, '년'), el('div', { class: 'pyeong-field' }, el('span', {}, '상환 방식'), methodBox)),
      out, exporter,
      el('p', { class: 'pyeong-note' }, '※ 참고용 계산입니다. 실제 금리·한도·상환 조건은 금융기관 심사와 상품에 따라 정해지며, 중도상환수수료·변동금리는 반영하지 않았습니다.')));
    render();
  }

  const tools = { pyeong, score, loan };
  document.querySelectorAll('[data-tool]').forEach(root => tools[root.dataset.tool]?.(root));
})();
