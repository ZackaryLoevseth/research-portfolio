import { GRAPH, createInitialState, withdrawRoot, resetState } from './demo-engine.mjs?v=e4e6f1852fbb68f3';
import words from './demo-strings.mjs?v=511ff43bf954e375';

let state = createInitialState();
const $ = selector => document.querySelector(selector);
const format = (template, values) => Object.entries(values).reduce((result, [key, value]) => result.replaceAll(`{${key}}`, value), template);
const label = status => `${status === 'supported' ? '✓' : '◇'} ${words[status]}`;
const names = items => items.join(', ');
const element = (tag, text, className) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
};

function render(reset = false) {
  const event = state.history.at(-1);
  const before = event?.before || state.claims;
  $('#active-evidence').textContent = `${words.activeLabel}: ${names(state.activeRoots) || words.none}`;
  for (const root of GRAPH.roots) {
    const admitted = state.activeRoots.includes(root);
    $(`#root-${root}-status`).textContent = words[admitted ? 'admitted' : 'withdrawn'];
    const control = $(`[data-withdraw="${root}"]`);
    control.textContent = `${admitted ? words.withdraw : words.withdrawAgain} ${root}`;
    control.classList.toggle('is-absent', !admitted);
  }
  for (const node of [...GRAPH.roots, ...GRAPH.claims]) {
    const isRoot = GRAPH.roots.includes(node);
    const active = isRoot ? state.activeRoots.includes(node) : state.claims[node].status === 'supported';
    const group = $(`[data-node="${node}"]`);
    group.classList.toggle('is-inactive', !active);
    group.querySelector('.node-status').textContent = `${active ? '✓' : '◇'} ${words[isRoot ? (active ? 'admitted' : 'withdrawn') : state.claims[node].status]}`;
  }
  for (const [from, to] of GRAPH.edges) {
    const active = GRAPH.roots.includes(from) ? state.activeRoots.includes(from) : state.claims[from].status === 'supported';
    $(`[data-edge="${from}-${to}"]`).classList.toggle('is-inactive', !active);
  }
  const rows = GRAPH.claims.map(id => {
    const row = element('tr'); row.dataset.claim = id;
    const heading = element('th', id); heading.scope = 'row'; row.append(heading);
    for (const [phase, value] of [['before', before[id]], ['after', state.claims[id]]]) {
      const cell = element('td'); cell.dataset.phase = phase; cell.dataset.status = value.status; cell.dataset.label = words[phase];
      cell.append(element('span', label(value.status), `status-chip ${value.status}`)); row.append(cell);
    }
    const claim = state.claims[id];
    const reason = element('td', claim.grounds.length ? format(words.grounds, {roots: claim.grounds.join(' or ')}) : words.noGrounds, 'reason-cell');
    reason.dataset.label = words.reason;
    row.append(reason);
    return row;
  });
  $('#claim-rows').replaceChildren(...rows);
  let summary = reset ? words.resetMessage : words.initial;
  if (event) {
    summary = format(event.noChange ? words.noChangeMessage : words.withdrawnMessage, {root: event.root});
    if (!event.noChange) summary += ` ${event.changes.length ? format(words.lostMessage, {claims: names(event.changes)}) : words.retainedMessage}`;
  }
  $('#event-summary').textContent = summary;
  $('#event-summary').classList.toggle('has-review', Boolean(event?.changes.length));
  $('#comparison-event').textContent = event ? (event.noChange ? words.noChangeComparison : format(words.withdrawnMessage, {root: event.root})) : words.initialComparison;
  for (const procedure of ['unchanged', 'descendants', 'grounded']) {
    const results = $(`#comparison-${procedure}`);
    if (!event?.comparisons) {
      results.replaceChildren(element('p', event?.noChange ? words.noChange : words.initialComparison, 'awaiting'));
      continue;
    }
    const list = element('dl');
    for (const claim of GRAPH.claims) {
      const row = element('div'); row.dataset.claim = claim;
      const status = event.comparisons[procedure][claim]; row.dataset.status = status;
      row.append(element('dt', claim), element('dd', label(status), status)); list.append(row);
    }
    results.replaceChildren(list);
  }
  $('#demo-history').replaceChildren(...(state.history.length ? state.history.map((event, index) => {
    const summary = event.noChange ? words.noChange : event.changes.length ? format(words.historyChanged, {claims: names(event.changes)}) : words.historyRetained;
    return element('li', event.noChange ? `${index + 1}. ${format(words.noChangeMessage, {root: event.root})}` : `${index + 1}. ${format(words.withdrawnMessage, {root: event.root})} ${summary}.`);
  }) : [element('li', words.initialHistory)]));
}

for (const button of document.querySelectorAll('[data-withdraw]')) {
  button.disabled = false;
  button.addEventListener('click', () => {state = withdrawRoot(state, button.dataset.withdraw); render();});
}
$('#reset-demo').disabled = false;
$('#reset-demo').addEventListener('click', () => {state = resetState(); render(true);});
render();
