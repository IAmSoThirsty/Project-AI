import { OfficeFloor } from '../types/sovereign';

export const OFFICE_FLOORS: OfficeFloor[] = [
  {
    id: 1,
    name: 'Python Floor',
    specialty: 'Automation and orchestration',
    head: 'Aster',
    agents: ['Aster', 'Bayes', 'Cipher', 'Lint', 'Sage', 'Vector'],
    accent: '#f4ba3f',
    overview: 'Builds automation, governance glue, and experimental cognition paths.'
  },
  {
    id: 2,
    name: 'TypeScript Floor',
    specialty: 'Interface systems and typed control surfaces',
    head: 'Atlas',
    agents: ['Atlas', 'Circuit', 'Glyph', 'Patch', 'Signal', 'Thread'],
    accent: '#63b3ed',
    overview: 'Owns renderer logic, interaction models, and typed client systems.'
  },
  {
    id: 3,
    name: 'JavaScript Floor',
    specialty: 'Dynamic runtime utilities',
    head: 'Arc',
    agents: ['Arc', 'Cache', 'Flux', 'Pulse', 'Relay', 'Trace'],
    accent: '#f6e05e',
    overview: 'Handles runtime tooling, scripts, and adaptive glue layers.'
  },
  {
    id: 4,
    name: 'Rust Floor',
    specialty: 'Security and hardened systems',
    head: 'Bolt',
    agents: ['Bolt', 'Crate', 'Ferrite', 'Guard', 'Motive', 'Steel'],
    accent: '#fb7185',
    overview: 'Focuses on containment, hardened execution, and low-level resilience.'
  },
  {
    id: 5,
    name: 'Go Floor',
    specialty: 'Concurrent services and infrastructure',
    head: 'Gale',
    agents: ['Gale', 'Harbor', 'Kite', 'Marshal', 'Orbit', 'Wake'],
    accent: '#2dd4bf',
    overview: 'Builds service control planes, network-aware daemons, and parallel systems.'
  },
  {
    id: 6,
    name: 'Java Floor',
    specialty: 'Enterprise runtime systems',
    head: 'Amber',
    agents: ['Amber', 'Bridge', 'Harbor', 'Pulse', 'Rune', 'Vertex'],
    accent: '#f97316',
    overview: 'Maintains structured JVM services and long-lived substrate layers.'
  },
  {
    id: 7,
    name: 'Kotlin Floor',
    specialty: 'Modern JVM composition',
    head: 'Kestrel',
    agents: ['Kestrel', 'Lambda', 'Nova', 'Orbit', 'Scope', 'Tonic'],
    accent: '#a855f7',
    overview: 'Optimizes expressive JVM modules, mobile surfaces, and DSL work.'
  },
  {
    id: 8,
    name: 'C Floor',
    specialty: 'Native systems and tight loops',
    head: 'Copper',
    agents: ['Copper', 'Gauge', 'Mason', 'Needle', 'Switch', 'Tread'],
    accent: '#fda4af',
    overview: 'Handles native interfaces, performance-critical internals, and firmware edges.'
  },
  {
    id: 9,
    name: 'C++ Floor',
    specialty: 'High-performance engines',
    head: 'Carbon',
    agents: ['Carbon', 'Draft', 'Hinge', 'Lattice', 'Quarry', 'Spindle'],
    accent: '#c084fc',
    overview: 'Owns simulation engines, rendering cores, and performance-intensive pipelines.'
  },
  {
    id: 10,
    name: 'C# Floor',
    specialty: 'Tooling and application shells',
    head: 'Cinder',
    agents: ['Cinder', 'Facet', 'Halo', 'Ion', 'Prism', 'Vector'],
    accent: '#60a5fa',
    overview: 'Builds productive desktop tools, services, and ecosystem bridges.'
  },
  {
    id: 11,
    name: 'Swift Floor',
    specialty: 'Apple platform surfaces',
    head: 'Skylark',
    agents: ['Skylark', 'Petal', 'Satin', 'Mode', 'Tempo', 'Vale'],
    accent: '#fb7185',
    overview: 'Maintains fast, polished native experiences across Apple environments.'
  },
  {
    id: 12,
    name: 'Ruby Floor',
    specialty: 'Expressive applications and scripts',
    head: 'Rouge',
    agents: ['Rouge', 'Cameo', 'Fable', 'Lantern', 'Mercy', 'Velvet'],
    accent: '#ef4444',
    overview: 'Builds elegant workflows, scripting helpers, and narrative interfaces.'
  },
  {
    id: 13,
    name: 'PHP Floor',
    specialty: 'Web backends and legacy harmonization',
    head: 'Vesper',
    agents: ['Vesper', 'Anchor', 'Bloom', 'Ledger', 'Pillar', 'Static'],
    accent: '#818cf8',
    overview: 'Keeps legacy web surfaces coherent while modernizing their internals.'
  },
  {
    id: 14,
    name: 'Elixir Floor',
    specialty: 'Distributed coordination',
    head: 'Phoenix',
    agents: ['Phoenix', 'Beacon', 'Current', 'Loom', 'Spire', 'Tessera'],
    accent: '#c084fc',
    overview: 'Specializes in fault-tolerant, message-driven coordination systems.'
  },
  {
    id: 15,
    name: 'Haskell Floor',
    specialty: 'Formal functional reasoning',
    head: 'Sigma',
    agents: ['Sigma', 'Axiom', 'Chord', 'Monad', 'Proof', 'Tangent'],
    accent: '#94a3b8',
    overview: 'Explores high-assurance transformations and purely functional models.'
  },
  {
    id: 16,
    name: 'Lisp Floor',
    specialty: 'Metaprogramming and symbolic transformation',
    head: 'Paren',
    agents: ['Paren', 'Cloak', 'Macro', 'Muse', 'Scribe', 'Tailcall'],
    accent: '#f59e0b',
    overview: 'Shapes symbolic systems, macro tools, and reflective language machinery.'
  },
  {
    id: 17,
    name: 'Prolog Floor',
    specialty: 'Rule engines and inference',
    head: 'Verdict',
    agents: ['Verdict', 'Clause', 'Inference', 'Lattice', 'Reason', 'Unify'],
    accent: '#22c55e',
    overview: 'Works on logic, rule evaluation, and structured proof navigation.'
  },
  {
    id: 18,
    name: 'R Floor',
    specialty: 'Statistical analysis',
    head: 'Ribbon',
    agents: ['Ribbon', 'Delta', 'Metric', 'Pivot', 'Spline', 'Trend'],
    accent: '#38bdf8',
    overview: 'Analyzes datasets, trends, and research-oriented computational signals.'
  },
  {
    id: 19,
    name: 'Julia Floor',
    specialty: 'Scientific performance computing',
    head: 'Joule',
    agents: ['Joule', 'Array', 'Drift', 'Eigen', 'Phase', 'Vector'],
    accent: '#10b981',
    overview: 'Pushes numerical modeling and simulation throughput for research workloads.'
  },
  {
    id: 20,
    name: 'Bash Floor',
    specialty: 'System scripting and shell control',
    head: 'Bramble',
    agents: ['Bramble', 'Dash', 'Fork', 'Pipe', 'Prompt', 'Shell'],
    accent: '#84cc16',
    overview: 'Maintains shell flows, build scripts, and low-friction automation routes.'
  },
  {
    id: 21,
    name: 'PowerShell Floor',
    specialty: 'Windows automation and governance tooling',
    head: 'Iron',
    agents: ['Iron', 'Dispatch', 'Forge', 'Rivet', 'Torch', 'Vault'],
    accent: '#60a5fa',
    overview: 'Operates Windows-native automation, installers, and system management.'
  },
  {
    id: 22,
    name: 'Lua Floor',
    specialty: 'Embedded scripting',
    head: 'Lumen',
    agents: ['Lumen', 'Bloom', 'Feather', 'Orbit', 'Ripple', 'Spoke'],
    accent: '#a78bfa',
    overview: 'Handles embedded extension logic and lightweight runtime augmentation.'
  },
  {
    id: 23,
    name: 'SQL Floor',
    specialty: 'Data planes and query strategy',
    head: 'Quarry',
    agents: ['Quarry', 'Column', 'Index', 'Join', 'Ledger', 'Shard'],
    accent: '#2dd4bf',
    overview: 'Maintains schemas, data flows, and analytical persistence strategies.'
  },
  {
    id: 24,
    name: 'HTML Floor',
    specialty: 'Document structure and information surfaces',
    head: 'Frame',
    agents: ['Frame', 'Anchor', 'Canvas', 'Markup', 'Outline', 'Section'],
    accent: '#fb923c',
    overview: 'Shapes structural interfaces and navigable content architecture.'
  },
  {
    id: 25,
    name: 'CSS Floor',
    specialty: 'Visual systems and atmosphere',
    head: 'Velour',
    agents: ['Velour', 'Cascade', 'Grid', 'Hue', 'Keyline', 'Motion'],
    accent: '#f472b6',
    overview: 'Designs coherent presentation, motion, and visual rhythm for interfaces.'
  },
  {
    id: 26,
    name: 'JSON Floor',
    specialty: 'Schemas and machine-readable documents',
    head: 'Schema',
    agents: ['Schema', 'Archive', 'Facet', 'Ledger', 'Prism', 'Weave'],
    accent: '#fde68a',
    overview: 'Guards schemas, config documents, and portable interchange structures.'
  },
  {
    id: 27,
    name: 'YAML Floor',
    specialty: 'Declarative operations',
    head: 'Harbor',
    agents: ['Harbor', 'Indent', 'Merge', 'Node', 'Policy', 'Stack'],
    accent: '#86efac',
    overview: 'Controls declarative pipelines, deployment specs, and operator manifests.'
  },
  {
    id: 28,
    name: 'Markdown Floor',
    specialty: 'Narrative documentation',
    head: 'Quill',
    agents: ['Quill', 'Context', 'Mnemonic', 'Narrative', 'Signal', 'Tome'],
    accent: '#fbbf24',
    overview: 'Writes manuals, briefings, and structured human-readable operating knowledge.'
  },
  {
    id: 29,
    name: 'Thirsty-Lang Floor',
    specialty: 'Sovereign language invention',
    head: 'Thirst',
    agents: ['Thirst', 'Glyph', 'Kernel', 'Myth', 'Rune', 'Syntax'],
    accent: '#34d399',
    overview: 'Creates and evolves sovereign-native language constructs and semantics.'
  },
  {
    id: 30,
    name: 'TARL Floor',
    specialty: 'Governance law and rule execution',
    head: 'Galahad',
    agents: ['Galahad', 'Cerberus', 'Codex', 'Clause', 'Sentinel', 'Witness'],
    accent: '#7dd3fc',
    overview: 'Owns constitutional policy, governance proofs, and enforcement pathways.'
  }
];

export const DEFAULT_FLOOR_NAME = 'Python Floor';

export const OFFICE_FLOOR_BY_NAME = Object.fromEntries(
  OFFICE_FLOORS.map((floor) => [floor.name, floor])
);
