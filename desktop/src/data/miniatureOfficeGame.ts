import { OFFICE_FLOORS } from './office';

export interface MeetingRoutingResult {
  leadFloor: string;
  supportFloors: string[];
  transcript: string[];
  summary: string;
}

const keywordRoutes = [
  {
    keywords: ['ui', 'ux', 'frontend', 'react', 'electron', 'interface', 'pixel', 'game'],
    leadFloor: 'TypeScript Floor',
    supportFloors: ['HTML Floor', 'CSS Floor']
  },
  {
    keywords: ['automation', 'agent', 'governance', 'workflow', 'python', 'orchestration'],
    leadFloor: 'Python Floor',
    supportFloors: ['PowerShell Floor', 'Bash Floor']
  },
  {
    keywords: ['security', 'drift', 'virus', 'honeypot', 'hardening', 'native'],
    leadFloor: 'Rust Floor',
    supportFloors: ['C Floor', 'Bash Floor']
  },
  {
    keywords: ['database', 'sql', 'analytics', 'ledger', 'memory', 'data'],
    leadFloor: 'SQL Floor',
    supportFloors: ['Python Floor', 'R Floor']
  },
  {
    keywords: ['language', 'compiler', 'dsl', 'tarl', 'thirsty', 'kernel'],
    leadFloor: 'Thirsty-Lang Floor',
    supportFloors: ['TARL Floor', 'Prolog Floor']
  },
  {
    keywords: ['mobile', 'android', 'kotlin', 'jvm'],
    leadFloor: 'Kotlin Floor',
    supportFloors: ['Java Floor', 'TypeScript Floor']
  }
];

const pickOne = <T,>(values: T[]) => values[Math.floor(Math.random() * values.length)];

export const arrivalLines = [
  'Good morning, office.',
  'Morning, crew. Let us build something dangerous.',
  'Time to wake the tower up.',
  'Alright. Nobody drift today.'
];

export const lobbyLines = [
  'Lobby is clear. Elevator is waiting.',
  'The whole tower is humming already.',
  'City Archivists logged the morning roll call.'
];

export const ceoDeskLines = [
  'CEO floor online. Conference room is available.',
  'You can call a meeting or roam the building.',
  'The tower is idle until you assign the next build.'
];

export const easterEggsByFloor: Record<string, string[]> = {
  'Python Floor': ['A rubber duck sits beside a half-finished automaton blueprint.'],
  'TypeScript Floor': ['A tiny neon sign reads: "Undefined behavior not welcome."'],
  'Rust Floor': ['Someone mounted a microscopic shield over the coffee machine.'],
  'Go Floor': ['A fan spins over a whiteboard filled with worker pool jokes.'],
  'Markdown Floor': ['A framed note says: "Documentation is a kindness weapon."'],
  'Thirsty-Lang Floor': ['A sealed drawer is labeled: "Do not open before language sentience."'],
  'TARL Floor': ['A glowing brass plaque reads: "The rules remember everything."']
};

export const getFloorDialogue = (floorName: string) => {
  const floor = OFFICE_FLOORS.find((candidate) => candidate.name === floorName) || OFFICE_FLOORS[0];
  return [
    `${floor.head}: We keep ${floor.specialty.toLowerCase()} stable before lunch.`,
    `${pickOne(floor.agents)}: I am on ticket rotation, but I heard the CEO floor is spinning up.`,
    `${pickOne(floor.agents)}: If the conference room calls, we move immediately.`,
    `${floor.head}: The tower looks calm, but calm is usually temporary.`,
    `${pickOne(floor.agents)}: I buried an easter egg in here. I am not telling you where.`
  ];
};

export const buildLoungeExchange = () => {
  const floorA = pickOne(OFFICE_FLOORS);
  let floorB = pickOne(OFFICE_FLOORS);
  if (floorB.name === floorA.name) {
    floorB = OFFICE_FLOORS[(floorA.id + 3) % OFFICE_FLOORS.length];
  }

  return [
    `${floorA.head}: I swear the CEO floor only calls when everything is on fire.`,
    `${floorB.head}: Better that than letting drift settle in the walls.`,
    `${pickOne(floorA.agents)}: I am off script for five minutes. That is luxury here.`,
    `${pickOne(floorB.agents)}: Somebody hid another easter egg near the elevator again.`
  ];
};

export const routeMeetingRequest = (request: string): MeetingRoutingResult => {
  const normalizedRequest = request.toLowerCase();
  const matchedRoute =
    keywordRoutes.find((route) => route.keywords.some((keyword) => normalizedRequest.includes(keyword))) ||
    keywordRoutes[0];
  const leadFloor = OFFICE_FLOORS.find((floor) => floor.name === matchedRoute.leadFloor) || OFFICE_FLOORS[0];
  const supportFloors = matchedRoute.supportFloors
    .map((floorName) => OFFICE_FLOORS.find((floor) => floor.name === floorName))
    .filter((floor): floor is (typeof OFFICE_FLOORS)[number] => Boolean(floor));

  const transcript = [
    `${leadFloor.head}: This build smells like ${leadFloor.specialty.toLowerCase()}. My floor should lead.`,
    ...supportFloors.map(
      (floor) => `${floor.head}: ${floor.specialty} supports the lead cleanly. We will join the assignment.`
    ),
    `${leadFloor.head}: Fine. We split the work, keep the hallway clear, and dispatch immediately.`
  ];

  return {
    leadFloor: leadFloor.name,
    supportFloors: supportFloors.map((floor) => floor.name),
    transcript,
    summary: `${leadFloor.name} leads. ${supportFloors.map((floor) => floor.name).join(', ')} support.`
  };
};
