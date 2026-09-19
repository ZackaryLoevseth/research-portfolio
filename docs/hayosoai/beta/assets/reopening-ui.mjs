import {createProbeState, updateProbeState, setCoverage, probeSnapshot} from './reopening-engine.mjs';
import words from './reopening-strings.mjs';

const format = (template, values) => Object.entries(values).reduce((text, [key, value]) => text.replaceAll(`{${key}}`, value), template);

/** Mount once per root. No fetch, persistence, model calls, or external actions. */
export function mountReopening(root, w = words) {
  if (root.dataset.reopeningMounted === 'true') return;
  root.dataset.reopeningMounted = 'true';
  let state = createProbeState();
  const $ = selector => root.querySelector(selector);
  const status = (selector, value) => {
    const node = $(selector);
    node.textContent = w[value];
    node.dataset.status = value;
  };
  const summary = event => event.kind === 'coverage'
    ? format(w.coverageChanged, {coverage: w[event.coverage === 'partial' ? 'partialLabel' : 'completeLabel'], route: w[event.after.assessment.disposition]})
    : format(w.changed, {
      changes: Object.entries(event.changes).map(([id, value]) => `${id}: ${w[value]}`).join('; '),
      claim: w[event.after.claim], route: w[event.after.assessment.disposition],
    });
  function render(reset = false) {
    const {record} = state;
    const result = probeSnapshot(record);
    for (const id of ['p', 'q', 'r']) {
      const supported = record.premises[id] === 'supported';
      $(`[data-reopening-premise="${id}"]`).textContent = w[record.premises[id]];
      const control = $(`[data-reopening-toggle="${id}"]`);
      control.textContent = format(w[supported ? 'withdraw' : 'restore'], {id});
      control.classList.toggle('is-absent', !supported);
    }
    status('[data-reopening-claim]', result.claim);
    status('[data-reopening-route]', result.assessment.disposition);
    status('[data-reopening-comparison="a"]', result.assessment.disposition);
    status('[data-reopening-comparison="b"]', result.comparison.disposition);
    $('[data-reopening-claim-reason]').textContent = w[result.claim === 'supported' ? 'jointLive' : 'jointLost'];
    $('[data-reopening-ground-summary]').textContent = result.assessment.remaining_support_sets.length
      ? format(w.liveGrounds, {grounds: result.assessment.remaining_support_sets.map(ground => ground.join(' AND ')).join(' OR ')}) : w.noGrounds;
    $('[data-reopening-route-reason]').textContent = w.routeReasons[result.assessment.disposition];
    $('[data-reopening-partial]').checked = record.coverage === 'partial';
    $('[data-reopening-coverage]').textContent = w[record.coverage === 'partial' ? 'partialLabel' : 'completeLabel'];
    $('[data-reopening-announcement]').textContent = reset ? w.resetMessage : state.history.length ? summary(state.history.at(-1)) : w.initial;
    $('[data-reopening-announcement]').classList.toggle('has-review', result.claim !== 'supported');
    $('[data-reopening-record]').textContent = JSON.stringify(record, null, 2);
    const history = state.history.map(event => summary(event));
    $('[data-reopening-history]').replaceChildren(...(history.length ? history : [w.initialHistory]).map(text => {
      const node = root.ownerDocument.createElement('li'); node.textContent = text; return node;
    }));
  }
  for (const button of root.querySelectorAll('[data-reopening-toggle]')) {
    button.disabled = false;
    button.addEventListener('click', () => {
      const id = button.dataset.reopeningToggle;
      state = updateProbeState(state, {[id]: state.record.premises[id] === 'supported' ? 'withdrawn' : 'supported'});
      render();
    });
  }
  $('[data-reopening-partial]').disabled = false;
  $('[data-reopening-partial]').addEventListener('change', event => {
    state = setCoverage(state, event.target.checked ? 'partial' : 'complete_within_declared_scope');
    render();
  });
  $('[data-reopening-reset]').disabled = false;
  $('[data-reopening-reset]').addEventListener('click', () => {state = createProbeState(); render(true);});
  render();
  return {getState: () => structuredClone(state)};
}

if (typeof document !== 'undefined') {
  for (const root of document.querySelectorAll('[data-reopening-demo]')) mountReopening(root);
}
