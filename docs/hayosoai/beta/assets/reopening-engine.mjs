/** Finite support bookkeeping adapted from the supplied Reopening Probe 0.1.0.
 * AND within each sufficient ground, OR between grounds. No model or external actions.
 * A missing support is neither a false proposition nor permission to act.
 */
export const PREMISE_STATES = Object.freeze(['supported', 'withdrawn', 'refuted']);
export const COVERAGES = Object.freeze(['complete_within_declared_scope', 'partial']);
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const copy = value => JSON.parse(JSON.stringify(value));

export function validateRecord(record) {
  if (!isObject(record) || !['id', 'candidate', 'premises', 'grounds', 'coverage'].every(key => Object.hasOwn(record, key))) {
    throw new TypeError('Record requires id, candidate, premises, grounds, and coverage');
  }
  if (typeof record.id !== 'string' || !record.id || typeof record.candidate !== 'string' || !record.candidate) {
    throw new TypeError('Record and candidate require nonempty names');
  }
  if (!isObject(record.premises) || Object.entries(record.premises).some(([id, state]) => !id || !PREMISE_STATES.includes(state))) {
    throw new TypeError('Premises require explicit supported, withdrawn, or refuted states');
  }
  if (!COVERAGES.includes(record.coverage)) throw new TypeError('Explicit coverage is required');
  if (!Array.isArray(record.grounds)) throw new TypeError('Grounds must be a list of sufficient sets');
  for (const ground of record.grounds) {
    if (!Array.isArray(ground) || ground.some(id => typeof id !== 'string' || !Object.hasOwn(record.premises, id)) || new Set(ground).size !== ground.length) {
      throw new TypeError('Every sufficient set must contain unique declared premise IDs');
    }
  }
}

export function assessRecord(record) {
  validateRecord(record);
  const live = record.grounds.filter(ground => ground.every(id => record.premises[id] === 'supported')).map(ground => [...ground]);
  return {
    id: record.id,
    disposition: live.length ? 'excluded_under_recorded_grounds' : record.coverage === 'complete_within_declared_scope' ? 'reconsider' : 'insufficient_record',
    remaining_support_sets: live,
    candidate_acceptance: 'not_derived',
    execution_permission: 'not_granted',
  };
}

export function reviseRecord(record, changes) {
  validateRecord(record);
  if (!isObject(changes) || Object.entries(changes).some(([id, state]) => !Object.hasOwn(record.premises, id) || !PREMISE_STATES.includes(state))) {
    throw new TypeError('Updates require declared premises and explicit valid states');
  }
  const result = copy(record);
  for (const [id, state] of Object.entries(changes)) {
    Object.defineProperty(result.premises, id, {value: state, writable: true, configurable: true, enumerable: true});
  }
  return result;
}

export function probeSnapshot(record) {
  const assessment = assessRecord(record);
  // Claim C has the supplied joint support p AND q, separate from route exclusion.
  const claim = record.premises.p === 'supported' && record.premises.q === 'supported' ? 'supported' : 'review';
  const comparison = assessRecord({...record, id: 'arrangement-b', grounds: [['p'], ['q', 'r']]});
  return {claim, assessment, comparison};
}

export function createProbeState() {
  return {
    record: {
      id: 'arrangement-a',
      candidate: 'Reconsider a research route; no external action.',
      premises: {p: 'supported', q: 'supported', r: 'supported'},
      grounds: [['p', 'q'], ['r']],
      coverage: 'complete_within_declared_scope',
    },
    history: [],
  };
}

export function updateProbeState(state, changes) {
  const record = reviseRecord(state.record, changes);
  return {
    record,
    history: [...state.history, {kind: 'premises', changes: copy(changes), before: probeSnapshot(state.record), after: probeSnapshot(record)}],
  };
}

export function setCoverage(state, coverage) {
  if (!COVERAGES.includes(coverage)) throw new TypeError('Explicit coverage is required');
  const record = {...copy(state.record), coverage};
  validateRecord(record);
  return {
    record,
    history: [...state.history, {kind: 'coverage', coverage, before: probeSnapshot(state.record), after: probeSnapshot(record)}],
  };
}
