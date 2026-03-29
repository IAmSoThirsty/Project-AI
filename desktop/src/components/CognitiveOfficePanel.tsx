import React from 'react';
import { Box, Chip, Divider, Stack, Typography } from '@mui/material';
import {
  Apartment,
  AutoAwesome,
  GroupWork,
  HistoryEdu,
  MeetingRoom,
  TravelExplore
} from '@mui/icons-material';
import { OfficeFloor, RepoStatus, WorkOrder, WorkOrderPlan } from '../types/sovereign';
import MiniatureOfficeTower from './MiniatureOfficeTower';

interface CognitiveOfficePanelProps {
  workspaceName: string;
  workspaceRoot: string;
  plan: WorkOrderPlan;
  repoStatus: RepoStatus | null;
  floors: OfficeFloor[];
  activeFloorName: string;
  workOrders: WorkOrder[];
  onSelectFloor: (floorName: string) => void;
}

const panelSx = {
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  gap: 1.5,
  p: 2,
  border: '2px solid rgba(80, 101, 71, 0.95)',
  background: 'linear-gradient(180deg, #1a2018 0%, #11150f 100%)',
  boxShadow: '5px 5px 0 rgba(10, 13, 9, 0.92)',
  overflow: 'auto'
} as const;

const itemCardSx = {
  p: 1.3,
  border: '2px solid rgba(96, 117, 87, 0.9)',
  background: 'rgba(29, 36, 27, 0.94)',
  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
} as const;

const sectionTitleSx = {
  display: 'flex',
  alignItems: 'center',
  gap: 0.75,
  color: '#f3f7df'
} as const;

const CognitiveOfficePanel: React.FC<CognitiveOfficePanelProps> = ({
  workspaceName,
  workspaceRoot,
  plan,
  repoStatus,
  floors,
  activeFloorName,
  workOrders,
  onSelectFloor
}) => {
  const activeFloor = floors.find((floor) => floor.name === activeFloorName) ?? floors[0];
  const loungeFloors = floors
    .filter(
      (floor) =>
        floor.name !== activeFloor.name &&
        floor.name !== plan.primaryFloor &&
        !plan.supportFloors.includes(floor.name)
    )
    .slice(0, 4);
  const latestWorkOrder = workOrders[0] || null;
  const moraleState = repoStatus
    ? repoStatus.conflictedCount > 0
      ? 'Alert posture active. Lounge Stewards are pacing the crews through a high-pressure shift.'
      : repoStatus.modifiedCount + repoStatus.untrackedCount > 20
        ? 'Attention burn rate elevated. Sync-break rotations are recommended before the next wave.'
        : 'Morale nominal. Crews are focused, rested, and moving with steady rhythm.'
    : 'Morale telemetry will appear once the local repository status is sampled.';

  return (
    <Box sx={panelSx}>
      <Box>
        <Typography
          variant="overline"
          sx={{ color: '#f4ba3f', letterSpacing: 2.4, fontWeight: 700 }}
        >
          Miniature Office
        </Typography>
        <Typography
          variant="h5"
          sx={{
            mt: 0.5,
            fontWeight: 800,
            fontFamily: 'var(--font-code)',
            color: '#f5e6a6',
            textTransform: 'uppercase'
          }}
        >
          Interactive Cognitive IDE
        </Typography>
        <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
          Pixel-built command tower with a civil-defense control-room mood, custom crews, and
          offline work-order routing for the sovereign repair teams.
        </Typography>
      </Box>

      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
        <Chip
          label="Offline First"
          size="small"
          sx={{ color: '#f5e6a6', border: '1px solid #7d6b2d', bgcolor: '#353015' }}
        />
        <Chip
          label="Pixel Tower"
          size="small"
          sx={{ color: '#d4f3e5', border: '1px solid #35624f', bgcolor: '#18261f' }}
        />
        <Chip
          label="VR City Dormant"
          size="small"
          sx={{ color: '#bee3f8', border: '1px solid #2c5872', bgcolor: '#14202a' }}
        />
      </Stack>

      <MiniatureOfficeTower
        floors={floors}
        activeFloorName={activeFloor.name}
        leadFloorName={plan.primaryFloor}
        supportFloorNames={plan.supportFloors}
        workOrders={workOrders}
        onSelectFloor={onSelectFloor}
      />

      <Box sx={itemCardSx}>
        <Box sx={sectionTitleSx}>
          <Apartment fontSize="small" />
          <Typography variant="subtitle2">Active Floor Detail</Typography>
        </Box>
        <Typography
          variant="body2"
          sx={{ mt: 1, color: '#f5e6a6', fontWeight: 700, fontFamily: 'var(--font-code)' }}
        >
          {activeFloor.name}
        </Typography>
        <Typography variant="caption" sx={{ mt: 0.5, display: 'block', color: '#a5b39a' }}>
          Head: {activeFloor.head} | Specialty: {activeFloor.specialty}
        </Typography>
        <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
          {activeFloor.overview}
        </Typography>
        <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 1.2 }}>
          {activeFloor.agents.map((agent) => (
            <Chip
              key={agent}
              label={agent}
              size="small"
              sx={{
                color: '#eef2d1',
                border: `1px solid ${activeFloor.accent}`,
                bgcolor: 'rgba(255,255,255,0.03)'
              }}
            />
          ))}
        </Stack>
      </Box>

      <Box sx={itemCardSx}>
        <Box sx={sectionTitleSx}>
          <MeetingRoom fontSize="small" />
          <Typography variant="subtitle2">CEO Conference Room</Typography>
        </Box>
        <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
          {plan.summary}
        </Typography>
        <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 1.2 }}>
          <Chip label={`Lead: ${plan.primaryFloor}`} size="small" sx={{ color: '#7dd3fc' }} />
          {plan.supportFloors.map((floor) => (
            <Chip
              key={floor}
              label={floor}
              size="small"
              variant="outlined"
              sx={{ color: '#f0abfc', borderColor: 'rgba(240, 171, 252, 0.45)' }}
            />
          ))}
        </Stack>
        {latestWorkOrder && (
          <Typography variant="caption" sx={{ mt: 1, display: 'block', color: '#a5b39a' }}>
            Latest order: {latestWorkOrder.title} routed to {latestWorkOrder.assignedFloor} with{' '}
            {latestWorkOrder.status} status.
          </Typography>
        )}
      </Box>

      <Box sx={{ display: 'grid', gap: 1.2, gridTemplateColumns: '1fr 1fr' }}>
        <Box sx={itemCardSx}>
          <Box sx={sectionTitleSx}>
            <HistoryEdu fontSize="small" />
            <Typography variant="subtitle2">City Archivists</Typography>
          </Box>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            Branch {repoStatus?.branch || 'workspace'} tracking {repoStatus?.modifiedCount || 0}{' '}
            modified, {repoStatus?.untrackedCount || 0} untracked, and{' '}
            {repoStatus?.conflictedCount || 0} conflicted files.
          </Typography>
        </Box>

        <Box sx={itemCardSx}>
          <Box sx={sectionTitleSx}>
            <GroupWork fontSize="small" />
            <Typography variant="subtitle2">Off-Duty Lounge</Typography>
          </Box>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            {moraleState}
          </Typography>
          <Typography variant="caption" sx={{ mt: 0.8, display: 'block', color: '#a5b39a' }}>
            Resting floors: {loungeFloors.map((floor) => floor.name).join(', ') || 'All hands up'}
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: 'rgba(96, 117, 87, 0.75)' }} />

      <Box sx={itemCardSx}>
        <Box sx={sectionTitleSx}>
          <AutoAwesome fontSize="small" />
          <Typography variant="subtitle2">Plaza Decorators</Typography>
        </Box>
        <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
          Recognition protocol stands by for zero-drift merges and full-shift recovery wins across{' '}
          {workspaceName}.
        </Typography>
        <Typography variant="caption" sx={{ mt: 0.8, display: 'block', color: '#a5b39a' }}>
          Rooted at {workspaceRoot}
        </Typography>
      </Box>

      <Box sx={itemCardSx}>
        <Box sx={sectionTitleSx}>
          <TravelExplore fontSize="small" />
          <Typography variant="subtitle2">VR City Link</Typography>
        </Box>
        <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
          The city twin remains staged for later drift, intrusion, honeypot, and repair-crew
          visualization. This local workstation now provides the command backbone for it.
        </Typography>
      </Box>
    </Box>
  );
};

export default CognitiveOfficePanel;
