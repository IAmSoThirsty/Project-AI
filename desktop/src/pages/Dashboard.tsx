import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
} from '@mui/material';
import { Refresh, Circle } from '@mui/icons-material';
import { governanceApi, HealthResponse, AuditRecord } from '../api/governance';

const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [recentAudits, setRecentAudits] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const healthData = await governanceApi.getHealth();
      setHealth(healthData);

      const auditData = await governanceApi.getAudit(5);
      setRecentAudits(auditData.records);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const getPillarColor = (pillar: string) => {
    switch (pillar.toLowerCase()) {
      case 'galahad': return '#9D7CFF';
      case 'cerberus': return '#FF4444';
      case 'codexdeus':
      case 'codex deus': return '#44FF88';
      default: return '#7C7CFF';
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict.toLowerCase()) {
      case 'allow': return '#4CAF50';
      case 'deny': return '#F44336';
      default: return '#FF9800';
    }
  };

  if (loading && !health) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Governance Dashboard
        </Typography>
        <IconButton onClick={loadDashboard} disabled={loading}>
          <Refresh />
        </IconButton>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Kernel Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" fontWeight="bold">
              Governance Kernel
            </Typography>
            <Circle
              sx={{
                fontSize: 12,
                color: health?.status === 'governance-online' ? '#00E676' : '#FF5252',
              }}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" mt={1}>
            {health?.status || 'Loading...'}
          </Typography>
          <Typography variant="body2" sx={{ color: '#7C7CFF', mt: 0.5 }}>
            TARL {health?.tarl || '...'}
          </Typography>
        </CardContent>
      </Card>

      {/* Triumvirate Pillars */}
      <Typography variant="h6" fontWeight="bold" mb={2}>
        Triumvirate Pillars
      </Typography>
      <Grid container spacing={2} mb={3}>
        {[
          { name: 'Galahad', role: 'Ethics', color: '#9D7CFF' },
          { name: 'Cerberus', role: 'Defense', color: '#FF4444' },
          { name: 'Codex Deus', role: 'Arbiter', color: '#44FF88' },
        ].map((pillar) => (
          <Grid item xs={4} key={pillar.name}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    bgcolor: `${pillar.color}20`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 12px',
                  }}
                >
                  <Box
                    sx={{
                      width: 30,
                      height: 30,
                      borderRadius: '50%',
                      bgcolor: pillar.color,
                    }}
                  />
                </Box>
                <Typography variant="body1" fontWeight="bold">
                  {pillar.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {pillar.role}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Decisions */}
      <Typography variant="h6" fontWeight="bold" mb={2}>
        Recent Decisions
      </Typography>
      {recentAudits.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="text.secondary">No recent decisions</Typography>
          </CardContent>
        </Card>
      ) : (
        recentAudits.map((audit) => (
          <Card key={audit.intent_hash} sx={{ mb: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Chip
                    label={audit.final_verdict.toUpperCase()}
                    size="small"
                    sx={{
                      bgcolor: `${getVerdictColor(audit.final_verdict)}20`,
                      color: getVerdictColor(audit.final_verdict),
                      fontWeight: 'bold',
                    }}
                  />
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    {new Date(audit.timestamp * 1000).toLocaleString()}
                  </Typography>
                </Box>
                <Typography variant="caption" fontFamily="monospace" color="primary">
                  {audit.intent_hash.substring(0, 8)}...
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};

export default Dashboard;
