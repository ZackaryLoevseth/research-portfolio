const test = require('node:test');
const assert = require('node:assert/strict');
const {closure, patch, check} = require('../docs/correction.js');
for (const [roots, expected] of [[[],[]],[['A'],['C','D']],[['B'],['C','D']],[['A','B'],['C','D']]]) {
 test('grounded closure '+JSON.stringify(roots),()=>assert.deepEqual(closure(roots),expected));
}
for (const [roots, expected] of [[[],[]],[['A'],['C','D']],[['B'],[]],[['A','B'],[]]]) {
 test('withdrawal patch '+JSON.stringify(roots),()=>assert.deepEqual(patch(roots),expected));
}
test('cycles without a grounded entry do not derive claims',()=>assert.deepEqual(closure([], [{premises:['D'],head:'C'},{premises:['C'],head:'D'}]),[]));
test('conjunctive support requires every premise',()=>assert.deepEqual(closure(['A'],[{premises:['A','B'],head:'C'}]),[]));
test('summary merges incompatible corrections',()=>{const r=check('summary');assert.equal(r.occupiedSymbols,1);assert.equal(r.commonCorrectionExists,false);assert.deepEqual(r.groups[0].conflict,['C','D']);});
test('source-aware representation separates both responses',()=>{const r=check('support');assert.equal(r.occupiedSymbols,2);assert.equal(r.commonCorrectionExists,true);assert.deepEqual(r.groups.map(g=>g.requiredUnion),[[],['C','D']]);});
test('invalid representation rejected',()=>assert.throws(()=>check('unknown'),TypeError));
