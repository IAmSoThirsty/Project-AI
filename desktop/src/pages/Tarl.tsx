import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Grid,
} from '@mui/material';
import { governanceApi, TarlRule } from '../api/governance';

const TarlPage: React.FC = () => {
  const [rules, setRules] = useState<TarlRule[]>([]);
  const [version, setVersion] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTarl();
  }, []);

  const loadTarl = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governanceApi.getTarl();
      setRules(data.rules);
      setVersion(data.version);
    } catch (err: any) {
      setError(err.message || 'Failed to load TARL rules');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'low': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'high':
      case 'critical': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        TARL Governance
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            Trust & Authorization Runtime Layer
          </Typography>
          <Typography variant="body1" color="primary" fontWeight="bold" gutterBottom>
            Version {version}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            TARL defines the governance rules that all intents must satisfy. These rules are
            immutable and cryptographically signed.
          </Typography>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {rules.map((rule) => (
        <Card key={rule.action} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight="bold">
                {rule.action.toUpperCase()}
              </Typography>
              <Chip
                label={rule.risk.toUpperCase()}
                sx={{
                  bgcolor: `${getRiskColor(rule.risk)}20`,
                  color: getRiskColor(rule.risk),
                  fontWeight: 'bold',
                }}
              />
            </Box>

            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Allowed Actors:
            </Typography>
            {rule.allowed_actors.length === 0 ? (
              <Typography variant="body2" color="error" mb={2}>
                None (Always denied)
              </Typography>
            ) : (
              <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                {rule.allowed_actors.map((actor) => (
                  <Chip
                    key={actor}
                    label={actor}
                    size="small"
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                    }}
                  />
                ))}
              </Box>
            )}

            <Typography variant="body2" color="text.secondary">
              Default Verdict: <strong>{rule.default.toUpperCase()}</strong>
            </Typography>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default TarlPage;
