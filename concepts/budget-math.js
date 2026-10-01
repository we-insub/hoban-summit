(function (root) {
  function calculate(price, cash, loan, extras) {
    if (![price, cash, loan, extras].every(Number.isSafeInteger) || price <= 0 || Math.min(cash, loan, extras) < 0) throw new Error('금액을 확인해주세요.');
    const total = price + extras;
    if (!Number.isSafeInteger(total) || loan > total) throw new Error('예상 대출금은 총 필요 금액 이하로 입력해주세요.');
    const deposit = Math.round(price * 5 / 100);
    const interim = Math.round(price * 60 / 100);
    const balance = price - deposit - interim;
    return { total, first: 10000000, second: deposit - 10000000, deposit, interim, balance, equity: total - loan, gap: Math.max(0, total - loan - cash) };
  }
  root.ModelHouseBudget = { calculate };
  if (typeof module !== 'undefined') module.exports = { calculate };
})(typeof window === 'undefined' ? globalThis : window);
