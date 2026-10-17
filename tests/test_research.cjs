const assert=require('node:assert/strict');
const {cutoff,windowPoints,comparison,expire}=require('../research.js');
assert.equal(cutoff('2026-03-31','1M'),'2026-02-28');
assert.equal(cutoff('2026-10-16','YTD'),'2025-12-31');
const a=[{date:'2025-12-30',close:100},{date:'2026-01-02',close:110},{date:'2026-01-05',close:120}];
const b=[{date:'2026-01-02',close:200},{date:'2026-01-05',close:220}];
const c=comparison([{ticker:'A',data:a},{ticker:'B',data:b}],'YTD');
assert.equal(c[0].data[0].date,'2026-01-02');
assert.equal(c[0].data[0].close,0);
assert.ok(Math.abs(c[0].data[1].close-9.090909)<.00001);
assert.ok(Math.abs(c[1].data[1].close-10)<.00001);
assert.deepEqual(comparison([{ticker:'A',data:a},{ticker:'B',data:[]}],'YTD'),[]);
assert.equal(windowPoints(a,'YTD')[0].date,'2025-12-30');
console.log('Period, YTD anchor, common-date comparison and missing data tests passed');

const snapshot={quotes:[{marketDate:'2026-10-16',status:'cached',price:100,peTTM:20,forwardPE:18,fundamentals:{fetchedAt:'2026-10-17T00:00:00Z'},researchScore:{complete:true,total:50,parts:{valuation:10,growth:10,quality:10,revisions:10,risk:10}}}]};
assert.equal(expire(snapshot,Date.parse('2026-10-18')).quotes[0].peTTM,20);
const stale=expire(snapshot,Date.parse('2026-11-01')).quotes[0];
assert.equal(stale.status,'stale');assert.equal(stale.peTTM,null);assert.equal(stale.researchScore.total,null);assert.equal(stale.researchScore.coveragePoints,0);
assert.equal(snapshot.quotes[0].peTTM,20); // source data not mutated
console.log('Snapshot expiry hides stale ratios and scores without modifying source');
