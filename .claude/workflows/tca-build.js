export const meta = {
  name: 'tca-build',
  description: 'Build a TCA domain from an obligation: the architect graphs it, forge specialists build the nodes in dependency order under the gate, the reviewer reports for coverage. A forge gap routes back to the architect to replan.',
  phases: [
    { title: 'Architect', detail: 'graph the obligation' },
    { title: 'Forge', detail: 'build each partition in dependency order, gated' },
    { title: 'Replan', detail: 'architect re-graphs around a gap' },
    { title: 'Review', detail: 'report every deviation for coverage' },
  ],
}

// ---------------------------------------------------------------------------
// TCA in vanilla JavaScript. The orchestration's state is built from the same
// catalog the agents build to. Construction is the proof: a smart constructor
// validates and freezes, so an illegal value (an out-of-catalog kind, an edge
// to a missing node, a cyclic graph, a non-disjoint forge result) has no
// representation. The build order is a derivation over the graph's edges, not a
// hand-authored list. The forge result is a disjoint union selected by
// structure, with no tag. The one imperative part is the shell that meets time:
// it drives the construction graph in its derived order and emits effects after
// proof; it does not author a sequence.
//
// The Workflow sandbox runs plain JS with no imports, so there is no Zod here.
// In a TypeScript app the same shapes are a Zod schema (parse-don't-validate,
// `z.union` for tagless selection, `.brand` for scalars) plus its inferred
// static type. The pattern is the constant; the substrate is what changes.
// ---------------------------------------------------------------------------

class TCAError extends Error {}

// --- semantic scalars: a frozen, validated wrapper. Construction is the proof.
const scalar = (name, validate) =>
  class {
    constructor(root) {
      const problem = validate(root)
      if (problem) throw new TCAError(name + ': ' + problem + ' (got ' + JSON.stringify(root) + ')')
      this.root = root
      Object.freeze(this)
    }
  }
const text = (name) => scalar(name, (v) => (typeof v === 'string' && v.trim().length > 0 ? null : 'must be non-empty text'))
const oneOf = (name, members) => scalar(name, (v) => (members.includes(v) ? null : 'must be one of ' + members.join(', ')))

const CATALOG = [
  'semantic scalar', 'collection', 'frozen model', 'union', 'derivation', 'boundary model',
  'domain event', 'active model', 'service', 'route', 'config', 'composition root', 'projection',
]
const FORGE = ['forge-domain', 'forge-active', 'forge-config', 'forge-route', 'forge-service', 'forge-main']

const Obligation = text('Obligation')
const NodeName = text('NodeName')
const FilePath = text('FilePath')
const FieldSpec = text('FieldSpec')
const GapMeaning = text('GapMeaning')
const ConstructKind = oneOf('ConstructKind', CATALOG) // the catalog as a closed value space
const ForgeAgent = oneOf('ForgeAgent', FORGE)

// --- frozen model: one node of the construction graph.
class Node {
  constructor(raw) {
    this.name = new NodeName(raw.name)
    this.kind = new ConstructKind(raw.kind)
    this.agent = new ForgeAgent(raw.agent)
    this.file = new FilePath(raw.file)
    this.fields = new FieldSpec(raw.fields)
    this.dependsOn = Object.freeze((raw.depends_on || []).map((d) => new NodeName(d)))
    Object.freeze(this)
  }
}

// --- frozen model: the construction graph. Its existence proves the plan is
// well formed: every node is a catalog construct, every edge resolves to a real
// node, and the graph is acyclic. The build order is a derivation over the
// edges, so the edges are the build order rather than a hardcoded layer list.
class ConstructionGraph {
  constructor(rawNodes) {
    this.nodes = Object.freeze((rawNodes || []).map((n) => new Node(n)))
    const names = new Set(this.nodes.map((n) => n.name.root))
    for (const node of this.nodes)
      for (const dep of node.dependsOn)
        if (!names.has(dep.root)) throw new TCAError('edge to a node that does not exist: ' + dep.root)
    void this.partitions // run the derivation once, so a cyclic graph has no representation
    Object.freeze(this)
  }

  // derivation: the forge partitions in dependency order, pure and storing
  // nothing. Each forge specialist builds its whole partition; partitions are
  // ordered so a partition's cross-partition dependencies are built before it.
  get partitions() {
    const byAgent = new Map()
    for (const node of this.nodes) {
      if (!byAgent.has(node.agent.root)) byAgent.set(node.agent.root, [])
      byAgent.get(node.agent.root).push(node)
    }
    const agentOf = new Map(this.nodes.map((n) => [n.name.root, n.agent.root]))
    const needs = new Map([...byAgent.keys()].map((a) => [a, new Set()]))
    for (const node of this.nodes)
      for (const dep of node.dependsOn) {
        const depAgent = agentOf.get(dep.root)
        if (depAgent && depAgent !== node.agent.root) needs.get(node.agent.root).add(depAgent)
      }
    const order = []
    const built = new Set()
    while (order.length < byAgent.size) {
      const ready = [...byAgent.keys()].filter((a) => !built.has(a) && [...needs.get(a)].every((d) => built.has(d)))
      if (ready.length === 0) throw new TCAError('cyclic dependency between partitions')
      for (const a of ready) { order.push(a); built.add(a) }
    }
    return Object.freeze(order.map((a) => Object.freeze({ agent: new ForgeAgent(a), nodes: Object.freeze(byAgent.get(a)) })))
  }
}

// --- disjoint union, selected by structure with no tag: a forge run is either a
// set of built files or a gap. Construction lands exactly one; each variant
// carries its own isTerminal derivation, read off the value rather than switched.
class Built {
  constructor(files) { this.files = Object.freeze(files.map((f) => new FilePath(f))); Object.freeze(this) }
  get isTerminal() { return true }
}
class Gap {
  constructor(meaning) { this.meaning = new GapMeaning(meaning); Object.freeze(this) }
  get isTerminal() { return false }
}
const landOutcome = (raw) => {
  const hasGap = typeof raw.gap_meaning === 'string' && raw.gap_meaning.trim().length > 0
  const hasFiles = Array.isArray(raw.files) && raw.files.length > 0
  if (hasGap === hasFiles) throw new TCAError('forge result is not disjoint: it is a build or a gap, not both or neither')
  return hasGap ? new Gap(raw.gap_meaning) : new Built(raw.files)
}

// --- projection: typed truth leaving the graph as the prompt the model reads.
const DOCS = 'docs/proofs-and-graph.md (lens 1), docs/type-construction-architecture.md, docs/build-patterns.md, docs/program-topology.md'
const architectPrompt = (obligationValue, gap) =>
  'Design the TCA construction graph for this obligation. First read ' + DOCS + '.' +
  (gap ? '\n\nA forge agent hit a GAP: ' + gap.meaning.root + '\nReplan: locate the construct that already carries this meaning, or specify a new construct to gate through construction-as-proof. Reissue the full graph.' : '') +
  '\n\nOBLIGATION:\n' + obligationValue.root
const forgePrompt = (partition) =>
  'Build your partition of the construction graph as pure TCA Python, writing each file at its given path. Read docs/build-patterns.md and follow its examples. Before composing a dependency and after writing each file, settle it on the substrate (uv run python .claude/scripts/tca_gate.py --check FILE, and uv run basedpyright FILE) and fix until clean. If a node needs a meaning no construct carries, leave files empty and name the missing meaning in gap_meaning; otherwise list the files you wrote and leave gap_meaning empty.\n\nNODES:\n' +
  JSON.stringify(
    partition.nodes.map((n) => ({ name: n.name.root, kind: n.kind.root, file: n.file.root, fields: n.fields.root, depends_on: n.dependsOn.map((d) => d.root) })),
    null,
    2,
  )

// --- the forced typed terminal. The plan's kind is the closed catalog, so the
// architect cannot name a non-construct; the forge lands files xor a gap.
const GRAPH_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    nodes: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          name: { type: 'string' },
          kind: { type: 'string', enum: CATALOG },
          agent: { type: 'string', enum: FORGE },
          file: { type: 'string' },
          fields: { type: 'string' },
          depends_on: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'kind', 'agent', 'file', 'fields', 'depends_on'],
      },
    },
  },
  required: ['nodes'],
}
const FORGE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    files: { type: 'array', items: { type: 'string' } },
    gap_meaning: { type: 'string' },
  },
  required: ['files', 'gap_meaning'],
}

// The build target is the obligation, passed in as args at invocation. It states
// certainties and physics in domain language and names no construct: the architect
// derives the constructs from it. The engine is generic and carries no scenario;
// test obligations are passed in as args at invocation, never hardcoded here.
// args arrives as a string: either the obligation text itself, or a JSON object
// carrying an `obligation` field. Both forms resolve to the obligation text.
const obligationFromArgs = (a) => {
  if (typeof a !== 'string' || a.trim().length === 0) return null
  try {
    const parsed = JSON.parse(a)
    if (parsed && typeof parsed === 'object' && typeof parsed.obligation === 'string') return parsed.obligation
  } catch (_) {
    // args is the obligation text itself, not JSON. Fall through.
  }
  return a
}
const target = obligationFromArgs(args)
if (!target) throw new TCAError('no obligation: invoke with args set to the obligation text')
const obligation = new Obligation(target)

const graphFrom = async (gap) =>
  new ConstructionGraph(
    (await agent(architectPrompt(obligation, gap), { agentType: 'tca-architect', schema: GRAPH_SCHEMA, label: gap ? 'architect-replan' : 'architect', phase: gap ? 'Replan' : 'Architect' })).nodes,
  )

// --- the imperative shell: the one node where the graph meets time. It drives
// the construction graph in its derived order, lands each forge run as a proven
// outcome, reads the outcome's own isTerminal derivation, and on a gap routes
// back to the architect. Effects after proof. It drives the graph; it does not
// author the sequence, which is the graph's edges.
async function forgeGraph(graph, roundsLeft) {
  const outcomes = []
  for (const partition of graph.partitions) {
    phase('Forge')
    const raw = await agent(forgePrompt(partition), { agentType: partition.agent.root, schema: FORGE_SCHEMA, label: partition.agent.root, phase: 'Forge' })
    const outcome = landOutcome(raw)
    outcomes.push(outcome)
    if (!outcome.isTerminal) {
      if (roundsLeft <= 0) return { graph, outcomes }
      log('forge gap: ' + outcome.meaning.root + ' -> architect replans')
      return forgeGraph(await graphFrom(outcome), roundsLeft - 1)
    }
  }
  return { graph, outcomes }
}

phase('Architect')
const initialGraph = await graphFrom(null)
log('architect graphed ' + initialGraph.nodes.length + ' nodes in ' + initialGraph.partitions.length + ' partitions')

const result = await forgeGraph(initialGraph, 2)
const builtFiles = result.outcomes.filter((o) => o.isTerminal).flatMap((o) => o.files.map((f) => f.root))

phase('Review')
const review = await agent(
  'Read the TCA just built and report every deviation, for coverage, each tagged with which of the four breaks and a confidence. Run uv run python .claude/scripts/tca_gate.py --check on each .py file and uv run basedpyright, take the gate findings as ground, then judge the semantic residue: vacuous names, a vocabulary that should be a scalar or has fused axes, disjointness by constructing the minimal payloads and running them, and whether each construct discharges the obligation. Files built: ' + JSON.stringify(builtFiles),
  { agentType: 'tca-review', label: 'review', phase: 'Review' },
)

return { nodes: result.graph.nodes.map((n) => n.name.root), partitions: result.graph.partitions.length, builtFiles, review }
