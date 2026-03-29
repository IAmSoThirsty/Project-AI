import React from 'react';
import { Box, Button, Chip, Stack, Typography } from '@mui/material';
import {
  BugReport,
  Flare,
  Security,
  TravelExplore,
  VerifiedUser
} from '@mui/icons-material';
import {
  CityTwinDistrict,
  CityTwinIncident,
  CityTwinScenarioKind
} from '../types/sovereign';

interface CityTwinPanelProps {
  districts: CityTwinDistrict[];
  incidents: CityTwinIncident[];
  activeDistrictId: string;
  activeFloorName: string;
  onSelectDistrict: (districtId: string) => void;
  onInjectScenario: (kind: CityTwinScenarioKind, districtId: string) => void;
}

const scenarioDeck: Array<{
  kind: CityTwinScenarioKind;
  label: string;
  icon: typeof BugReport;
  tone: string;
}> = [
  { kind: 'drift', label: 'Inject Drift', icon: Flare, tone: '#f4ba3f' },
  { kind: 'virus', label: 'Inject Virus', icon: BugReport, tone: '#f87171' },
  { kind: 'honeypot', label: 'Deploy Honeypot', icon: Security, tone: '#7dd3fc' },
  { kind: 'recovery', label: 'Run Recovery', icon: VerifiedUser, tone: '#86efac' }
];

const CityTwinPanel: React.FC<CityTwinPanelProps> = ({
  districts,
  incidents,
  activeDistrictId,
  activeFloorName,
  onSelectDistrict,
  onInjectScenario
}) => {
  const activeDistrict =
    districts.find((district) => district.id === activeDistrictId) || districts[0] || null;
  const cityHealth = Math.max(
    0,
    Math.round(
      districts.reduce((sum, district) => sum + district.defense + district.throughput - district.drift, 0) /
        Math.max(1, districts.length * 2)
    )
  );
  const activeIncidents = incidents.filter((incident) => incident.status === 'active').length;

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 1.5,
        p: 2,
        border: '2px solid rgba(80, 101, 71, 0.95)',
        background: 'linear-gradient(180deg, #161c14 0%, #0f130d 100%)',
        boxShadow: '5px 5px 0 rgba(10, 13, 9, 0.92)',
        overflow: 'auto'
      }}
    >
      <Box>
        <Typography variant="overline" sx={{ color: '#f4ba3f', letterSpacing: 2.1, fontWeight: 700 }}>
          City Twin
        </Typography>
        <Typography
          variant="h4"
          sx={{ mt: 0.35, color: '#f5e6a6', fontFamily: 'var(--font-code)', fontWeight: 800 }}
        >
          Pre-VR Simulation Deck
        </Typography>
        <Typography variant="body2" sx={{ mt: 0.8, color: '#c7d0b1', maxWidth: 840 }}>
          District telemetry, incident staging, and repair-crew routing for the future embodied city
          layer. This is the offline 2D command view that VR will inherit from.
        </Typography>
      </Box>

      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
        <Chip label={`City health ${cityHealth}%`} size="small" sx={{ color: '#86efac' }} />
        <Chip label={`${activeIncidents} active incidents`} size="small" sx={{ color: '#f4ba3f' }} />
        <Chip label={`Lead floor ${activeFloorName}`} size="small" sx={{ color: '#7dd3fc' }} />
        <Chip label="VR staging offline" size="small" sx={{ color: '#c4b5fd' }} />
      </Stack>

      <Box
        sx={{
          p: 1.5,
          border: '2px solid rgba(96, 117, 87, 0.9)',
          bgcolor: '#121710',
          boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
        }}
      >
        <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
          Pixel District Grid
        </Typography>
        <Box
          sx={{
            mt: 1.25,
            display: 'grid',
            gap: 1,
            gridTemplateColumns: {
              xs: 'repeat(2, minmax(0, 1fr))',
              md: 'repeat(4, minmax(0, 1fr))'
            }
          }}
        >
          {districts.map((district) => {
            const isActive = district.id === activeDistrictId;

            return (
              <Box
                key={district.id}
                onClick={() => onSelectDistrict(district.id)}
                sx={{
                  p: 1,
                  cursor: 'pointer',
                  border: '2px solid',
                  borderColor: isActive ? '#f4ba3f' : 'rgba(96, 117, 87, 0.9)',
                  bgcolor: isActive ? 'rgba(244, 186, 63, 0.12)' : '#1f261c',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                }}
              >
                <Typography variant="body2" sx={{ color: '#f3f7df', fontWeight: 700 }} noWrap>
                  {district.label}
                </Typography>
                <Typography variant="caption" sx={{ color: '#a5b39a' }} noWrap>
                  {district.assignedFloor}
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.35, mt: 1 }}>
                  {Array.from({ length: 6 }).map((_, index) => (
                    <Box
                      key={`${district.id}-${index}`}
                      sx={{
                        width: 10,
                        height: 10,
                        border: '1px solid rgba(0,0,0,0.45)',
                        bgcolor:
                          index < Math.min(6, Math.max(1, Math.round(district.throughput / 18)))
                            ? '#7dd3fc'
                            : 'rgba(86, 96, 72, 0.45)'
                      }}
                    />
                  ))}
                </Box>
                <Stack direction="row" spacing={0.6} useFlexGap flexWrap="wrap" sx={{ mt: 1 }}>
                  <Chip label={`Drift ${district.drift}`} size="small" sx={{ color: '#f4ba3f' }} />
                  <Chip label={`Defense ${district.defense}`} size="small" sx={{ color: '#86efac' }} />
                </Stack>
              </Box>
            );
          })}
        </Box>
      </Box>

      {activeDistrict && (
        <Box
          sx={{
            p: 1.5,
            border: '2px solid rgba(96, 117, 87, 0.9)',
            bgcolor: '#121710',
            boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
          }}
        >
          <Stack direction="row" justifyContent="space-between" spacing={2} alignItems="center">
            <Box>
              <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
                Active District
              </Typography>
              <Typography
                variant="h6"
                sx={{ mt: 0.4, color: '#f3f7df', fontFamily: 'var(--font-code)', fontWeight: 800 }}
              >
                {activeDistrict.label}
              </Typography>
              <Typography variant="body2" sx={{ mt: 0.6, color: '#c7d0b1' }}>
                {activeDistrict.focus}
              </Typography>
            </Box>
            <TravelExplore sx={{ color: '#7dd3fc' }} />
          </Stack>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.25 }}>
            <Chip label={`Queue ${activeDistrict.queueDepth}`} size="small" sx={{ color: '#f5e6a6' }} />
            <Chip label={`Incidents ${activeDistrict.incidentCount}`} size="small" sx={{ color: '#f87171' }} />
            <Chip label={activeDistrict.assignedFloor} size="small" sx={{ color: '#7dd3fc' }} />
          </Stack>

          <Typography variant="caption" sx={{ mt: 1.2, display: 'block', color: '#a5b39a' }}>
            Scenario injection deck
          </Typography>
          <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 0.8 }}>
            {scenarioDeck.map((scenario) => {
              const Icon = scenario.icon;
              return (
                <Button
                  key={scenario.kind}
                  size="small"
                  startIcon={<Icon fontSize="small" />}
                  onClick={() => onInjectScenario(scenario.kind, activeDistrict.id)}
                  sx={{
                    color: scenario.tone,
                    border: '2px solid rgba(96, 117, 87, 0.9)',
                    bgcolor: '#1f261c',
                    borderRadius: 0,
                    boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                  }}
                >
                  {scenario.label}
                </Button>
              );
            })}
          </Stack>
        </Box>
      )}

      <Box
        sx={{
          p: 1.5,
          border: '2px solid rgba(96, 117, 87, 0.9)',
          bgcolor: '#121710',
          boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
        }}
      >
        <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
          Incident Feed
        </Typography>
        <Stack spacing={0.9} sx={{ mt: 1.2 }}>
          {incidents.length === 0 && (
            <Typography variant="body2" sx={{ color: '#a5b39a' }}>
              No simulated incidents staged yet.
            </Typography>
          )}
          {incidents.slice(0, 6).map((incident) => (
            <Box
              key={incident.id}
              sx={{
                p: 1,
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor:
                  incident.status === 'active'
                    ? '#2a1714'
                    : incident.status === 'contained'
                      ? '#172018'
                      : '#1c1f24'
              }}
            >
              <Stack direction="row" justifyContent="space-between" spacing={1}>
                <Typography variant="body2" sx={{ color: '#f3f7df', fontWeight: 700 }}>
                  {incident.title}
                </Typography>
                <Typography variant="caption" sx={{ color: '#a5b39a' }}>
                  {incident.createdAt}
                </Typography>
              </Stack>
              <Typography variant="body2" sx={{ mt: 0.6, color: '#c7d0b1' }}>
                {incident.detail}
              </Typography>
              <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 0.8 }}>
                <Chip label={incident.district} size="small" sx={{ color: '#7dd3fc' }} />
                <Chip label={incident.assignedFloor} size="small" sx={{ color: '#f5e6a6' }} />
                <Chip label={incident.status} size="small" sx={{ color: '#86efac' }} />
                <Chip label={`Severity ${incident.severity}`} size="small" sx={{ color: '#f87171' }} />
              </Stack>
            </Box>
          ))}
        </Stack>
      </Box>
    </Box>
  );
};

export default CityTwinPanel;
