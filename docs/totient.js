/* Presentation of the pinned F104 CSV; exact values remain strings. */
'use strict';
(() => {
  const data = document.getElementById('trajectory-data');
  if (!data) return;
  // This pinned certificate CSV has no quoted fields or commas within fields.
  const lines = JSON.parse(data.textContent).trim().split(/\r?\n/);
  const headers = lines.shift().split(',');
  if (headers.join(',') !== 'index,n,is_prime,factorization,phi_n,next_n') throw new Error('Unexpected CSV schema');
  const rows = lines.map(line => {
    const values = line.split(',');
    if (values.length !== headers.length) throw new Error('Malformed certificate row');
    return Object.fromEntries(headers.map((key, i) => [key, values[i]]));
  });
  if (rows.length !== 105 || rows[0].n !== '400000287233629' || rows[104].n !== '27515203921') {
    throw new Error('Unexpected trajectory data; controls remain disabled.');
  }
  rows.forEach((r, i) => {
    if (Number(r.index) !== i || !/^\d+$/.test(r.n)) throw new Error('Invalid trajectory row');
    if (i < 104 && (BigInt(r.phi_n) + 1n !== BigInt(r.next_n) || r.next_n !== rows[i + 1].n)) {
      throw new Error('Broken trajectory transition');
    }
  });
  const el = id => document.getElementById(id);
  const pretty = value => value.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  const controls = ['step', 'previous', 'next', 'terminal'];
  controls.forEach(id => { el(id).disabled = false; });
  let current = 0;
  function render(index) {
    current = Math.max(0, Math.min(104, Math.trunc(index)));
    const row = rows[current];
    el('step').value = String(current);
    el('step-label').textContent = String(current);
    el('step-index').textContent = String(current);
    el('exact-n').textContent = pretty(row.n);
    el('prime-status').textContent = current === 104 ? 'First prime reached · stop here' : 'Composite · continue the iteration';
    el('factors').textContent = row.factorization.split(' * ').map(f => f.split('^').map((v, i) => i ? v : pretty(v)).join('^')).join(' × ');
    el('phi').textContent = current === 104 ? 'Not evaluated: the stopping condition is met.' : pretty(row.phi_n);
    el('next-n').textContent = current === 104 ? 'Stop at the first prime.' : pretty(row.next_n);
    el('previous').setAttribute('aria-disabled', String(current === 0));
    el('next').setAttribute('aria-disabled', String(current === 104));
    el('step').setAttribute('aria-valuetext', `Iteration ${current}: ${pretty(row.n)}, ${current === 104 ? 'first prime' : 'composite'}`);
    el('step-marker').setAttribute('cx', String(65 + current / 104 * 780));
    el('step-marker').setAttribute('cy', String(280 - (Math.log10(Number(row.n)) - 10) / 5 * 235));
  }
  el('step').addEventListener('input', e => render(Number(e.target.value)));
  el('previous').addEventListener('click', () => render(current - 1));
  el('next').addEventListener('click', () => render(current + 1));
  el('terminal').addEventListener('click', () => render(104));
  render(0);
})();
