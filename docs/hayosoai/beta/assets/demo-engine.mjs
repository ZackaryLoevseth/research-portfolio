/**
 * A finite, synthetic support graph. Each edge is an alternative sufficient
 * support rule: either a or b can support c; this is not a conjunction.
 * This module is pure and has no DOM, storage, network, or model dependency.
 */
export const GRAPH = Object.freeze({
  roots: Object.freeze(['a', 'b', 'k']),
  claims: Object.freeze(['c', 'd', 'i']),
  edges: Object.freeze([
    Object.freeze(['a', 'c']),
    Object.freeze(['b', 'c']),
    Object.freeze(['c', 'd']),
    Object.freeze(['k', 'i']),
  ]),
});

function validateGraph(graph) {
  if (!graph || !Array.isArray(graph.roots) || !Array.isArray(graph.claims)
      || !Array.isArray(graph.edges)) {
    throw new TypeError('A graph must contain roots, claims, and edges arrays.');
  }
  const nodes = [...graph.roots, ...graph.claims];
  if (nodes.some((node) => typeof node !== 'string' || !node)
      || new Set(nodes).size !== nodes.length) {
    throw new TypeError('Graph node IDs must be unique nonempty strings.');
  }
  const nodeSet = new Set(nodes);
  const claimSet = new Set(graph.claims);
  for (const edge of graph.edges) {
    if (!Array.isArray(edge) || edge.length !== 2
        || !nodeSet.has(edge[0]) || !claimSet.has(edge[1])) {
      throw new TypeError('Each edge must connect a known node to a claim.');
    }
  }
}

function admittedRoots(graph, activeRoots) {
  if (!Array.isArray(activeRoots)
      || activeRoots.some((root) => !graph.roots.includes(root))) {
    throw new TypeError('Active evidence must be an array of known root IDs.');
  }
  const admitted = new Set(activeRoots);
  return graph.roots.filter((root) => admitted.has(root));
}

const copyClaims = (claims) => Object.fromEntries(
  Object.entries(claims).map(([id, claim]) => [id, {
    status: claim.status,
    grounds: [...claim.grounds],
  }]),
);

const statuses = (claims) => Object.fromEntries(
  Object.entries(claims).map(([id, claim]) => [id, claim.status]),
);

/**
 * Find the least fixed point of support grounded in admitted evidence roots.
 * A claim is supported exactly when some admitted root reaches it. Recording
 * every such root explains retained support. An ungrounded cycle cannot create
 * support; propagation only adds roots that were admitted at initialization.
 */
export function evaluateSupport(graph, activeRoots) {
  validateGraph(graph);
  const admitted = new Set(admittedRoots(graph, activeRoots));
  const grounds = new Map([
    ...graph.roots.map((root) => [root, new Set(admitted.has(root) ? [root] : [])]),
    ...graph.claims.map((claim) => [claim, new Set()]),
  ]);

  let changed = true;
  while (changed) {
    changed = false;
    for (const [from, to] of graph.edges) {
      for (const root of grounds.get(from)) {
        if (!grounds.get(to).has(root)) {
          grounds.get(to).add(root);
          changed = true;
        }
      }
    }
  }

  return Object.fromEntries(graph.claims.map((claim) => [claim, {
    status: grounds.get(claim).size ? 'supported' : 'review',
    grounds: graph.roots.filter((root) => grounds.get(claim).has(root)),
  }]));
}

function downstreamClaims(graph, root) {
  const reached = new Set([root]);
  const queue = [root];
  for (let index = 0; index < queue.length; index += 1) {
    for (const [from, to] of graph.edges) {
      if (from === queue[index] && !reached.has(to)) {
        reached.add(to);
        queue.push(to);
      }
    }
  }
  return new Set(graph.claims.filter((claim) => reached.has(claim)));
}

export function createInitialState(graph = GRAPH) {
  const claims = evaluateSupport(graph, graph.roots);
  return { activeRoots: [...graph.roots], claims, history: [] };
}

/**
 * Apply one withdrawal to the support-aware state. Comparison procedures use
 * the same pre-event claim statuses and evidence change; their results never
 * feed back into the actual state. A repeated withdrawal skips comparison.
 * 'review' means no recorded support remains, not that a claim is false.
 */
export function withdrawRoot(state, root, graph = GRAPH) {
  validateGraph(graph);
  if (!graph.roots.includes(root)) {
    throw new RangeError(`Unknown evidence root: ${root}`);
  }
  const activeRootsBefore = admittedRoots(graph, state.activeRoots);
  const noChange = !activeRootsBefore.includes(root);
  const activeRootsAfter = activeRootsBefore.filter((id) => id !== root);
  const before = copyClaims(state.claims);
  const after = noChange ? copyClaims(before) : evaluateSupport(graph, activeRootsAfter);
  const changes = graph.claims.filter(
    (claim) => before[claim].status === 'supported' && after[claim].status === 'review',
  );
  const retained = graph.claims.filter(
    (claim) => before[claim].status === 'supported' && after[claim].status === 'supported',
  );

  let comparisons = null;
  if (!noChange) {
    const descendants = downstreamClaims(graph, root);
    comparisons = {
      unchanged: statuses(before),
      descendants: Object.fromEntries(graph.claims.map((claim) => [claim,
        before[claim].status === 'supported' && descendants.has(claim)
          ? 'review' : before[claim].status,
      ])),
      grounded: statuses(after),
    };
  }

  const event = {
    root,
    noChange,
    activeRootsBefore,
    activeRootsAfter: [...activeRootsAfter],
    before,
    after: copyClaims(after),
    changes,
    retained,
    comparisons,
  };
  return {
    activeRoots: activeRootsAfter,
    claims: after,
    history: [...state.history, event],
  };
}

/** Reset means a fresh initial state, including an empty local history. */
export function resetState(graph = GRAPH) {
  return createInitialState(graph);
}
