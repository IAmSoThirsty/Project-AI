import React from 'react';
import { Box, Typography } from '@mui/material';
import { OfficeFloor, WorkOrder } from '../types/sovereign';

interface MiniatureOfficeTowerProps {
  floors: OfficeFloor[];
  activeFloorName: string;
  leadFloorName: string;
  supportFloorNames: string[];
  workOrders: WorkOrder[];
  onSelectFloor: (floorName: string) => void;
}

const MiniatureOfficeTower: React.FC<MiniatureOfficeTowerProps> = ({
  floors,
  activeFloorName,
  leadFloorName,
  supportFloorNames,
  workOrders,
  onSelectFloor
}) => {
  const supportSet = new Set(supportFloorNames);
  const workOrderCountByFloor = workOrders.reduce<Record<string, number>>((current, order) => {
    current[order.assignedFloor] = (current[order.assignedFloor] || 0) + 1;
    return current;
  }, {});

  return (
    <Box
      sx={{
        p: 1.25,
        border: '2px solid rgba(56, 76, 58, 0.95)',
        bgcolor: '#141812',
        boxShadow: '4px 4px 0 rgba(11, 14, 10, 0.9)'
      }}
    >
      <Typography
        variant="caption"
        sx={{ color: '#f4ba3f', display: 'block', mb: 1, letterSpacing: 1.4, fontWeight: 700 }}
      >
        MINIATURE OFFICE TOWER
      </Typography>

      <Box
        sx={{
          mb: 0.9,
          px: 1,
          py: 0.7,
          border: '2px solid rgba(96, 117, 87, 0.9)',
          bgcolor: '#233021',
          boxShadow: '3px 3px 0 rgba(11, 14, 10, 0.85)'
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 700, color: '#f5e6a6' }}>
          CEO FLOOR
        </Typography>
        <Typography variant="caption" sx={{ color: '#d1d8b7' }}>
          Conference room ready for mash-up project routing
        </Typography>
      </Box>

      <Box
        sx={{
          maxHeight: 286,
          overflow: 'auto',
          pr: 0.5
        }}
      >
        {floors
          .slice()
          .sort((left, right) => right.id - left.id)
          .map((floor) => {
            const isActive = floor.name === activeFloorName;
            const isLead = floor.name === leadFloorName;
            const isSupport = supportSet.has(floor.name);
            const queueCount = workOrderCountByFloor[floor.name] || 0;

            return (
              <Box
                key={floor.name}
                onClick={() => onSelectFloor(floor.name)}
                sx={{
                  mb: 0.7,
                  p: 0.75,
                  display: 'grid',
                  gridTemplateColumns: '34px minmax(0, 1fr) auto',
                  gap: 0.9,
                  alignItems: 'center',
                  cursor: 'pointer',
                  border: '2px solid',
                  borderColor: isActive
                    ? '#f4ba3f'
                    : isLead
                      ? '#6ee7b7'
                      : isSupport
                        ? '#7dd3fc'
                        : 'rgba(92, 109, 79, 0.95)',
                  bgcolor: isActive
                    ? 'rgba(244, 186, 63, 0.12)'
                    : isLead
                      ? 'rgba(110, 231, 183, 0.08)'
                      : 'rgba(27, 34, 27, 0.95)',
                  boxShadow: '3px 3px 0 rgba(11, 14, 10, 0.9)',
                  '&:hover': {
                    transform: 'translate(-1px, -1px)',
                    boxShadow: '4px 4px 0 rgba(11, 14, 10, 0.92)'
                  }
                }}
              >
                <Box
                  sx={{
                    px: 0.3,
                    py: 0.55,
                    textAlign: 'center',
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#233021',
                    color: '#f5e6a6',
                    fontSize: 12,
                    fontWeight: 800
                  }}
                >
                  {floor.id}
                </Box>
                <Box sx={{ minWidth: 0 }}>
                  <Typography variant="body2" sx={{ fontWeight: 700, color: '#f3f7df' }} noWrap>
                    {floor.name}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#b6c0a6' }} noWrap>
                    {floor.head} leading {floor.specialty}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.35 }}>
                  {[0, 1, 2, 3].map((windowIndex) => (
                    <Box
                      key={`${floor.name}-${windowIndex}`}
                      sx={{
                        width: 9,
                        height: 9,
                        border: '1px solid rgba(0,0,0,0.5)',
                        bgcolor:
                          windowIndex < Math.min(queueCount + (isLead ? 1 : 0), 4)
                            ? floor.accent
                            : 'rgba(86, 96, 72, 0.45)'
                      }}
                    />
                  ))}
                </Box>
              </Box>
            );
          })}
      </Box>

      <Box
        sx={{
          mt: 0.9,
          px: 1,
          py: 0.7,
          border: '2px solid rgba(96, 117, 87, 0.9)',
          bgcolor: '#1e241b',
          boxShadow: '3px 3px 0 rgba(11, 14, 10, 0.85)'
        }}
      >
        <Typography variant="body2" sx={{ fontWeight: 700, color: '#f5e6a6' }}>
          OFF-DUTY LOUNGE
        </Typography>
        <Typography variant="caption" sx={{ color: '#d1d8b7' }}>
          Pixel annex for morale recovery and sync breaks
        </Typography>
      </Box>
    </Box>
  );
};

export default MiniatureOfficeTower;
