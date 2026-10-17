const assert=require('node:assert/strict');
const {reconstructionSeries}=require('../reconstruction.js');
const data={stocks:[{ticker:'A',points:[{date:'2021-10-31',partialPoints:60,coveragePoints:85,parts:{quality:20}},{date:'2021-11-30',partialPoints:0,coveragePoints:0,parts:{quality:null}}]}]};
assert.deepEqual(reconstructionSeries(data,['A','A'],'partial')[0].points.map(p=>p.value),[60,null]);
assert.deepEqual(reconstructionSeries(data,['A'],'quality')[0].points.map(p=>p.value),[20,null]);
assert.deepEqual(reconstructionSeries(data,['A'],'coverage')[0].points.map(p=>p.value),[85,0]);
assert.equal(reconstructionSeries(data,['missing'])[0].points.length,0);
console.log('Reconstruction UI: missing evidence stays missing; partial values remain unscaled.');
