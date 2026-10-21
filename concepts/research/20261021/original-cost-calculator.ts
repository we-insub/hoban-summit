export type Repayment = 'annuity' | 'principal' | 'bullet';

function nonnegative(value: number) {
  if (!Number.isFinite(value) || value < 0) throw new Error('0 이상의 유효한 숫자를 입력해 주세요.');
}

/** Monthly cash flow from today's balance, with no grace period. Amount unit is arbitrary. */
export function repaymentSchedule(principal: number, annualRate: number, months: number, method: Repayment) {
  nonnegative(principal); nonnegative(annualRate);
  if (!Number.isInteger(months) || months < 1 || months > 600) throw new Error('기간은 1~600개월로 입력해 주세요.');
  const rate = annualRate / 1200;
  const fixed = rate === 0 ? principal / months : principal * rate / -Math.expm1(-months * Math.log1p(rate));
  let balance = principal;
  let totalInterest = 0;
  let annualPayment = 0;
  let firstPayment = 0;
  for (let month = 1; month <= months; month++) {
    const interest = balance * rate;
    const capital = month === months ? balance : method === 'bullet' ? 0 : method === 'principal' ? principal / months : Math.min(balance, fixed - interest);
    const payment = capital + interest;
    if (month === 1) firstPayment = payment;
    if (month <= 12) annualPayment += payment;
    totalInterest += interest;
    balance = Math.max(0, balance - capital);
  }
  return { firstPayment, annualPayment, totalInterest, totalPayment: principal + totalInterest };
}

/** General-rate, paid residential acquisition only; input is KRW. No exemptions or surcharges. */
export function generalAcquisitionTax(base: number, over85: boolean) {
  nonnegative(base);
  // Local Tax Act art. 11: round the fractional tax rate to four decimal places.
  const rate = base <= 600_000_000 ? .01 : base > 900_000_000 ? .03 : Math.round((base * 2 / 300_000_000 - 3) / 100 * 10000) / 10000;
  const acquisition = Math.floor(base * rate);
  const education = Math.floor(base * rate / 10);
  const rural = over85 ? Math.floor(base * .002) : 0;
  return { rate, acquisition, education, rural, total: acquisition + education + rural };
}

export function calculateDsr(income: number, annualPayments: number[]) {
  if (!Number.isFinite(income) || income <= 0) throw new Error('연소득을 0보다 크게 입력해 주세요.');
  annualPayments.forEach(nonnegative);
  const annualPayment = annualPayments.reduce((sum, value) => sum + value, 0);
  return { annualPayment, ratio: annualPayment / income * 100 };
}
