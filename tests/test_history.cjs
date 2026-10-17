const assert=require('node:assert/strict');
const {historySeries}=require('../dashboard.js');
const archive={snapshots:[
{date:'2026-10-16',modelVersion:'v1',quotes:[{ticker:'A',coveragePoints:100,total:90}]},
{date:'2026-10-17',modelVersion:'v2',quotes:[{ticker:'A',coveragePoints:100,total:60},{ticker:'B',coveragePoints:75,total:null,partialPoints:45}]},
{date:'2026-10-18',modelVersion:'v2',quotes:[{ticker:'B',coveragePoints:100,total:61,partialPoints:61}]}
]};
const result=historySeries(archive,['A','B','A'],'v2');
assert.equal(result.length,2);
assert.deepEqual(result[0].points.map(p=>p.value),[60,null]);
assert.deepEqual(result[1].points.map(p=>p.value),[null,61]);
assert.deepEqual(historySeries(archive,['B'],'v2','partial')[0].points.map(p=>p.value),[45,61]);
assert.deepEqual(historySeries(archive,['B'],'v2','coverage')[0].points.map(p=>p.value),[75,100]);
assert.equal(historySeries(archive,['A'],'unknown')[0].points.length,0);
console.log('History: model separation, missing values and unscaled partial points passed.');
