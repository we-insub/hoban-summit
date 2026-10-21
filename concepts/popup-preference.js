/* Popup display preference only; never stores consultation inputs or consent. */
(function(root) {
  const DAY = 86400000, KST = 9 * 3600000;
  const nextKstMidnight = now => Math.floor((now + KST) / DAY) * DAY + DAY - KST;
  const isSuppressed = (stored, now) => Number.isFinite(Number(stored)) && Number(stored) > now && Number(stored) <= nextKstMidnight(now);
  const api = { nextKstMidnight, isSuppressed };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PopupPreference = api;
})(typeof window !== 'undefined' ? window : globalThis);
