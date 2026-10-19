const assert=require('node:assert/strict');
const {datasetFresh,selectRows}=require('../discovery.js');
const now=Date.parse('2026-10-19T12:00:00Z');
assert(datasetFresh({snapshotAt:'2026-10-19T11:00:00Z'},now));
assert(!datasetFresh({snapshotAt:'2026-10-01T11:00:00Z'},now));
assert(!datasetFresh({snapshotAt:'2026-10-25T11:00:00Z'},now));
assert(!datasetFresh({},now));
const rows=[{ticker:'A',name:'Alpha',coverage:100,originalUniverse:true,sp500Top100:{rank:1},industry:'Software'},
 {ticker:'B',name:'Beta',coverage:85,originalUniverse:false,sp500Top100:{rank:20},industry:'Banks'},
 {ticker:'C',name:'Gamma',coverage:55,originalUniverse:true,industry:'Software'}];
assert.deepEqual(selectRows(rows,{universe:'sp500',minimum:100}).map(r=>r.ticker),['A']);
assert.deepEqual(selectRows(rows,{universe:'original',search:'software'}).map(r=>r.ticker),['A','C']);
assert.deepEqual(selectRows(rows,{search:'  beta  ',minimum:85}).map(r=>r.ticker),['B']);
assert.equal(rows.length,3);
console.log('Research views: stale/future datasets blocked; universe, coverage and search filters remain independent.');
