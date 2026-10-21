const assert = require('node:assert/strict');
const p=require('../concepts/popup-preference.js');
for(const t of ['2026-10-21T14:59:59Z','2026-10-21T15:00:00Z','2026-12-31T14:59:59Z']){
 const now=Date.parse(t),until=p.nextKstMidnight(now);
 assert(until>now && until-now<=86400000);
 assert(p.isSuppressed(String(until),now));assert(!p.isSuppressed(until,until));
 assert(!p.isSuppressed('bad',now));assert(!p.isSuppressed(until+86400000,now));
}
console.log('KST day boundary / expiry / corrupt preference: passed');
