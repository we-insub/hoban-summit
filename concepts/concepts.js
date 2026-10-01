(() => {
  const byId = id => document.getElementById(id);
  const data = window.HOBAN_DATA;
  const modal = document.querySelector('.reservation-modal');
  const form = document.querySelector('.reservation-form');
  const switchers = [...document.querySelectorAll('[data-modal-mode]')];
  const phoneHint = document.querySelector('.modal-phone-only');
  const planAssetBase = new URL('.', byId('plan-image').src);
  const syncModalScroll = () => document.body.classList.toggle('reservation-open', modal.classList.contains('is-open'));
  new MutationObserver(syncModalScroll).observe(modal, { attributes: true, attributeFilter: ['class'] });
  syncModalScroll();
  let returnFocus = null;
  function showMode(mode) {
    form.hidden = mode !== 'booking'; phoneHint.hidden = mode !== 'phone';
    switchers.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.modalMode === mode)));
  }
  switchers.forEach(button => button.addEventListener('click', () => showMode(button.dataset.modalMode)));
  document.querySelectorAll('[data-open-booking]').forEach(button => button.addEventListener('click', () => {
    returnFocus = button; modal.classList.add('is-open'); showMode('booking');
    form.elements.interest.value = byId('plan-unit').value; form.elements.name.focus();
  }));
  function close() { modal.classList.remove('is-open'); if (returnFocus) returnFocus.focus(); }
  document.querySelector('.modal-close').addEventListener('click', close);
  document.addEventListener('keydown', event => {
    if (!modal.classList.contains('is-open')) return;
    if (event.key === 'Escape') close();
    if (event.key === 'Tab') {
      const targets = [...modal.querySelectorAll('a,button,input,select,summary')].filter(el => !el.disabled && el.getClientRects().length > 0);
      const first = targets[0], last = targets[targets.length-1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  document.querySelector('.modal-close').focus();
  const tabs = [...document.querySelectorAll('[data-cost-tab]')];
  function showTab(button) {
    tabs.forEach(tab => {
      const active = tab === button; tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1;
      byId(tab.getAttribute('aria-controls')).hidden = !active;
    });
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => showTab(tab));
    tab.addEventListener('keydown', event => {
      const next = event.key === 'ArrowRight' ? (index+1)%tabs.length : event.key === 'ArrowLeft' ? (index+tabs.length-1)%tabs.length : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length-1 : null;
      if (next !== null) { event.preventDefault(); showTab(tabs[next]); tabs[next].focus(); }
    });
  });
  const won = value => new Intl.NumberFormat('ko-KR').format(value) + '원';
  const selectedUnit = () => data.units.find(unit => unit.id === byId('budget-unit').value);
  function moneyInput(id) {
    const input = byId(id);
    if (!input.validity.valid) throw new Error('현금·대출·추가 비용은 0 이상의 금액으로 입력해주세요.');
    const value = input.value === '' ? 0 : Number(input.value);
    const result = Math.round(value * 10000);
    if (!Number.isFinite(value) || !Number.isSafeInteger(result) || result < 0 || result > 1000000000000) throw new Error('금액 범위를 확인해주세요.');
    return result;
  }
  function updateBudget() {
    const unit = selectedUnit(); const row = unit.prices[Number(byId('budget-floor').value)];
    byId('budget-price').value = new Intl.NumberFormat('ko-KR').format(row.won/10000);
    byId('price-context').replaceChildren(document.createTextNode(`${unit.block} · ${unit.id} · ${row.floor} · 2026.06.05 공고의 공급금액입니다. `));
    const source = document.createElement('a'); source.href = `${unit.source_url}#page=${unit.pdf_page}`; source.target = '_blank'; source.rel = 'noopener'; source.textContent = `공고 ${unit.pdf_page}쪽 ↗`; byId('price-context').append(source);
    try {
      const result = window.ModelHouseBudget.calculate(row.won, moneyInput('budget-cash'), moneyInput('budget-loan'), moneyInput('budget-options') + moneyInput('budget-fees'));
      for (const key of ['total','equity','gap','first','second','interim','balance']) byId(`result-${key}`).textContent = won(result[key]);
      byId('budget-error').textContent = '';
    } catch (error) {
      byId('budget-error').textContent = error.message;
      for (const key of ['total','equity','gap','first','second','interim','balance']) byId(`result-${key}`).textContent = '입력한 금액을 확인해 주세요.';
    }
  }
  function updatePlan(id) {
    const unit = data.units.find(item => item.id === id);
    byId('plan-image').src = new URL(`unit-${id.toLowerCase()}.jpg`, planAssetBase).href;
    byId('plan-image').alt = `공식 ${unit.block} ${id} 확장 기본형 평면도 미리보기`;
    byId('plan-original').href = byId('plan-image').src;
    byId('plan-caption').textContent = `${unit.block} · ${id} 확장형 평면도입니다. 이미지를 누르면 면적표와 비확장형 평면도도 볼 수 있습니다. 옵션과 가구, 시공 범위는 계약할 때 확인해 주세요.`;
  }
  byId('plan-unit').addEventListener('change', () => {
    byId('budget-unit').value = byId('plan-unit').value; updatePlan(byId('plan-unit').value); updateBudget();
  });
  byId('budget-unit').addEventListener('change', () => {
    byId('plan-unit').value = byId('budget-unit').value; updatePlan(byId('budget-unit').value); updateBudget();
  });
  byId('budget-floor').addEventListener('change', updateBudget);
  ['budget-cash','budget-loan','budget-options','budget-fees'].forEach(id => byId(id).addEventListener('input', updateBudget));
  updateBudget();
})();
