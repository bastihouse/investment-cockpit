const assert=require('node:assert/strict');
const {segmentKey,selectSamples}=require('../research_next.js');
const base={modelVersion:'v1',profile:'operating',coverage:85,components:'valuation|growth|quality|risk',growthBasis:'quarterly-yoy',horizonMonths:6,partition:'test'};
const rows=[base,{...base,coverage:55},{...base,modelVersion:'v2'},{...base,horizonMonths:12},{...base,partition:'development'}];
assert.equal(selectSamples({retrospective:{samples:rows}},{segment:segmentKey(base)}).length,1);
assert.notEqual(segmentKey(base),segmentKey({...base,modelVersion:'v2'}));
assert.equal(selectSamples({observed:{samples:[{...base,partition:undefined}]}},{kind:'observed',segment:segmentKey(base)}).length,1);
assert.deepEqual(selectSamples(null,{}),[]);
console.log('Score diagnostic segments: model, coverage, horizon and time partition remain separated.');
