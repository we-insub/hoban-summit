'use client';

import { useState, useEffect } from 'react';
import { Calculator, Plus, Trash2 } from 'lucide-react';
import { calculateDsr, generalAcquisitionTax, repaymentSchedule, type Repayment } from './cost-math';
import { costPresets } from './cost-presets';

type Option = { id: number; name: string; amount: string; selected: boolean; taxable: boolean };
type Debt = { id: number; name: string; principal: string; rate: string; months: string; method: Repayment; manual: boolean; annual: string; stress: string };
const tabs = ['모의계산', '옵션계산', '취등록세', 'DSR계산기'] as const;
type Tab = typeof tabs[number];
const tabLabels: Record<Tab, string> = { 모의계산: '모의 계산', 옵션계산: '옵션 계산', 취등록세: '취득세 계산', DSR계산기: 'DSR 계산' };
const number = (value: string) => value.trim() === '' ? 0 : Number(value);
const won = (value: number) => `${Math.round(value).toLocaleString('ko-KR')}원`;
const money = (value: number) => won(value * 10000);
const blankDebt = (id: number): Debt => ({ id, name: id === 1 ? '이번 아파트 주택담보대출' : '기존 대출', principal: '', rate: '', months: '360', method: 'annuity', manual: false, annual: '', stress: '0' });
const blankOptions = (): Option[] => [{ id: 1, name: '발코니 확장', amount: '', selected: false, taxable: true }, { id: 2, name: '시스템 에어컨', amount: '', selected: false, taxable: true }];

function Amount({ label, value, onChange, unit = '만원', required = false, max = 100000000, min = 0, step = 'any', readOnly = false }: { label: string; value: string; onChange: (value: string) => void; unit?: string; required?: boolean; max?: number; min?: number; step?: string; readOnly?: boolean }) {
  return <label className="cost-field"><span>{label}</span><div><input readOnly={readOnly} type="number" inputMode="decimal" min={min} max={max} step={step} required={required} value={value} onChange={e => { const next = e.target.value; if (next === '' || (Number.isFinite(Number(next)) && Number(next) >= 0 && Number(next) <= max)) onChange(next); }} placeholder="직접 입력" /><span>{unit}</span></div></label>;
}

export function CostCalculator({ initialTab = '모의계산', standalone = false, projectSlug }: { initialTab?: Tab; standalone?: boolean; projectSlug?: string }) {
  const [tab, setTab] = useState<Tab>(initialTab);
  const preset = projectSlug ? costPresets[projectSlug] : undefined;
  const initialSelection = preset?.defaultSelection ?? (preset ? { block: 0, type: 0, floor: 0 } : undefined);
  const initialBlock = initialSelection && preset?.blocks[initialSelection.block];
  const initialType = initialSelection && initialBlock?.types[initialSelection.type];
  const initialRow = initialSelection && initialType?.rows[initialSelection.floor];
  const [blockIndex, setBlockIndex] = useState(initialBlock ? String(initialSelection?.block) : '');
  const [typeIndex, setTypeIndex] = useState(initialType ? String(initialSelection?.type) : '');
  const [floorIndex, setFloorIndex] = useState(initialRow ? String(initialSelection?.floor) : '');
  const selectedBlock = blockIndex === '' ? undefined : preset?.blocks[Number(blockIndex)];
  const selectedType = typeIndex === '' ? undefined : selectedBlock?.types[Number(typeIndex)];
  useEffect(() => { const el=document.getElementById('mohamoa-calculator'); if(el)el.dataset.currentUnit=selectedType?.label || ''; }, [selectedType?.label]);
  const selectedRow = floorIndex === '' ? undefined : selectedType?.rows[Number(floorIndex)];
  const [price, setPrice] = useState(initialRow ? String(initialRow.price) : '');
  const [contract, setContract] = useState(initialRow ? String(initialBlock?.contractPercent ?? preset?.contractPercent) : '10');
  const [interim, setInterim] = useState(initialRow ? String(preset?.interimPercent) : '60');
  const [cash, setCash] = useState('');
  const [loan, setLoan] = useState('');
  const [options, setOptions] = useState<Option[]>(() => blankOptions().map((option, index) => index === 0 && initialType ? { ...option, amount: initialType.balconyIncluded ? '' : String(initialType.balconyAmount), taxable: false } : option));
  const [over85, setOver85] = useState(initialType?.over85 ?? false);
  const [taxMode, setTaxMode] = useState('');
  const [extraBase, setExtraBase] = useState('');
  const [confirmedTax, setConfirmedTax] = useState('');
  const [income, setIncome] = useState('');
  const [limit, setLimit] = useState('40');
  const [debts, setDebts] = useState<Debt[]>([blankDebt(1)]);
  const [dsr, setDsr] = useState<null | { ratio: number; annualPayment: number; stressedRatio: number; rows: { name: string; annual: number; monthly: number | null; stressAnnual: number }[]; threshold: number }>(null);
  const [error, setError] = useState('');
  const [budgetReady, setBudgetReady] = useState(false);
  const [taxReady, setTaxReady] = useState(false);
  const optionTotal = options.filter(o => o.selected).reduce((sum, o) => sum + number(o.amount), 0);
  const taxableOptions = options.filter(o => o.selected && o.taxable).reduce((sum, o) => sum + number(o.amount), 0);
  const base = number(price) + taxableOptions + number(extraBase);
  const safeBase = Number.isFinite(base) && base >= 0 ? base : 0;
  const taxes = generalAcquisitionTax(safeBase * 10000, over85);
  const taxTotal = taxMode === 'normal' ? taxes.total / 10000 : number(confirmedTax);
  const taxKnown = taxMode === 'normal' || (taxMode === 'confirmed' && confirmedTax !== '');
  const total = number(price) + optionTotal + (taxKnown ? taxTotal : 0);
  const validOptions = options.every(o => !o.selected || (o.amount !== '' && Number.isFinite(number(o.amount)) && number(o.amount) >= 0));

  function changed() { setBudgetReady(false); setTaxReady(false); setError(''); }
  function clearPresetValues() { setPrice(''); setContract('10'); setInterim('60'); setOver85(false); setOptions(blankOptions()); changed(); }
  function applyType(type: typeof selectedType, block: typeof selectedBlock) {
    const row = type?.rows[0];
    setFloorIndex(row ? '0' : '');
    setPrice(row ? String(row.price) : '');
    setContract(row && preset ? String(block?.contractPercent ?? preset.contractPercent) : '10');
    setInterim(row && preset ? String(preset.interimPercent) : '60');
    setOver85(type?.over85 ?? false);
    setOptions(current => current.map((option, index) => index === 0 ? { ...option, name: '발코니 확장', amount: type && !type.balconyIncluded ? String(type.balconyAmount) : '', selected: false, taxable: false } : option));
    changed();
  }
  function chooseBlock(value: string) {
    setBlockIndex(value);
    const block = value === '' ? undefined : preset?.blocks[Number(value)];
    setTypeIndex(block?.types[0] ? '0' : '');
    if (block) applyType(block.types[0], block); else { setFloorIndex(''); clearPresetValues(); }
  }
  function chooseType(value: string) {
    setTypeIndex(value);
    const type = value === '' ? undefined : selectedBlock?.types[Number(value)];
    if (type) applyType(type, selectedBlock); else { setFloorIndex(''); clearPresetValues(); }
  }
  function chooseFloor(value: string) {
    setFloorIndex(value);
    const row = value === '' ? undefined : selectedType?.rows[Number(value)];
    setPrice(row ? String(row.price) : '');
    setContract(row && preset ? String(selectedBlock?.contractPercent ?? preset.contractPercent) : '10');
    setInterim(row && preset ? String(preset.interimPercent) : '60');
    setOver85(row ? Boolean(selectedType?.over85) : false);
    changed();
  }
  function updateOption(id: number, patch: Partial<Option>) { setOptions(options.map(o => o.id === id ? { ...o, ...patch } : o)); changed(); }
  function updateDebt(id: number, patch: Partial<Debt>) { setDebts(debts.map(d => d.id === id ? { ...d, ...patch } : d)); setDsr(null); setError(''); }
  function switchTab(next: Tab) { setTab(next); setError(''); }
  function calculate() {
    try {
      const rows = debts.map(d => {
        if (d.manual) {
          if (d.annual === '') throw new Error(`${d.name}: 연간 원리금 상환액을 입력해 주세요.`);
          return { name: d.name, annual: number(d.annual), monthly: null, stressAnnual: number(d.annual) };
        }
        if (d.principal === '' || d.rate === '') throw new Error(`${d.name}: 대출금과 금리를 입력해 주세요.`);
        const actual = repaymentSchedule(number(d.principal), number(d.rate), number(d.months), d.method);
        const stressed = repaymentSchedule(number(d.principal), number(d.rate) + number(d.stress), number(d.months), d.method);
        return { name: d.name, annual: actual.annualPayment, monthly: actual.firstPayment, stressAnnual: stressed.annualPayment };
      });
      const result = calculateDsr(number(income), rows.map(r => r.annual));
      const stress = calculateDsr(number(income), rows.map(r => r.stressAnnual));
      setDsr({ ...result, stressedRatio: stress.ratio, rows, threshold: number(limit) }); setError('');
    } catch (e) { setDsr(null); setError(e instanceof Error ? e.message : '입력값을 확인해 주세요.'); }
  }

  return <div className="cost-workspace">
    {projectSlug && <section className="cost-project-selection" aria-label="단지별 계산 기준 선택">
      <h2>관심 있는 주택형과 층을 골라보세요</h2>
      {preset ? <><p>블록과 주택형, 층을 고르면 해당 공고의 분양가가 나옵니다. 분양가와 계약금·중도금 비율은 공고 금액으로 계산하므로 직접 바꿀 수 없습니다. 현재 계약할 세대의 금액과 납부 조건은 공식 분양처에 따로 확인해 주세요.</p>
        <div className="cost-fields"><label className="cost-field"><span>블록</span><select value={blockIndex} onChange={e => chooseBlock(e.target.value)}><option value="">블록 선택</option>{preset.blocks.map((block, i) => <option key={block.label} value={i}>{block.label}</option>)}</select></label>
        <label className="cost-field"><span>주택형</span><select value={typeIndex} disabled={!selectedBlock} onChange={e => chooseType(e.target.value)}><option value="">주택형 선택</option>{selectedBlock?.types.map((type, i) => <option key={type.label} value={i}>{type.label}</option>)}</select></label>
        <label className="cost-field"><span>층 구분</span><select value={floorIndex} disabled={!selectedType} onChange={e => chooseFloor(e.target.value)}><option value="">층 선택</option>{selectedType?.rows.map((row, i) => <option key={row.floor} value={i}>{row.floor}</option>)}</select></label></div>
        {selectedRow && selectedBlock && <p className="cost-preset-source">{selectedType?.label} · {selectedRow.floor} 모집공고 분양가 <strong>{selectedRow.price.toLocaleString('ko-KR')}만원</strong> · 계약금 {selectedBlock.contractPercent ?? preset.contractPercent}% · 중도금 {preset.interimPercent}% · 전용 85㎡ {selectedType?.over85 ? '초과' : '이하'} · {selectedType?.balconyIncluded ? '발코니 확장비 공급금액에 포함' : `발코니 확장비 ${selectedType?.balconyAmount.toLocaleString('ko-KR')}만원(선택 시 합산)`}<br />출처: <a href={selectedBlock.source} target="_blank" rel="noopener noreferrer">{selectedBlock.label} 공식 모집공고 공급금액·발코니 확장비 표</a>{selectedBlock.supplementalSource && <> · <a href={selectedBlock.supplementalSource} target="_blank" rel="noopener noreferrer">정정 모집공고</a></>} · 자료 확인일 {preset.reviewedAt}. 공고 기준 2026.06.05. 계약할 동·호수의 실제 금액과 납부 조건은 계약 전에 확인해 주세요.{price !== String(selectedRow.price) && <> 현재 직접 수정한 분양가 입력값은 공고 금액과 다릅니다.</>}</p>}
        {selectedRow && number(price) > 0 && number(contract) + number(interim) <= 100 && <div className="cost-quick-breakdown" aria-label="선택한 주택형의 납부 금액"><strong>선택한 주택형의 납부 금액</strong><span>계약금 {money(number(price) * number(contract) / 100)}</span><span>중도금 {money(number(price) * number(interim) / 100)}</span><span>잔금 {money(number(price) * (100 - number(contract) - number(interim)) / 100)}</span></div>}
      </> : <p>이 단지는 블록·주택형·층별 공식 가격표가 아직 계산기에 등록되지 않았습니다. 공식 모집공고에서 원하는 동·호수의 공급금액을 확인해 아래에 입력해 주세요.</p>}
    </section>}
    {!standalone && <nav className="cost-tabs" aria-label="계산기 선택">{tabs.map(t => <button key={t} type="button" aria-pressed={tab === t} onClick={() => switchTab(t)}>{tabLabels[t]}</button>)}</nav>}
    <section className="cost-panel" aria-label={tab}>
      {tab === '모의계산' && <form onSubmit={e => { e.preventDefault(); if (number(contract) + number(interim) > 100) { setError('계약금과 중도금 비율의 합은 100% 이하여야 합니다.'); return; } if (!validOptions) { setError('옵션계산에서 선택한 옵션의 금액을 입력해 주세요.'); return; } setError(''); setBudgetReady(true); }}>
        <h2>내 집 마련 자금 모의계산</h2><p className="cost-description">{selectedRow ? '선택하신 주택형과 층의 공고 분양가입니다. 준비한 현금과 예상 대출금을 넣어보세요. 실제 계약할 세대의 금액과 납부 조건도 함께 확인해 주세요.' : '공식 공급금액을 입력하면 납부 단계별 금액과 필요한 자기자금을 계산합니다.'}</p>
        <div className="cost-fields"><Amount readOnly={Boolean(preset)} label="분양가" value={price} onChange={v => { setPrice(v); changed(); }} required min={.0001} /><Amount label="보유 현금" value={cash} onChange={v => { setCash(v); changed(); }} /><Amount label="예상 대출금" value={loan} onChange={v => { setLoan(v); changed(); }} /><Amount readOnly={Boolean(preset)} label="계약금 비율" unit="%" value={contract} onChange={v => { setContract(v); changed(); }} required max={100} /><Amount readOnly={Boolean(preset)} label="중도금 비율" unit="%" value={interim} onChange={v => { setInterim(v); changed(); }} required max={100} /></div>
        <p className="cost-hint">{selectedRow ? '계약금과 중도금은 선택하신 블록의 모집공고 비율로 계산합니다. 실제 납부 조건은 계약 전에 다시 확인해 주세요.' : '계약금 10%·중도금 60%는 계산 예시입니다. 해당 단지의 계약 조건으로 수정하세요.'} 예상 대출금은 자금 계획을 위해 입력하는 금액입니다. 중도금 납부일에 맞춘 대출 실행 여부까지 계산하는 것은 아닙니다.</p>
        <div className="cost-inline-summary"><span>선택 옵션 <strong>{money(optionTotal)}</strong></span><button type="button" onClick={() => switchTab('옵션계산')}>옵션 선택하기 →</button><span>취득 관련 세금 <strong>{taxKnown ? money(taxTotal) : '미설정'}</strong></span><button type="button" onClick={() => switchTab('취등록세')}>세금 설정하기 →</button></div>
        <button className="cost-primary" type="submit"><Calculator size={18} />모의계산</button>
        {budgetReady && <div className="cost-result" aria-live="polite"><p>총 예상 지출 {taxKnown ? '(세금 포함)' : '(세금 제외)'}</p><strong className="cost-result-number">{money(total)}</strong><dl><div><dt>분양대금 계약금</dt><dd>{money(number(price) * number(contract) / 100)}</dd></div><div><dt>분양대금 중도금</dt><dd>{money(number(price) * number(interim) / 100)}</dd></div><div><dt>분양대금 잔금</dt><dd>{money(number(price) * (100 - number(contract) - number(interim)) / 100)}</dd></div><div><dt>별도로 선택한 옵션</dt><dd>{money(optionTotal)}</dd></div><div><dt>대출 외에 준비할 금액</dt><dd>{money(Math.max(0, total - number(loan)))}</dd></div><div><dt>추가로 필요한 금액</dt><dd>{money(Math.max(0, total - number(loan) - number(cash)))}</dd></div></dl><p>옵션 납부 시점·대출이자·등기 수수료·채권 할인·중개보수·이사비는 포함하지 않습니다.{number(loan) > total && ' 예상 대출금이 총 지출보다 큽니다. 입력값을 확인하세요.'}</p></div>}
      </form>}

      {tab === '옵션계산' && <><h2>필요한 옵션의 비용을 계산해 보세요</h2><p className="cost-description">{selectedType ? selectedType.balconyIncluded ? '선택한 펜트하우스는 발코니 확장비가 공급금액에 포함돼 있습니다. 다른 옵션은 공식 계약 금액을 확인해 입력하세요.' : '발코니 확장비는 공고에 나온 금액입니다. 확장을 선택하실 때 체크해 주세요. 시스템 에어컨 등 다른 옵션은 계약 자료에서 금액을 확인한 뒤 넣으면 됩니다.' : '공식 옵션표의 금액을 입력하고 선택하세요.'} 옵션 이름은 원하는 항목으로 바꿀 수 있습니다.</p><div className="cost-option-list">{options.filter(o => !selectedType?.balconyIncluded || o.id !== 1).map((o, i) => <div className="cost-option" key={o.id}><label className="cost-check"><input type="checkbox" checked={o.selected} onChange={e => updateOption(o.id, { selected: e.target.checked })} />선택</label><label className="cost-field"><span>옵션 {i + 1} 이름</span><input value={o.name} maxLength={60} onChange={e => updateOption(o.id, { name: e.target.value })} /></label><Amount label="옵션 금액" value={o.amount} onChange={v => { if (v === '' || (Number.isFinite(Number(v)) && Number(v) >= 0 && Number(v) <= 100000000)) updateOption(o.id, { amount: v }); }} /><label className="cost-check"><input type="checkbox" checked={o.taxable} onChange={e => updateOption(o.id, { taxable: e.target.checked })} />취득세 계산에 포함</label><button className="cost-remove" type="button" aria-label={`옵션 ${i + 1} 삭제`} onClick={() => { setOptions(options.filter(entry => entry.id !== o.id)); changed(); }}><Trash2 size={18} /></button></div>)}</div>
        <button type="button" className="cost-secondary" disabled={options.length >= 20} onClick={() => { setOptions([...options, { id: Math.max(0, ...options.map(o => o.id)) + 1, name: '추가 옵션', amount: '', selected: false, taxable: true }]); changed(); }}><Plus size={17} />옵션 추가</button>
        <p className="cost-hint">옵션 비용을 취득세 계산에 더해야 하는지는 공급 형태와 계약에 따라 다릅니다. 공급계약서와 관할 지자체에서 확인한 내용에 맞춰 체크해 주세요.</p><div className="cost-result"><p>선택 옵션 합계</p><strong className="cost-result-number">{money(optionTotal)}</strong>{standalone && <p>취득세 계산에 포함한 옵션 금액: {money(taxableOptions)}. 실제 과세 여부를 확인한 뒤 취득세 계산기의 추가 금액에 입력하세요.</p>}<p>{validOptions ? (standalone ? '선택한 옵션만 합산한 금액입니다. 다른 계산기로 이동하면 입력값이 초기화됩니다.' : '선택한 옵션은 자금 모의계산에 더해집니다. 취득세는 ‘취득세 계산에 포함’으로 체크한 금액만 함께 계산합니다.') : '선택한 옵션 중 금액이 비어 있습니다. 금액을 입력해 주세요.'}</p></div></>}

      {tab === '취등록세' && <form onSubmit={e => { e.preventDefault(); if (!validOptions) { setError('선택한 옵션 금액을 먼저 입력해 주세요.'); return; } setError(''); setTaxReady(true); }}><h2>취득세와 함께 내는 세금</h2><p className="cost-description">주택을 구입할 때 내는 취득세와 지방교육세, 농어촌특별세의 예상 금액을 계산합니다. 일반세율을 적용한 결과이며, 예전의 등록세는 취득세에 통합돼 별도로 더하지 않습니다.</p>
        <label className="cost-field"><span>계산 대상 확인</span><select required value={taxMode} onChange={e => { setTaxMode(e.target.value); changed(); }}><option value="">해당하는 방식을 선택하세요</option><option value="normal">개인 주택 유상취득 · 일반세율 (중과·감면 없음)</option><option value="confirmed">다주택·법인·감면 해당 · 관할 지자체에서 확인한 세액 입력</option></select></label>
        <div className="cost-fields"><Amount readOnly={Boolean(preset)} label={standalone ? "매매가 또는 분양가" : "분양가 (자금 모의계산과 같은 금액)"} value={price} onChange={v => { setPrice(v); changed(); }} required min={.0001} />{taxMode === 'normal' && <Amount readOnly={Boolean(preset)} label={standalone ? "과세표준 추가 금액 (과세 대상 옵션 등)" : "기타 과세표준 추가 금액"} value={extraBase} onChange={v => { setExtraBase(v); changed(); }} />}{taxMode === 'confirmed' && <Amount label="확인받은 세금 총액" value={confirmedTax} onChange={v => { setConfirmedTax(v); changed(); }} required />}</div>
        {taxMode === 'normal' && <><label className="cost-check"><input type="checkbox" disabled={Boolean(preset)} checked={over85} onChange={e => { setOver85(e.target.checked); changed(); }} />전용면적 85㎡ 초과 (선택한 주택형 기준)</label><p className="cost-hint">{!standalone && <>선택 옵션 중 과표 포함 금액: {money(taxableOptions)} · </>}계산 과표: {money(base)}. 일반세율은 6억원 이하 1%, 6억 초과~9억원 이하 1~3%, 9억원 초과 3%입니다. 생애최초 감면·일시적 2주택·중과 판정은 자동 적용하지 않습니다.</p></>}
        <button className="cost-primary" type="submit">취득 관련 세금 계산</button>
        {taxReady && <div className="cost-result" aria-live="polite"><p>{taxMode === 'normal' ? '일반세율 기준 예상 세금' : '직접 입력한 확인 세액'}</p><strong className="cost-result-number">{money(taxTotal)}</strong>{taxMode === 'normal' && <dl><div><dt>취득세 ({(taxes.rate * 100).toFixed(2)}%)</dt><dd>{won(taxes.acquisition)}</dd></div><div><dt>지방교육세</dt><dd>{won(taxes.education)}</dd></div><div><dt>농어촌특별세 ({over85 ? '0.2%' : '85㎡ 이하 제외'})</dt><dd>{won(taxes.rural)}</dd></div></dl>}<p>등기 수수료·국민주택채권 할인액은 제외합니다. 실제 과표와 원단위 처리에 따라 고지액이 달라질 수 있습니다.</p></div>}
        <p className="cost-source-note">계산 근거: <a href="https://law.go.kr/LSW/lsSideInfoP.do?docCls=jo&joBrNo=00&joNo=0011&lsiSeq=282559&urlMode=lsScJoRltInfoR" target="_blank" rel="noopener noreferrer">지방세법 제11조</a> · <a href="https://www.goheung.go.kr/contentsView.do?pageId=www527" target="_blank" rel="noopener noreferrer">지자체 취득세 안내</a> (확인 2026.09.10)</p>
      </form>}

      {tab === 'DSR계산기' && <form onSubmit={e => { e.preventDefault(); calculate(); }}><h2>총부채원리금상환비율 (DSR) 계산</h2>
        <details className="cost-explainer" open={!standalone}><summary>DSR이란?</summary><p>연소득에서 모든 대출의 연간 원금과 이자 상환액이 차지하는 비율입니다. 연소득 5,000만원에 연간 상환액 2,000만원이면 DSR은 40%입니다.</p><strong>DSR = 연간 전체 대출 원리금 상환액 ÷ 연소득 × 100</strong><p>아래 결과는 입력한 상환 조건에 따른 모의 DSR입니다. 금융기관의 규제 DSR은 대출 종류별 인정 만기·예외·스트레스 금리 등에 따라 다릅니다. 신용대출 등은 금융기관에서 안내받은 ‘DSR 산정용 연간 원리금’을 직접 입력할 수 있습니다.</p></details>
        <details className="cost-explainer"><summary>상환방법과 스트레스 금리</summary><p>원리금균등: 매달 원금과 이자의 합계가 같습니다. 원금균등: 원금은 일정하고 이자는 점차 줄어듭니다. 만기일시: 매달 이자를 내고 만기에 원금을 갚습니다.</p><p>잔액과 남은 기간을 기준으로 앞으로 12개월의 납부액을 합산하며, 거치기간은 지원하지 않습니다. 만기일시상환의 만기가 12개월 안이면 원금 전액을 포함합니다. 이는 금융기관의 규제 산식과 다를 수 있습니다.</p><p>스트레스 가산금리는 실제 납부금리에 붙는 이자가 아닌 심사용 가정입니다. 대출별 적용 금리를 금융기관에서 확인해 입력하세요. 기본값 0%p는 스트레스 미반영이며 현재 정책 금리를 뜻하지 않습니다. 연간 원리금을 직접 입력한 대출에는 추가로 가산하지 않습니다.</p></details>
        <div className="cost-fields"><Amount label="증빙 가능한 연소득" value={income} onChange={v => { setIncome(v); setDsr(null); }} required min={.0001} /><label className="cost-field"><span>비교할 DSR 비율 · 대출 승인 기준 아님</span><select value={limit} onChange={e => { setLimit(e.target.value); setDsr(null); }}><option value="40">은행권 참고 40%</option><option value="50">비은행권 참고 50%</option></select></label></div>
        <p className="cost-description">이번에 받을 대출과 아직 갚고 있는 대출을 함께 넣어주세요. 연소득과 대출금은 ‘만원’ 단위로 입력합니다.</p>
        {number(loan) > 0 && <button className="cost-secondary" type="button" onClick={() => updateDebt(debts[0].id, { principal: loan, manual: false })}>첫 대출에 모의계산 대출금 {money(number(loan))} 적용</button>}
        <div className="cost-debts">{debts.map((d, index) => <fieldset key={d.id}><legend>대출 {index + 1}</legend><div className="cost-debt-heading"><label className="cost-field"><span>대출 이름</span><input value={d.name} maxLength={60} required onChange={e => updateDebt(d.id, { name: e.target.value })} /></label>{debts.length > 1 && <button className="cost-remove" type="button" aria-label={`대출 ${index + 1} 삭제`} onClick={() => { setDebts(debts.filter(entry => entry.id !== d.id)); setDsr(null); }}><Trash2 size={18} /></button>}</div><label className="cost-check"><input type="checkbox" checked={d.manual} onChange={e => updateDebt(d.id, { manual: e.target.checked })} />금융기관의 DSR 산정용 연간 원리금 직접 입력</label>
          {d.manual ? <Amount label="연간 원리금 상환액" value={d.annual} onChange={v => updateDebt(d.id, { annual: v })} required /> : <div className="cost-fields"><Amount label="대출금 또는 현재 잔액" value={d.principal} onChange={v => updateDebt(d.id, { principal: v })} required min={.0001} /><Amount label="연 금리" unit="%" value={d.rate} onChange={v => updateDebt(d.id, { rate: v })} required max={100} /><Amount label="남은 대출기간" unit="개월" value={d.months} onChange={v => updateDebt(d.id, { months: v })} required min={1} max={600} step="1" /><label className="cost-field"><span>상환방법</span><select value={d.method} onChange={e => updateDebt(d.id, { method: e.target.value as Repayment })}><option value="annuity">원리금균등</option><option value="principal">원금균등</option><option value="bullet">만기일시</option></select></label><Amount label="스트레스 가산금리 (미반영: 0)" unit="%p" value={d.stress} onChange={v => updateDebt(d.id, { stress: v })} max={20} /></div>}</fieldset>)}</div>
        <div className="cost-button-row"><button className="cost-secondary" type="button" disabled={debts.length >= 20} onClick={() => { setDebts([...debts, blankDebt(Math.max(...debts.map(d => d.id)) + 1)]); setDsr(null); }}><Plus size={17} />대출 추가</button><button className="cost-primary" type="submit">DSR 계산</button></div>
        {dsr && <div className="cost-result" aria-live="polite"><p>입력하신 조건으로 계산한 DSR</p><strong className="cost-result-number">{dsr.ratio.toFixed(2)}%</strong><p>비교 기준 {dsr.threshold}% {dsr.ratio > dsr.threshold ? '초과' : '이하'} · 대출 가능 여부를 의미하지 않습니다.</p><dl><div><dt>연간 원리금 합계</dt><dd>{money(dsr.annualPayment)}</dd></div><div><dt>가산금리 반영 모의 DSR</dt><dd>{dsr.stressedRatio.toFixed(2)}%</dd></div></dl>{dsr.rows.map((r, i) => <div className="cost-debt-result" key={i}><strong>{r.name}</strong><p>연간 {money(r.annual)}{r.monthly !== null && ` · 첫 달 ${money(r.monthly)}`}</p></div>)}<p>LTV·DTI·상품별 한도·소득 인정·중도금 대출 예외 등을 심사하지 않습니다. 가산금리가 0이면 스트레스 DSR 규제를 반영한 결과가 아닙니다.</p></div>}
        <p className="cost-source-note">설명 근거: <a href="https://www.fsc.go.kr/po020201/76750" target="_blank" rel="noopener noreferrer">금융위원회 DSR 안내</a> · <a href="https://www.fsc.go.kr/po010101/81343" target="_blank" rel="noopener noreferrer">스트레스 DSR 개념</a>. 실제 적용은 대출 실행일·지역·상품에 따라 확인하세요.</p>
      </form>}
      {error && <p className="cost-error" role="alert">{error}</p>}
    </section>
  </div>;
}
