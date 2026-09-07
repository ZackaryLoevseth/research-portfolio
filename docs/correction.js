/* Finite, authored illustration of ETI Foundations §§2.2–3.1.
   No model calls, external input, analytics, or network requests. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.ETICorrection = api;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', api.init);
    else api.init();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const claims = ['C', 'D'];
  const rules = [
    { premises: ['A'], head: 'C' },
    { premises: ['B'], head: 'C' },
    { premises: ['C'], head: 'D' }
  ];
  const histories = [['A', 'B'], ['A']];
  function closure(roots, ruleSet = rules, claimSet = claims) {
    const reached = new Set(roots);
    let changed = true;
    while (changed) {
      changed = false;
      for (const rule of ruleSet) {
        if (!reached.has(rule.head) && rule.premises.every(p => reached.has(p))) {
          reached.add(rule.head);
          changed = true;
        }
      }
    }
    return claimSet.filter(c => reached.has(c));
  }
  function patch(roots, removed = 'A') {
    const surviving = new Set(closure(roots.filter(x => x !== removed)));
    return closure(roots).filter(c => !surviving.has(c));
  }
  function check(mode) {
    if (!['summary', 'support'].includes(mode)) throw new TypeError('Unknown saved representation');
    const cells = new Map();
    histories.forEach((roots, i) => {
      const symbol = mode === 'summary' ? closure(roots).join(',') : roots.slice().sort().join(',');
      if (!cells.has(symbol)) cells.set(symbol, []);
      cells.get(symbol).push({ record: i + 1, edits: patch(roots) });
    });
    const groups = Array.from(cells, ([symbol, members]) => {
      const requiredUnion = [...new Set(members.flatMap(m => m.edits))];
      const permittedIntersection = claims.filter(c => members.every(m => m.edits.includes(c)));
      const conflict = requiredUnion.filter(c => !permittedIntersection.includes(c));
      return { symbol, records: members.map(m => m.record), requiredUnion, permittedIntersection, conflict };
    });
    return { occupiedSymbols: cells.size, commonCorrectionExists: groups.every(g => g.conflict.length === 0), groups };
  }
  function init() {
    const lab = document.getElementById('correction-lab');
    if (!lab || lab.dataset.initialized) return;
    lab.dataset.initialized = 'true';
    const el = id => document.getElementById(id);
    let mode = 'summary';
    let withdrawn = false;
    function render() {
      el('saved-1').textContent = mode === 'summary'
        ? 'Which sources support them is not retained.'
        : 'Also retained: A and B are available. The support rules are shared.';
      el('saved-2').textContent = mode === 'summary'
        ? 'Which sources support them is not retained.'
        : 'Also retained: only A is available. The support rules are shared.';
      el('outcomes').hidden = !withdrawn;
      el('withdraw').textContent = withdrawn ? 'A withdrawn' : 'Withdraw A & compare';
      el('withdraw').setAttribute('aria-disabled', String(withdrawn));
      // Keep focus on the event button; repeated activation is a harmless no-op.
      [1, 2].forEach(i => {
        const graph = el('graph-' + i);
        graph.querySelectorAll('[data-source="A"]').forEach(n => n.classList.toggle('lost', withdrawn));
        graph.querySelector('[data-caption="A"]').textContent = withdrawn ? 'withdrawn' : 'admitted';
        graph.querySelectorAll('[data-claim]').forEach(n => n.classList.toggle('reopened', withdrawn && i === 2));
        graph.querySelector('[data-source="C"]').classList.toggle('lost', withdrawn && i === 2);
        el('graph-title-' + i).textContent = !withdrawn
          ? (i === 1 ? 'Record 1: A and B independently support C; C supports D.' : 'Record 2: only A supports C; C supports D. B is absent.')
          : (i === 1 ? 'Record 1: A withdrawn. B still supports C and downstream D.' : 'Record 2: A withdrawn. B absent. C and D have lost their grounded support.');
      });
      const result = check(mode);
      el('verdict').classList.toggle('conflict', withdrawn && !result.commonCorrectionExists);
      if (!withdrawn) {
        el('verdict-title').textContent = 'Both histories justify the same saved answer.';
        el('verdict-copy').textContent = 'Withdraw A to see whether the selected memory format preserves enough information for the next decision.';
        el('verdict-note').textContent = '“Supported” means grounded under the example’s admitted rules. It is not an unrestricted guarantee of truth.';
      } else if (!result.commonCorrectionExists) {
        el('verdict-title').textContent = 'One saved summary. Two required corrections.';
        el('verdict-copy').textContent = 'The summary cannot tell whether B exists. Keeping both claims supported is wrong for Record 2; reopening both is unnecessary for Record 1 under the exact-reopening contract.';
        el('verdict-note').textContent = 'Compare the “Answer + supporting sources” setup above. Retrieving the missing record would also supply additional information; it is not a correction from the same summary alone.';
      } else {
        el('verdict-title').textContent = 'The retained distinction resolves this ambiguity.';
        el('verdict-copy').textContent = 'Record 1 retains B and keeps C and D supported. Record 2 has no alternative and reopens both claim-status records. Record A’s withdrawal in either case.';
        el('verdict-note').textContent = 'This compares two saved-record setups. It assumes the supplied records and rules are correct; it does not measure a real system’s construction accuracy or performance.';
      }
      el('computed-model').textContent = JSON.stringify({ event: 'withdraw A', eventApplied: withdrawn, savedFormat: mode, ...result }, null, 2);
    }
    lab.querySelector('fieldset').disabled = false;
    el('withdraw').disabled = false;
    el('reset').disabled = false;
    lab.querySelectorAll('input[name="memory"]').forEach(input => input.addEventListener('change', () => {
      if (input.checked) { mode = input.value; render(); }
    }));
    el('withdraw').addEventListener('click', () => { if (!withdrawn) { withdrawn = true; render(); } });
    el('reset').addEventListener('click', () => {
      mode = 'summary'; withdrawn = false;
      lab.querySelector('input[value="summary"]').checked = true;
      render();
    });
    render();
  }
  return { closure, patch, check, init };
});
