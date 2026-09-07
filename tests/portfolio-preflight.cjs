/* Run from a complete checkout before publishing, not from a partial overlay. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const docs = path.resolve(__dirname, '../docs');
const pages = fs.readdirSync(docs).filter(file => file.endsWith('.html')).sort();
const failures = [];
const requireCheck = (label, fn) => {
  try { fn(); console.log('PASS:', label); }
  catch (error) { failures.push(label); console.error('FAIL:', label, '-', error.message); }
};
requireCheck('unchanged foundations PDF exists', () => {
  const bytes = fs.readFileSync(path.join(docs, 'assets/publications/eti/ETI_Foundations.pdf'));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), 'e87a88c4dedbd9d53978d4bb90dbfe5186aacc007950dc5a8d87a5b2a31e2578');
});
for (const file of pages) requireCheck('local destinations in ' + file, () => {
  const html = fs.readFileSync(path.join(docs, file), 'utf8');
  assert.equal((html.match(/<h1(?:\s|>)/g) || []).length, 1);
  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = match[1];
    if (/^(?:https?:|mailto:|data:)/.test(href)) continue;
    const [raw, fragment] = href.split('#');
    const name = (raw || file).replace(/^\/research-portfolio\//, '');
    const destination = path.resolve(docs, name);
    assert.ok(destination.startsWith(docs + path.sep), 'Unexpected path: ' + name);
    assert.ok(fs.existsSync(destination), 'Missing: ' + name);
    if (fragment && name.endsWith('.html')) {
      const target = fs.readFileSync(destination, 'utf8');
      assert.ok(target.includes('id="' + fragment + '"'), 'Missing anchor: ' + href);
    }
  }
});
requireCheck('embedded certificate matches pinned source', () => {
  const html = fs.readFileSync(path.join(docs, 'totient-explorer.html'), 'utf8');
  const match = html.match(/<script type="application\/json" id="trajectory-data">([\s\S]*?)<\/script>/);
  assert.ok(match, 'Certificate data missing');
  const csv = JSON.parse(match[1]);
  const bytes = Buffer.from(csv, 'utf8');
  const blob = Buffer.concat([Buffer.from('blob ' + bytes.length + '\0'), bytes]);
  assert.equal(crypto.createHash('sha1').update(blob).digest('hex'), 'd8d3c17f12b0b0264a26b22d791c696dca54764b');
  const rows = csv.trim().split(/\r?\n/).slice(1).map(line => line.split(','));
  assert.equal(rows.length, 105);
  rows.forEach((row, i) => {
    assert.equal(Number(row[0]), i);
    if (i < 104) {
      assert.equal(BigInt(row[4]) + 1n, BigInt(row[5]));
      assert.equal(row[5], rows[i + 1][1]);
    }
  });
});
if (failures.length) {
  console.error('\nNOT READY TO PUBLISH:', failures.length, 'failed checks.');
  process.exitCode = 1;
} else console.log('\nAll local publication checks passed. Verify the deployed URLs after merging.');
