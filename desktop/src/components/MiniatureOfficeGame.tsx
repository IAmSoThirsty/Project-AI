import React, { useEffect, useMemo, useState } from 'react';
import { Box, Button, Stack, TextField, Typography } from '@mui/material';
import { Close, CropSquare, Minimize } from '@mui/icons-material';
import { OFFICE_FLOORS } from '../data/office';
import {
  arrivalLines,
  buildLoungeExchange,
  ceoDeskLines,
  easterEggsByFloor,
  getFloorDialogue,
  lobbyLines,
  routeMeetingRequest,
  type MeetingRoutingResult
} from '../data/miniatureOfficeGame';

type GameScene = 'arrival' | 'lobby' | 'elevator' | 'ceo' | 'explore' | 'conference';
type ArrivalPhase = 'idle' | 'driving' | 'parking' | 'walking' | 'ready';
type ExploreMode = 'floor' | 'lounge';
type ConferencePhase = 'briefing' | 'gathering' | 'deliberating' | 'dispatching';
type AssignmentStatus = 'assembling' | 'building' | 'validating' | 'completed';
type Facing = 'up' | 'down' | 'left' | 'right';

interface AssignmentLedger {
  id: string;
  request: string;
  leadFloor: string;
  supportFloors: string[];
  summary: string;
  createdAt: string;
  updatedAt: string;
  status: AssignmentStatus;
  report: string[];
}

interface PlayerPosition {
  x: number;
  y: number;
}

interface DeskSlot {
  deskX: number;
  deskY: number;
  actorX: number;
  actorY: number;
}

const GAME_SCENE_STORE_KEY = 'sovereign.game.scene';
const GAME_FLOOR_INDEX_STORE_KEY = 'sovereign.game.floor-index';
const GAME_LEDGER_STORE_KEY = 'sovereign.game.ledger';

const pixelButtonSx = {
  justifyContent: 'flex-start',
  px: 1.2,
  py: 1,
  color: '#11150f',
  bgcolor: '#f4ba3f',
  border: '3px solid #2e2712',
  borderRadius: 0,
  fontFamily: 'var(--font-code)',
  fontSize: 12,
  textTransform: 'none',
  boxShadow: '4px 4px 0 rgba(10, 13, 9, 0.92)',
  '&:hover': { bgcolor: '#f7c862' }
} as const;

const secondaryPixelButtonSx = {
  ...pixelButtonSx,
  color: '#edf2d0',
  bgcolor: '#283123',
  borderColor: '#5c6d4f',
  '&:hover': { bgcolor: '#34402e' }
} as const;

const pixelPanelSx = {
  border: '4px solid #151a13',
  bgcolor: '#1b2218',
  boxShadow: '8px 8px 0 rgba(10, 13, 9, 0.9)'
} as const;

const missionStatusTone: Record<AssignmentStatus, { label: string; color: string; background: string }> = {
  assembling: { label: 'ASSEMBLING', color: '#f5e6a6', background: '#3c3320' },
  building: { label: 'BUILDING', color: '#8ee4df', background: '#20383a' },
  validating: { label: 'VALIDATING', color: '#c4f1be', background: '#23351f' },
  completed: { label: 'COMPLETE', color: '#f6f7df', background: '#31412b' }
};

const deskSlots: DeskSlot[] = [
  { deskX: 12, deskY: 16, actorX: 16, actorY: 27 },
  { deskX: 39, deskY: 16, actorX: 43, actorY: 27 },
  { deskX: 66, deskY: 16, actorX: 70, actorY: 27 },
  { deskX: 12, deskY: 48, actorX: 16, actorY: 59 },
  { deskX: 39, deskY: 48, actorX: 43, actorY: 59 },
  { deskX: 66, deskY: 48, actorX: 70, actorY: 59 }
];

const conferenceSeats = [
  { x: 20, y: 26, facing: 'right' as Facing },
  { x: 31, y: 18, facing: 'down' as Facing },
  { x: 42, y: 26, facing: 'left' as Facing },
  { x: 53, y: 18, facing: 'down' as Facing },
  { x: 62, y: 26, facing: 'right' as Facing },
  { x: 31, y: 55, facing: 'up' as Facing },
  { x: 47, y: 61, facing: 'up' as Facing },
  { x: 63, y: 55, facing: 'up' as Facing }
];

const pickOne = <T,>(values: T[]) => values[Math.floor(Math.random() * values.length)];

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));

const createTimestamp = () =>
  new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(new Date());

const extractSearchToken = (request: string) => {
  const stopwords = new Set(['the', 'and', 'for', 'with', 'that', 'this', 'build', 'make', 'need', 'want']);
  return (
    request
      .toLowerCase()
      .split(/[^a-z0-9]+/)
      .find((token) => token.length >= 4 && !stopwords.has(token)) || ''
  );
};

const getSpawnPoint = (scene: GameScene, exploreMode: ExploreMode): PlayerPosition => {
  if (scene === 'arrival') return { x: 24, y: 70 };
  if (scene === 'lobby') return { x: 50, y: 72 };
  if (scene === 'elevator') return { x: 50, y: 66 };
  if (scene === 'ceo') return { x: 52, y: 72 };
  if (scene === 'conference') return { x: 80, y: 72 };
  return exploreMode === 'lounge' ? { x: 81, y: 70 } : { x: 48, y: 83 };
};

const getMovementBounds = (scene: GameScene, exploreMode: ExploreMode) => {
  if (scene === 'arrival') return { minX: 12, maxX: 78, minY: 56, maxY: 84 };
  if (scene === 'lobby') return { minX: 14, maxX: 82, minY: 24, maxY: 82 };
  if (scene === 'elevator') return { minX: 38, maxX: 58, minY: 28, maxY: 76 };
  if (scene === 'ceo') return { minX: 18, maxX: 80, minY: 26, maxY: 84 };
  if (scene === 'conference') return { minX: 16, maxX: 84, minY: 18, maxY: 84 };
  return exploreMode === 'lounge'
    ? { minX: 16, maxX: 86, minY: 34, maxY: 82 }
    : { minX: 12, maxX: 84, minY: 18, maxY: 86 };
};

const tilePattern = (base: string, line: string, size = 18) => ({
  bgcolor: base,
  backgroundImage: `repeating-linear-gradient(0deg, transparent 0 ${size - 2}px, ${line} ${size - 2}px ${size}px), repeating-linear-gradient(90deg, transparent 0 ${size - 2}px, ${line} ${size - 2}px ${size}px)`
});

const dottedPattern = (base: string, dot: string, size = 22) => ({
  bgcolor: base,
  backgroundImage: `radial-gradient(${dot} 14%, transparent 15%)`,
  backgroundSize: `${size}px ${size}px`
});

const WindowControls = () => (
  <Box
    sx={{
      position: 'absolute',
      inset: '0 0 auto 0',
      height: 36,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      px: 1.2,
      bgcolor: '#11150f',
      borderBottom: '4px solid #2a3324',
      WebkitAppRegion: 'drag',
      zIndex: 30
    }}
  >
    <Stack direction="row" spacing={1.2} alignItems="center">
      <Box sx={{ width: 10, height: 10, bgcolor: '#f4ba3f', border: '2px solid #151a13' }} />
      <Typography variant="caption" sx={{ color: '#f5e6a6', letterSpacing: 1.1, fontFamily: 'var(--font-code)' }}>
        THIRSTY&apos;S MINIATURE OFFICE
      </Typography>
    </Stack>
    <Stack direction="row" spacing={0.25} sx={{ WebkitAppRegion: 'no-drag' }}>
      <Button size="small" onClick={() => void window.electron?.window.minimize()} sx={{ minWidth: 0, color: '#edf2d0' }}>
        <Minimize fontSize="small" />
      </Button>
      <Button size="small" onClick={() => void window.electron?.window.maximize()} sx={{ minWidth: 0, color: '#edf2d0' }}>
        <CropSquare fontSize="small" />
      </Button>
      <Button size="small" onClick={() => void window.electron?.window.close()} sx={{ minWidth: 0, color: '#f7b7aa' }}>
        <Close fontSize="small" />
      </Button>
    </Stack>
  </Box>
);

const PixelActor = ({
  label,
  accent,
  x,
  y,
  bubble,
  facing = 'down',
  active = false,
  scale = 1
}: {
  label: string;
  accent: string;
  x: number;
  y: number;
  bubble?: string;
  facing?: Facing;
  active?: boolean;
  scale?: number;
}) => {
  const eyeOffsetX = facing === 'left' ? -4 : facing === 'right' ? 4 : 0;
  const hairColor = active ? '#f4ba3f' : '#7a5537';

  return (
    <Box
      sx={{
        position: 'absolute',
        left: `${x}%`,
        top: `${y}%`,
        width: 70,
        transform: `translate(-50%, -50%) scale(${scale})`,
        transformOrigin: 'center center',
        textAlign: 'center',
        transition: 'left 0.12s linear, top 0.12s linear',
        zIndex: 15
      }}
    >
      {bubble && (
        <Box
          sx={{
            mb: 0.8,
            px: 0.8,
            py: 0.55,
            border: '2px solid #1b1f17',
            bgcolor: '#f5e6a6',
            color: '#141812',
            fontFamily: 'var(--font-code)',
            fontSize: 11,
            lineHeight: 1.15,
            boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
          }}
        >
          {bubble}
        </Box>
      )}
      <Box sx={{ mx: 'auto', width: 26, height: 10, bgcolor: active ? 'rgba(244, 186, 63, 0.28)' : 'rgba(0, 0, 0, 0.24)' }} />
      <Box sx={{ mx: 'auto', mt: '-2px', width: 24, height: 8, bgcolor: hairColor, border: '2px solid #1b1f17' }} />
      <Box sx={{ mx: 'auto', mt: '-2px', width: 26, height: 18, bgcolor: '#f1cd99', border: '2px solid #1b1f17' }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5, mt: 0.6, pl: `${eyeOffsetX}px` }}>
          <Box sx={{ width: 3, height: 3, bgcolor: '#11150f' }} />
          <Box sx={{ width: 3, height: 3, bgcolor: '#11150f' }} />
        </Box>
      </Box>
      <Box sx={{ mx: 'auto', mt: '-1px', width: 30, height: 16, bgcolor: accent, border: '2px solid #1b1f17' }} />
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.6, mt: '-2px' }}>
        <Box sx={{ width: 6, height: 8, bgcolor: '#f1cd99', border: '2px solid #1b1f17' }} />
        <Box sx={{ width: 14, height: 8, bgcolor: accent, border: '2px solid #1b1f17' }} />
        <Box sx={{ width: 6, height: 8, bgcolor: '#f1cd99', border: '2px solid #1b1f17' }} />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.6, mt: '-2px' }}>
        <Box sx={{ width: 7, height: 10, bgcolor: '#475363', border: '2px solid #1b1f17' }} />
        <Box sx={{ width: 7, height: 10, bgcolor: '#475363', border: '2px solid #1b1f17' }} />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mt: '-2px' }}>
        <Box sx={{ width: 8, height: 5, bgcolor: '#1f251d', border: '2px solid #1b1f17' }} />
        <Box sx={{ width: 8, height: 5, bgcolor: '#1f251d', border: '2px solid #1b1f17' }} />
      </Box>
      <Typography variant="caption" sx={{ color: '#edf2d0', display: 'block', mt: 0.7, fontFamily: 'var(--font-code)' }}>
        {label}
      </Typography>
    </Box>
  );
};

const PixelFlowerPatch = ({ x, y, colors }: { x: number; y: number; colors: string[] }) => (
  <Box sx={{ position: 'absolute', left: `${x}%`, top: `${y}%`, width: 110, height: 36 }}>
    {Array.from({ length: 10 }).map((_, index) => (
      <Box
        key={index}
        sx={{
          position: 'absolute',
          left: `${(index % 5) * 18}px`,
          top: `${Math.floor(index / 5) * 14 + (index % 2) * 4}px`,
          width: 10,
          height: 10,
          bgcolor: colors[index % colors.length],
          border: '2px solid rgba(27, 31, 23, 0.35)'
        }}
      />
    ))}
  </Box>
);

const PixelPlanter = ({ x, y }: { x: number; y: number }) => (
  <Box sx={{ position: 'absolute', left: `${x}%`, top: `${y}%`, width: 52, height: 58, transform: 'translate(-50%, -50%)' }}>
    <Box sx={{ position: 'absolute', left: 10, top: 24, width: 30, height: 22, bgcolor: '#6d4a2c', border: '3px solid #1b1f17' }} />
    <Box sx={{ position: 'absolute', left: 4, top: 8, width: 40, height: 18, bgcolor: '#7db45b', border: '3px solid #1b1f17' }} />
    <Box sx={{ position: 'absolute', left: 10, top: 0, width: 28, height: 16, bgcolor: '#93cb69', border: '3px solid #1b1f17' }} />
  </Box>
);

const PixelTowerExterior = () => (
  <Box sx={{ position: 'absolute', right: '4%', top: '10%', width: 360, height: 292 }}>
    <Box sx={{ position: 'absolute', left: 48, top: 0, width: 214, height: 76, bgcolor: '#d9e7ae', border: '6px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 0, top: 48, width: 156, height: 198, bgcolor: '#d4c47b', border: '6px solid #151a13', boxShadow: '8px 8px 0 rgba(10, 13, 9, 0.88)' }} />
    <Box sx={{ position: 'absolute', right: 0, top: 48, width: 194, height: 220, bgcolor: '#d0bf72', border: '6px solid #151a13', boxShadow: '8px 8px 0 rgba(10, 13, 9, 0.88)' }} />
    <Box sx={{ position: 'absolute', left: 130, top: 70, width: 32, height: 182, bgcolor: '#775b39', borderLeft: '6px solid #151a13', borderRight: '6px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 34, top: 98, width: 76, height: 24, bgcolor: '#1f241c', border: '4px solid #151a13', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Typography variant="caption" sx={{ color: '#f4ba3f', fontFamily: 'var(--font-code)', letterSpacing: 1 }}>
        HQ
      </Typography>
    </Box>
    <Box sx={{ position: 'absolute', left: 44, top: 142, width: 58, height: 92, bgcolor: '#231910', border: '5px solid #151a13' }} />
    {Array.from({ length: 14 }).map((_, index) => (
      <Box
        key={index}
        sx={{
          position: 'absolute',
          left: index < 4 ? 28 + index * 22 : 186 + ((index - 4) % 4) * 24,
          top: index < 4 ? 128 : 100 + Math.floor((index - 4) / 4) * 44,
          width: 18,
          height: 16,
          bgcolor: index % 3 === 0 ? '#f2df95' : '#95dbef',
          border: '3px solid #151a13'
        }}
      />
    ))}
  </Box>
);

const PixelCar = ({ left, top }: { left: number; top: number }) => (
  <Box sx={{ position: 'absolute', left: `${left}%`, top: `${top}%`, width: 92, height: 128, transform: 'translate(-50%, -50%) rotate(-15deg)', transition: 'left 0.9s steps(8), top 0.9s steps(8)', zIndex: 12 }}>
    <Box sx={{ position: 'absolute', left: 22, top: 0, width: 46, height: 18, bgcolor: '#f0d98e', border: '4px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 14, top: 16, width: 62, height: 90, bgcolor: '#d64b42', border: '4px solid #151a13', boxShadow: '6px 6px 0 rgba(10, 13, 9, 0.88)' }} />
    <Box sx={{ position: 'absolute', left: 24, top: 28, width: 42, height: 18, bgcolor: '#9ee8ff', border: '3px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 24, top: 54, width: 42, height: 18, bgcolor: '#9ee8ff', border: '3px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 8, top: 24, width: 16, height: 28, bgcolor: '#1b1f17', border: '4px solid #8d979d' }} />
    <Box sx={{ position: 'absolute', right: 8, top: 24, width: 16, height: 28, bgcolor: '#1b1f17', border: '4px solid #8d979d' }} />
    <Box sx={{ position: 'absolute', left: 8, bottom: 20, width: 16, height: 28, bgcolor: '#1b1f17', border: '4px solid #8d979d' }} />
    <Box sx={{ position: 'absolute', right: 8, bottom: 20, width: 16, height: 28, bgcolor: '#1b1f17', border: '4px solid #8d979d' }} />
  </Box>
);

const PixelDesk = ({ x, y, accent, lit = false }: { x: number; y: number; accent: string; lit?: boolean }) => (
  <Box sx={{ position: 'absolute', left: `${x}%`, top: `${y}%`, width: 96, height: 84, transform: 'translate(-50%, -50%)' }}>
    <Box sx={{ position: 'absolute', inset: '10px 8px 18px 8px', bgcolor: '#6d4a2c', border: '4px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 20, top: 18, width: 30, height: 18, bgcolor: lit ? accent : '#92a0a8', border: '3px solid #151a13', boxShadow: lit ? `0 0 0 2px ${accent}55` : 'none' }} />
    <Box sx={{ position: 'absolute', left: 30, top: 38, width: 10, height: 6, bgcolor: '#151a13' }} />
    <Box sx={{ position: 'absolute', right: 18, top: 20, width: 16, height: 16, bgcolor: '#bc9668', border: '3px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 16, bottom: 0, width: 10, height: 18, bgcolor: '#151a13' }} />
    <Box sx={{ position: 'absolute', right: 16, bottom: 0, width: 10, height: 18, bgcolor: '#151a13' }} />
  </Box>
);

const PixelSofa = ({ x, y, width = 150 }: { x: number; y: number; width?: number }) => (
  <Box sx={{ position: 'absolute', left: `${x}%`, top: `${y}%`, width, height: 72, transform: 'translate(-50%, -50%)' }}>
    <Box sx={{ position: 'absolute', inset: '18px 0 0 0', bgcolor: '#7c5c42', border: '4px solid #151a13' }} />
    <Box sx={{ position: 'absolute', inset: '0 14px auto 14px', height: 20, bgcolor: '#926b4d', border: '4px solid #151a13' }} />
    <Box sx={{ position: 'absolute', left: 14, top: 22, width: 18, height: 26, bgcolor: '#aa845f', border: '3px solid #151a13' }} />
    <Box sx={{ position: 'absolute', right: 14, top: 22, width: 18, height: 26, bgcolor: '#aa845f', border: '3px solid #151a13' }} />
  </Box>
);

const SceneFrame = ({
  title,
  subtitle,
  children
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) => (
  <Box sx={{ ...pixelPanelSx, position: 'relative', flex: 1, overflow: 'hidden', m: 1.5, mb: 0.8 }}>
    <Box sx={{ position: 'absolute', inset: 0, pointerEvents: 'none', backgroundImage: 'repeating-linear-gradient(180deg, rgba(255,255,255,0.02) 0 5px, rgba(0,0,0,0.08) 5px 7px)', zIndex: 20 }} />
    <Box sx={{ position: 'absolute', left: 16, top: 14, zIndex: 21 }}>
      <Typography variant="body2" sx={{ color: '#f5e6a6', fontWeight: 700, fontFamily: 'var(--font-code)', letterSpacing: 1 }}>
        {title}
      </Typography>
      <Typography variant="caption" sx={{ color: '#d6dfc2', fontFamily: 'var(--font-code)' }}>
        {subtitle}
      </Typography>
    </Box>
    {children}
  </Box>
);

const MiniatureOfficeGame: React.FC = () => {
  const [workspaceName, setWorkspaceName] = useState('Sovereign-Governance-Substrate');
  const [scene, setScene] = useState<GameScene>('arrival');
  const [arrivalPhase, setArrivalPhase] = useState<ArrivalPhase>('idle');
  const [exploreMode, setExploreMode] = useState<ExploreMode>('floor');
  const [conferencePhase, setConferencePhase] = useState<ConferencePhase>('briefing');
  const [floorIndex, setFloorIndex] = useState(0);
  const [playerPosition, setPlayerPosition] = useState<PlayerPosition>(getSpawnPoint('arrival', 'floor'));
  const [playerFacing, setPlayerFacing] = useState<Facing>('down');
  const [playerBubble, setPlayerBubble] = useState('');
  const [npcSpeaker, setNpcSpeaker] = useState('');
  const [npcBubble, setNpcBubble] = useState('');
  const [ambientTicker, setAmbientTicker] = useState('Drive up to the building and enter the tower.');
  const [loungeExchange, setLoungeExchange] = useState<string[]>(buildLoungeExchange());
  const [meetingPrompt, setMeetingPrompt] = useState('');
  const [meetingDecision, setMeetingDecision] = useState<MeetingRoutingResult | null>(null);
  const [assignmentLedger, setAssignmentLedger] = useState<AssignmentLedger[]>([]);

  const activeFloor = OFFICE_FLOORS[floorIndex] || OFFICE_FLOORS[0];
  const missionBoard = assignmentLedger.slice(0, 4);
  const activeFloorAssignments = assignmentLedger.filter(
    (assignment) =>
      assignment.status !== 'completed' &&
      [assignment.leadFloor, ...assignment.supportFloors].includes(activeFloor.name)
  );

  const floorWorkers = useMemo(
    () =>
      activeFloor.agents.map((agent, index) => {
        const slot = deskSlots[index % deskSlots.length];
        return { agent, slot };
      }),
    [activeFloor]
  );

  const nearestWorker = useMemo(() => {
    return floorWorkers.reduce(
      (closest, worker) => {
        const distance = Math.hypot(playerPosition.x - worker.slot.actorX, playerPosition.y - worker.slot.actorY);
        if (distance < closest.distance) {
          return { worker, distance };
        }
        return closest;
      },
      { worker: floorWorkers[0], distance: Number.POSITIVE_INFINITY }
    ).worker;
  }, [floorWorkers, playerPosition]);

  useEffect(() => {
    const bootstrap = async () => {
      const nextWorkspaceRoot = await window.electron?.workspace?.getRoot?.();
      const storedScene = await window.electron?.store?.get<GameScene>(GAME_SCENE_STORE_KEY);
      const storedFloorIndex = await window.electron?.store?.get<number>(GAME_FLOOR_INDEX_STORE_KEY);
      const storedLedger = await window.electron?.store?.get<AssignmentLedger[]>(GAME_LEDGER_STORE_KEY);

      if (typeof nextWorkspaceRoot === 'string' && nextWorkspaceRoot.trim()) {
        const segments = nextWorkspaceRoot.split(/[\\/]+/).filter(Boolean);
        setWorkspaceName(segments[segments.length - 1] || nextWorkspaceRoot);
      }
      if (storedScene) setScene(storedScene);
      if (typeof storedFloorIndex === 'number' && storedFloorIndex >= 0 && storedFloorIndex < OFFICE_FLOORS.length) {
        setFloorIndex(storedFloorIndex);
      }
      if (Array.isArray(storedLedger)) setAssignmentLedger(storedLedger);
    };

    void bootstrap();
  }, []);

  useEffect(() => {
    if (!window.electron?.store) return;
    void window.electron.store.set(GAME_SCENE_STORE_KEY, scene);
    void window.electron.store.set(GAME_FLOOR_INDEX_STORE_KEY, floorIndex);
    void window.electron.store.set(GAME_LEDGER_STORE_KEY, assignmentLedger);
  }, [scene, floorIndex, assignmentLedger]);

  useEffect(() => {
    setPlayerPosition(getSpawnPoint(scene, exploreMode));
    setPlayerFacing(scene === 'conference' ? 'left' : 'down');
  }, [scene, exploreMode]);

  useEffect(() => {
    if (scene !== 'explore' || exploreMode !== 'lounge') return;
    const interval = window.setInterval(() => setLoungeExchange(buildLoungeExchange()), 5000);
    return () => window.clearInterval(interval);
  }, [scene, exploreMode]);

  const updateAssignment = (assignmentId: string, update: (assignment: AssignmentLedger) => AssignmentLedger) => {
    setAssignmentLedger((current) =>
      current.map((assignment) => (assignment.id === assignmentId ? update(assignment) : assignment))
    );
  };

  const clearDialogue = () => {
    setNpcSpeaker('');
    setNpcBubble('');
  };

  const movePlayer = (deltaX: number, deltaY: number, facing: Facing) => {
    if (scene === 'arrival' && arrivalPhase === 'idle') return;
    const bounds = getMovementBounds(scene, exploreMode);
    setPlayerFacing(facing);
    setPlayerPosition((current) => ({
      x: clamp(current.x + deltaX, bounds.minX, bounds.maxX),
      y: clamp(current.y + deltaY, bounds.minY, bounds.maxY)
    }));
  };

  const goToLobby = () => {
    setScene('lobby');
    clearDialogue();
    setPlayerBubble('');
    setAmbientTicker('Lobby reached. Reception is open and the elevator is waiting.');
  };

  const goToElevator = () => {
    setScene('elevator');
    clearDialogue();
    setPlayerBubble('');
    setAmbientTicker('Elevator doors close. CEO floor selected.');
  };

  const goToCEO = () => {
    setScene('ceo');
    clearDialogue();
    setPlayerBubble(pickOne(ceoDeskLines));
    setAmbientTicker('CEO office reached. Choose to call a meeting or explore the tower.');
  };

  const goToExplore = () => {
    setExploreMode('floor');
    setScene('explore');
    clearDialogue();
    setPlayerBubble('');
    setAmbientTicker(`Exploring ${activeFloor.name}. Every employee desk is active on this floor.`);
  };

  const goToLounge = () => {
    setExploreMode('lounge');
    clearDialogue();
    setAmbientTicker('Observation mode engaged. Off-duty chatter is live.');
  };

  const startArrivalSequence = () => {
    setArrivalPhase('driving');
    clearDialogue();
    setPlayerBubble('');
    setAmbientTicker('The car rolls through the grass and lines up on the approach road.');
    window.setTimeout(() => {
      setArrivalPhase('parking');
      setAmbientTicker('Brake lights flare. The car parks at the curb.');
      setPlayerPosition({ x: 31, y: 74 });
    }, 850);
    window.setTimeout(() => {
      setArrivalPhase('walking');
      setPlayerBubble(pickOne(arrivalLines));
      setPlayerPosition({ x: 46, y: 68 });
      setAmbientTicker('The player gets out and walks toward the entrance.');
    }, 1650);
    window.setTimeout(() => {
      setArrivalPhase('ready');
      setAmbientTicker('Arrival complete. Move to the door or enter the lobby.');
    }, 2850);
  };

  const talkToWorker = () => {
    const addressed = nearestWorker?.agent || activeFloor.head;
    const lines =
      activeFloorAssignments.length > 0
        ? [
            `${addressed}: Conference room sent the order down. We are on active build.`,
            `${activeFloor.head}: Keep the aisle clear. This floor is in motion.`,
            `${addressed}: Desk lights are live because the assignment board lit up.`
          ]
        : getFloorDialogue(activeFloor.name).map((line) => line.replace(/^[^:]+:/, `${addressed}:`));

    setNpcSpeaker(addressed);
    setNpcBubble(pickOne(lines));
    setAmbientTicker(`${activeFloor.name} responded from the nearest desk.`);
  };

  const inspectEasterEgg = () => {
    const eggLines =
      easterEggsByFloor[activeFloor.name] || [
        'A tiny brass plate is bolted beneath a desk and no one will admit who put it there.'
      ];
    setNpcSpeaker('Easter Egg');
    setNpcBubble(pickOne(eggLines));
    setAmbientTicker(`You found something hidden on ${activeFloor.name}.`);
  };

  const runAssignmentCrew = async (assignment: AssignmentLedger) => {
    window.setTimeout(() => {
      updateAssignment(assignment.id, (current) => ({
        ...current,
        status: 'building',
        updatedAt: createTimestamp(),
        report: [...current.report, 'Department heads left the table and the floors are now in motion.']
      }));
    }, 1200);

    const token = extractSearchToken(assignment.request);
    const [repoStatus, searchResults] = await Promise.all([
      window.electron?.workspace?.getRepoStatus?.(),
      token ? window.electron?.workspace?.searchFiles?.(token) : Promise.resolve([])
    ]);

    window.setTimeout(() => {
      updateAssignment(assignment.id, (current) => ({
        ...current,
        status: 'validating',
        updatedAt: createTimestamp(),
        report: [
          ...current.report,
          `City Archivists logged ${repoStatus?.modifiedCount || 0} modified, ${repoStatus?.untrackedCount || 0} untracked, and ${repoStatus?.conflictedCount || 0} conflicted files.`,
          token
            ? `Scouts on ${assignment.leadFloor} flagged ${
                (searchResults as unknown[] | undefined)?.length || 0
              } likely touchpoints around "${token}".`
            : `${assignment.leadFloor} proceeded without a keyword-specific scout sweep.`
        ]
      }));
    }, 2600);

    window.setTimeout(() => {
      updateAssignment(assignment.id, (current) => ({
        ...current,
        status: 'completed',
        updatedAt: createTimestamp(),
        report: [
          ...current.report,
          `${assignment.leadFloor} filed an initial build pass and returned the summary to the CEO floor.`
        ]
      }));
      setAmbientTicker(`${assignment.leadFloor} reports: first pass complete.`);
    }, 4300);
  };

  const deliberateMeeting = () => {
    if (!meetingPrompt.trim()) return;
    clearDialogue();
    setConferencePhase('gathering');
    setMeetingDecision(null);
    setAmbientTicker('Department heads gather around the table and decide floor ownership.');
    window.setTimeout(() => {
      const decision = routeMeetingRequest(meetingPrompt);
      setMeetingDecision(decision);
      setConferencePhase('deliberating');
      setAmbientTicker(`${decision.leadFloor} takes point. Support floors align behind the plan.`);
    }, 900);
  };

  const dispatchMeeting = () => {
    if (!meetingDecision || !meetingPrompt.trim()) return;
    setConferencePhase('dispatching');
    const nextAssignment: AssignmentLedger = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      request: meetingPrompt.trim(),
      leadFloor: meetingDecision.leadFloor,
      supportFloors: meetingDecision.supportFloors,
      summary: meetingDecision.summary,
      createdAt: createTimestamp(),
      updatedAt: createTimestamp(),
      status: 'assembling',
      report: ['Conference adjourned. Elevators and hallways are now full of moving department heads.']
    };

    setAssignmentLedger((current) => [nextAssignment, ...current]);
    setAmbientTicker(`${meetingDecision.leadFloor} and support floors are leaving the conference room.`);
    window.setTimeout(() => {
      setScene('ceo');
      setConferencePhase('briefing');
      setMeetingPrompt('');
      setMeetingDecision(null);
      setPlayerBubble('Good. Go build it.');
      void runAssignmentCrew(nextAssignment);
    }, 950);
  };

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing =
        !!target &&
        (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable);

      if (!typing) {
        if (event.key === 'ArrowUp' || event.key.toLowerCase() === 'w') {
          event.preventDefault();
          movePlayer(0, -2.8, 'up');
          return;
        }
        if (event.key === 'ArrowDown' || event.key.toLowerCase() === 's') {
          event.preventDefault();
          movePlayer(0, 2.8, 'down');
          return;
        }
        if (event.key === 'ArrowLeft' || event.key.toLowerCase() === 'a') {
          event.preventDefault();
          movePlayer(-2.8, 0, 'left');
          return;
        }
        if (event.key === 'ArrowRight' || event.key.toLowerCase() === 'd') {
          event.preventDefault();
          movePlayer(2.8, 0, 'right');
          return;
        }
      }

      if (event.key === 'Enter' && !typing) {
        if (scene === 'arrival' && arrivalPhase === 'idle') {
          event.preventDefault();
          startArrivalSequence();
          return;
        }
        if (scene === 'arrival' && arrivalPhase === 'ready') {
          event.preventDefault();
          goToLobby();
          return;
        }
        if (scene === 'lobby') {
          event.preventDefault();
          goToElevator();
          return;
        }
        if (scene === 'elevator') {
          event.preventDefault();
          goToCEO();
        }
      }

      if (!typing && scene === 'explore' && exploreMode === 'floor' && event.key.toLowerCase() === 't') {
        event.preventDefault();
        talkToWorker();
      } else if (!typing && scene === 'explore' && exploreMode === 'floor' && event.key.toLowerCase() === 'e') {
        event.preventDefault();
        inspectEasterEgg();
      } else if (!typing && event.key === 'Escape' && scene !== 'arrival') {
        event.preventDefault();
        goToCEO();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [arrivalPhase, exploreMode, nearestWorker, scene, activeFloorAssignments, activeFloor.name, meetingPrompt, meetingDecision]);

  const sceneMeta = useMemo(() => {
    if (scene === 'arrival') {
      return {
        title: 'FIELD APPROACH',
        subtitle:
          arrivalPhase === 'idle'
            ? 'Birds-eye exterior approach'
            : arrivalPhase === 'ready'
              ? 'Move to the entrance and enter'
              : 'Arrival sequence in progress'
      };
    }
    if (scene === 'lobby') return { title: 'LOBBY', subtitle: 'Top-down reception and elevator hall' };
    if (scene === 'elevator') return { title: 'ELEVATOR', subtitle: 'Vertical movement between floors' };
    if (scene === 'ceo') return { title: 'CEO FLOOR', subtitle: workspaceName };
    if (scene === 'conference') return { title: 'CONFERENCE ROOM', subtitle: 'Department heads deliberate at one table' };
    return {
      title: exploreMode === 'lounge' ? 'OFF-DUTY LOUNGE' : activeFloor.name.toUpperCase(),
      subtitle:
        exploreMode === 'lounge'
          ? 'Observation mode'
          : `${activeFloor.specialty} // ${activeFloor.agents.length} desks online`
    };
  }, [activeFloor, arrivalPhase, exploreMode, scene, workspaceName]);

  const primarySpeaker = npcSpeaker || 'Tower Feed';
  const primaryDialogue = npcBubble || playerBubble || ambientTicker;

  const worldView = useMemo(() => {
    if (scene === 'arrival') {
      const carLeft = arrivalPhase === 'idle' ? 10 : arrivalPhase === 'driving' ? 25 : 34;
      return (
        <SceneFrame title={sceneMeta.title} subtitle={sceneMeta.subtitle}>
          <Box sx={{ position: 'absolute', inset: 0, ...dottedPattern('#7ec55f', 'rgba(105,170,74,0.56)', 24) }} />
          <Box sx={{ position: 'absolute', left: '-10%', top: '44%', width: '135%', height: 120, bgcolor: '#d2ceb1', borderTop: '4px solid #151a13', borderBottom: '4px solid #151a13', transform: 'rotate(-18deg)', transformOrigin: 'left center' }} />
          <Box sx={{ position: 'absolute', left: '-6%', top: '50%', width: '132%', height: 72, bgcolor: '#798088', borderTop: '4px solid #151a13', borderBottom: '4px solid #151a13', transform: 'rotate(-18deg)', transformOrigin: 'left center' }} />
          {Array.from({ length: 6 }).map((_, index) => (
            <Box
              key={index}
              sx={{
                position: 'absolute',
                left: `${18 + index * 10}%`,
                top: `${56 - index * 3.4}%`,
                width: 42,
                height: 4,
                bgcolor: '#eef5e6',
                transform: 'rotate(-18deg)'
              }}
            />
          ))}
          <PixelFlowerPatch x={6} y={72} colors={['#f6d989', '#f49090', '#eef1d3']} />
          <PixelFlowerPatch x={18} y={84} colors={['#eef1d3', '#f49090', '#b8dff5']} />
          <PixelFlowerPatch x={70} y={84} colors={['#f49090', '#b8dff5', '#f6d989']} />
          <PixelPlanter x={88} y={70} />
          <PixelTowerExterior />
          <PixelCar left={carLeft} top={64} />
          <PixelActor label="Guard" accent="#c98068" x={64} y={58} facing="left" scale={0.9} />
          <PixelActor label="Courier" accent="#b16de3" x={72} y={61} facing="down" scale={0.9} />
          <Box sx={{ position: 'absolute', left: '52%', top: '36%', width: 52, height: 4, bgcolor: '#dcf7ff', opacity: 0.7, animation: '1.1s steps(5) infinite pixel-whoosh' }} />
          <Box sx={{ position: 'absolute', left: '58%', top: '42%', width: 36, height: 4, bgcolor: '#dcf7ff', opacity: 0.55, animation: '1.2s steps(5) infinite 0.2s pixel-whoosh' }} />
          <PixelActor label="You" accent="#59b1a6" x={playerPosition.x} y={playerPosition.y} bubble={arrivalPhase === 'walking' || arrivalPhase === 'ready' ? playerBubble : undefined} facing={playerFacing} active={arrivalPhase === 'ready'} />
        </SceneFrame>
      );
    }

    if (scene === 'lobby') {
      return (
        <SceneFrame title={sceneMeta.title} subtitle={sceneMeta.subtitle}>
          <Box sx={{ position: 'absolute', inset: 0, ...tilePattern('#d8cc9b', 'rgba(74, 58, 35, 0.1)', 24) }} />
          <Box sx={{ position: 'absolute', left: '8%', top: '10%', width: 190, height: 96, bgcolor: '#55664c', border: '6px solid #151a13' }} />
          <Box sx={{ position: 'absolute', left: '12%', top: '16%', width: 120, height: 20, bgcolor: '#f4ba3f', border: '3px solid #151a13', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="caption" sx={{ color: '#11150f', fontFamily: 'var(--font-code)' }}>
              RECEPTION
            </Typography>
          </Box>
          <Box sx={{ position: 'absolute', right: '10%', top: '8%', width: 218, height: 188, bgcolor: '#2b3136', border: '8px solid #151a13' }} />
          <Box sx={{ position: 'absolute', right: '14%', top: '16%', width: 70, height: 132, bgcolor: '#9aa2ab', border: '5px solid #151a13' }} />
          <Box sx={{ position: 'absolute', right: '31%', top: '16%', width: 70, height: 132, bgcolor: '#9aa2ab', border: '5px solid #151a13' }} />
          <Box sx={{ position: 'absolute', right: '25%', top: '12%', width: 32, height: 18, bgcolor: '#f4ba3f', border: '4px solid #151a13' }} />
          <PixelPlanter x={20} y={74} />
          <PixelPlanter x={80} y={74} />
          <Box sx={{ position: 'absolute', left: '34%', top: '60%', width: 170, height: 50, bgcolor: '#8c6a42', border: '6px solid #151a13' }} />
          <PixelActor label="Reception" accent="#c98068" x={18} y={34} bubble={lobbyLines[0]} facing="down" />
          <PixelActor label="You" accent="#59b1a6" x={playerPosition.x} y={playerPosition.y} facing={playerFacing} active />
        </SceneFrame>
      );
    }

    if (scene === 'elevator') {
      return (
        <SceneFrame title={sceneMeta.title} subtitle={sceneMeta.subtitle}>
          <Box sx={{ position: 'absolute', inset: 0, ...tilePattern('#655943', 'rgba(0,0,0,0.13)', 18) }} />
          <Box sx={{ position: 'absolute', left: '28%', top: '10%', width: '44%', height: '76%', bgcolor: '#2a3035', border: '8px solid #151a13' }} />
          <Box sx={{ position: 'absolute', left: '37%', top: '18%', width: '11%', height: '46%', bgcolor: '#9aa2ab', border: '6px solid #151a13' }} />
          <Box sx={{ position: 'absolute', left: '52%', top: '18%', width: '11%', height: '46%', bgcolor: '#9aa2ab', border: '6px solid #151a13' }} />
          <Box sx={{ position: 'absolute', right: '14%', top: '18%', width: 120, height: 208, bgcolor: '#171b15', border: '4px solid #151a13', p: 1 }}>
            {[30, 28, 24, 17, 9, 1].map((floor, index) => (
              <Box
                key={floor}
                sx={{
                  mb: 1,
                  height: 24,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: index === 0 ? '#f4ba3f' : '#8a9675',
                  border: '3px solid #151a13',
                  fontFamily: 'var(--font-code)',
                  color: index === 0 ? '#11150f' : '#151a13'
                }}
              >
                {floor}
              </Box>
            ))}
          </Box>
          <PixelActor label="You" accent="#59b1a6" x={playerPosition.x} y={playerPosition.y} facing={playerFacing} active />
        </SceneFrame>
      );
    }

    if (scene === 'ceo') {
      return (
        <SceneFrame title={sceneMeta.title} subtitle={sceneMeta.subtitle}>
          <Box sx={{ position: 'absolute', inset: 0, ...tilePattern('#3b4934', 'rgba(20,24,18,0.1)', 24) }} />
          <Box sx={{ position: 'absolute', left: '6%', top: '8%', width: 244, height: 126, bgcolor: '#cfdfec', border: '7px solid #151a13' }} />
          <Box sx={{ position: 'absolute', left: '8%', top: '12%', width: 204, height: 86, bgcolor: '#9cc9ec', border: '4px solid #151a13' }} />
          {Array.from({ length: 6 }).map((_, index) => (
            <Box key={index} sx={{ position: 'absolute', left: `${12 + (index % 3) * 8}%`, top: `${20 + Math.floor(index / 3) * 10}%`, width: 22, height: 16, bgcolor: '#53606a' }} />
          ))}
          <Box sx={{ position: 'absolute', left: '34%', top: '48%', width: 220, height: 90, bgcolor: '#8c6a42', border: '8px solid #151a13', boxShadow: '10px 10px 0 rgba(10, 13, 9, 0.88)' }} />
          <Box sx={{ position: 'absolute', left: '38%', top: '52%', width: 120, height: 18, bgcolor: '#11150f', border: '3px solid #151a13' }} />
          <Box sx={{ position: 'absolute', right: '10%', top: '18%', width: 282, minHeight: 186, bgcolor: '#1f261c', border: '5px solid #5c6d4f', p: 1.2 }}>
            <Typography variant="caption" sx={{ color: '#f4ba3f', fontFamily: 'var(--font-code)' }}>
              MISSION BOARD
            </Typography>
            {missionBoard.length === 0 && <Typography variant="body2" sx={{ mt: 1, color: '#d6dfc2' }}>No dispatched builds yet.</Typography>}
            {missionBoard.map((mission) => (
              <Box key={mission.id} sx={{ mt: 1, p: 0.8, bgcolor: missionStatusTone[mission.status].background, border: '2px solid #5c6d4f' }}>
                <Stack direction="row" justifyContent="space-between" spacing={1}>
                  <Typography variant="body2" sx={{ color: '#f5e6a6', fontWeight: 700 }}>{mission.leadFloor}</Typography>
                  <Typography variant="caption" sx={{ color: missionStatusTone[mission.status].color, fontFamily: 'var(--font-code)' }}>{missionStatusTone[mission.status].label}</Typography>
                </Stack>
                <Typography variant="caption" sx={{ color: '#d6dfc2', display: 'block', mt: 0.4 }}>
                  {mission.report[mission.report.length - 1] || mission.summary}
                </Typography>
              </Box>
            ))}
          </Box>
          <PixelPlanter x={16} y={72} />
          <PixelActor label="You" accent="#59b1a6" x={playerPosition.x} y={playerPosition.y} bubble={playerBubble || ceoDeskLines[0]} facing={playerFacing} active />
        </SceneFrame>
      );
    }

    if (scene === 'conference') {
      return (
        <SceneFrame title={sceneMeta.title} subtitle={sceneMeta.subtitle}>
          <Box sx={{ position: 'absolute', inset: 0, ...tilePattern('#4a382b', 'rgba(0,0,0,0.12)', 26) }} />
          <Box sx={{ position: 'absolute', left: '24%', top: '24%', width: '44%', height: 140, bgcolor: '#6d4a2c', border: '8px solid #151a13', boxShadow: '10px 10px 0 rgba(10, 13, 9, 0.88)' }} />
          <Box sx={{ position: 'absolute', left: '34%', top: '18%', width: '24%', height: 26, bgcolor: '#181c16', border: '5px solid #151a13', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="caption" sx={{ color: '#f4ba3f', fontFamily: 'var(--font-code)' }}>
              FLOOR HEADS
            </Typography>
          </Box>
          {OFFICE_FLOORS.slice(0, 8).map((floor, index) => {
            const seat = conferenceSeats[index];
            const bubble = meetingDecision?.leadFloor === floor.name && conferencePhase === 'deliberating' ? 'We take point.' : undefined;
            const x = conferencePhase === 'briefing' || conferencePhase === 'dispatching' ? (index % 2 === 0 ? 4 : 96) : seat.x;
            const y = conferencePhase === 'briefing' || conferencePhase === 'dispatching' ? (index % 2 === 0 ? 26 + index * 5 : 18 + index * 5) : seat.y;
            return <PixelActor key={floor.name} label={floor.head} accent={floor.accent} x={x} y={y} bubble={bubble} facing={seat.facing} active={meetingDecision?.leadFloor === floor.name} scale={0.92} />;
          })}
          <PixelActor label="You" accent="#59b1a6" x={playerPosition.x} y={playerPosition.y} facing={playerFacing} active />
        </SceneFrame>
      );
    }

    return null;
  }, [
    arrivalPhase,
    conferencePhase,
    exploreMode,
    meetingDecision,
    missionBoard,
    playerBubble,
    playerFacing,
    playerPosition,
    scene,
    sceneMeta.subtitle,
    sceneMeta.title
  ]);
