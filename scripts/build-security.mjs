import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Only public advisory metadata belongs in this file. Product/CVE headings
// deliberately avoid copying a technical title that may be under revision.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { verified_on, entries } = JSON.parse(fs.readFileSync(path.join(root, 'content/security-disclosures.json'), 'utf8'));
const escape = value => String(value).replace(/[&<>"']/g, character => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[character]));
const date = value => new Intl.DateTimeFormat('en-GB', { dateStyle: 'long', timeZone: 'UTC' }).format(new Date(value + 'T00:00:00Z'));
const seen = new Set();
for (const entry of entries) {
  if (entry.status !== 'published') throw new Error('Only published disclosures may appear in the portfolio.');
  if (!/^CVE-\d{4}-\d{4,}$/.test(entry.id) || seen.has(entry.id)) throw new Error('Missing or duplicate CVE identifier.');
  if (new URL(entry.advisory_url).protocol !== 'https:') throw new Error('A public HTTPS advisory is required.');
  for (const field of ['product', 'publication_date', 'publisher', 'patched_version', 'cvss', 'severity']) {
    if (!entry[field]) throw new Error('Missing disclosure field: ' + field);
  }
  date(entry.publication_date);
  seen.add(entry.id);
}
date(verified_on);

const cards = entries.map(entry => `<article class="disclosure-card" id="${escape(entry.id.toLowerCase())}">
  <div class="disclosure-heading"><span class="status">Published advisory</span><p class="disclosure-id">${escape(entry.id)}</p></div>
  <h3>${escape(entry.product)}</h3>
  <p class="note">${escape(entry.publisher)} · <time datetime="${escape(entry.publication_date)}">${date(entry.publication_date)}</time></p>
  <dl class="disclosure-facts"><div><dt>Advisory severity</dt><dd>${escape(entry.cvss)} · ${escape(entry.severity)}</dd></div><div><dt>Patched release</dt><dd>${escape(entry.patched_version)}</dd></div></dl>
  <a class="advisory-link" href="${escape(entry.advisory_url)}">Read the public advisory</a>
</article>`).join('\n');

const start = '<!-- SECURITY-DISCLOSURES:START -->';
const end = '<!-- SECURITY-DISCLOSURES:END -->';
for (const file of ['index.html', 'security.html']) {
  const target = path.join(root, 'docs', file);
  const original = fs.readFileSync(target, 'utf8');
  if (original.split(start).length !== 2 || original.split(end).length !== 2) throw new Error('Missing disclosure markers in ' + file);
  const updated = original.replace(new RegExp(start + '[\\s\\S]*?' + end), `${start}\n<div class="disclosure-list">${cards}</div>\n${end}`)
    .replace(/<time data-advisory-checked datetime="[^"]*">[^<]*<\/time>/g, `<time data-advisory-checked datetime="${verified_on}">${date(verified_on)}</time>`);
  if (process.argv.includes('--check')) {
    if (original !== updated) throw new Error('Disclosure output is stale: run node scripts/build-security.mjs');
  } else fs.writeFileSync(target, updated);
}
console.log(process.argv.includes('--check') ? 'Published disclosure output is current.' : 'Published disclosure sections rebuilt.');
