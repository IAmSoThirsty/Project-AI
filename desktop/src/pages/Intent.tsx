import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  ToggleButtonGroup,
  ToggleButton,
  Alert,
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material';
import { Send } from '@mui/icons-material';
import { governanceApi, Intent, IntentResponse } from '../api/governance';

const IntentPage: React.FC = () => {
  const [actor, setActor] = useState<'human' | 'agent' | 'system'>('human');
  const [action, setAction] = useState<'read' | 'write' | 'execute' | 'mutate'>('read');
  const [target, setTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IntentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!target.trim()) {
      setError('Target resource is required');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const intent: Intent = {
        actor,
        action,
        target: target.trim(),
        origin: 'desktop_app',
      };

      const response = await governanceApi.submitIntent(intent);
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || 'Failed to submit intent');
    } finally {
      setLoading(false);
    }
  };

  const getPillarColor = (pillar: string) => {
    switch (pillar.toLowerCase()) {
      case 'galahad': return '#9D7CFF';
      case 'cerberus': return '#FF4444';
      default: return '#44FF88';
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict.toLowerCase()) {
      case 'allow': return '#4CAF50';
      case 'deny': return '#F44336';
      default: return '#FF9800';
    }
  };

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" mb={3}>
        Submit Intent
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            Submit an intent for Triumvirate evaluation. All requests pass through TARL governance.
          </Typography>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Actor Type
          </Typography>
          <ToggleButtonGroup
            value={actor}
            exclusive
            onChange={(_, value) => value && setActor(value)}
            fullWidth
            sx={{ mb: 3 }}
          >
            <ToggleButton value="human">Human</ToggleButton>
            <ToggleButton value="agent">Agent</ToggleButton>
            <ToggleButton value="system">System</ToggleButton>
          </ToggleButtonGroup>

          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Action Type
          </Typography>
          <ToggleButtonGroup
            value={action}
            exclusive
            onChange={(_, value) => value && setAction(value)}
            fullWidth
            sx={{ mb: 3 }}
          >
            <ToggleButton value="read">Read</ToggleButton>
            <ToggleButton value="write">Write</ToggleButton>
            <ToggleButton value="execute">Execute</ToggleButton>
            <ToggleButton value="mutate">Mutate</ToggleButton>
          </ToggleButtonGroup>

          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Target Resource
          </Typography>
          <TextField
            fullWidth
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="/path/to/resource"
            sx={{ mb: 3 }}
          />

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleSubmit}
            disabled={loading || !target.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          >
            {loading ? 'Submitting...' : 'Submit Intent'}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Card
          sx={{
            borderLeft: 4,
            borderColor: getVerdictColor(result.governance.final_verdict),
          }}
        >
          <CardContent>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Governance Result
            </Typography>

            <Chip
              label={result.governance.final_verdict.toUpperCase()}
              sx={{
                bgcolor: `${getVerdictColor(result.governance.final_verdict)}20`,
                color: getVerdictColor(result.governance.final_verdict),
                fontWeight: 'bold',
                mb: 2,
              }}
            />

            <Typography variant="body2" color="text.secondary" fontFamily="monospace">
              Hash: {result.governance.intent_hash.substring(0, 16)}...
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              TARL {result.governance.tarl_version}
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Pillar Votes:
            </Typography>

            {result.governance.votes.map((vote) => (
              <Box key={vote.pillar} mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                  <Typography
                    variant="body2"
                    fontWeight="bold"
                    sx={{ color: getPillarColor(vote.pillar) }}
                  >
                    {vote.pillar}
                  </Typography>
                  <Chip
                    label={vote.verdict}
                    size="small"
                    sx={{
                      bgcolor: `${getVerdictColor(vote.verdict)}20`,
                      color: getVerdictColor(vote.verdict),
                    }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {vote.reason}
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default IntentPage;
