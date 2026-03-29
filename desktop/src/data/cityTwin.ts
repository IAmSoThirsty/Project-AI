export interface CityTwinDistrictDefinition {
  id: string;
  label: string;
  focus: string;
  defaultFloor: string;
}

export const CITY_TWIN_DISTRICTS: CityTwinDistrictDefinition[] = [
  {
    id: 'command-core',
    label: 'Command Core',
    focus: 'Conference routing and sovereign command',
    defaultFloor: 'TARL Floor'
  },
  {
    id: 'desktop',
    label: 'Desktop Ward',
    focus: 'Renderer shells, UI, and local workstation behavior',
    defaultFloor: 'TypeScript Floor'
  },
  {
    id: 'governance',
    label: 'Governance Ring',
    focus: 'Policy, proofs, constitutional flow, and control law',
    defaultFloor: 'TARL Floor'
  },
  {
    id: 'services',
    label: 'Service Spine',
    focus: 'APIs, orchestration, and long-running substrates',
    defaultFloor: 'Python Floor'
  },
  {
    id: 'integrations',
    label: 'Integration Basin',
    focus: 'External bridges, pipelines, and tool connectors',
    defaultFloor: 'PowerShell Floor'
  },
  {
    id: 'tests',
    label: 'Validation Sector',
    focus: 'Tests, harnesses, and drift detection',
    defaultFloor: 'Python Floor'
  },
  {
    id: 'archive',
    label: 'Archive Belt',
    focus: 'Historical state, reports, and retained artifacts',
    defaultFloor: 'Markdown Floor'
  },
  {
    id: 'trunk',
    label: 'Trunk Junction',
    focus: 'Shared execution surfaces and branch convergence',
    defaultFloor: 'Bash Floor'
  }
];

export const CITY_TWIN_DISTRICT_BY_ID = Object.fromEntries(
  CITY_TWIN_DISTRICTS.map((district) => [district.id, district])
);
