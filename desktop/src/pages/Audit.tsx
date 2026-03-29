import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { governanceApi, AuditRecord } from '../api/governance';

const AuditPage: React.FC = () => {
  const [audits, setAudits] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAudits();
  }, []);

  const loadAudits = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governanceApi.getAudit(100);
      setAudits(data.records);
    } catch (err: any) {
      setError(err.message || 'Failed to load audit log');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict.toLowerCase()) {
      case 'allow': return '#4CAF50';
      case 'deny': return '#F44336';
      default: return '#FF9800';
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
        Audit Log
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            Immutable audit trail of all governance decisions. Every intent evaluation is
            cryptographically logged.
          </Typography>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {audits.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="text.secondary">No audit records found</Typography>
          </CardContent>
        </Card>
      ) : (
        audits.map((audit) => (
          <Card key={audit.intent_hash} sx={{ mb: 2 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box flex={1}>
                  <Chip
                    label={audit.final_verdict.toUpperCase()}
                    size="small"
                    sx={{
                      bgcolor: `${getVerdictColor(audit.final_verdict)}20`,
                      color: getVerdictColor(audit.final_verdict),
                      fontWeight: 'bold',
                      mb: 1,
                    }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {new Date(audit.timestamp * 1000).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" fontFamily="monospace" color="text.secondary">
                    Hash: {audit.intent_hash.substring(0, 16)}...
                  </Typography>
                </Box>
                <Chip
                  label={`TARL ${audit.tarl_version}`}
                  size="small"
                  variant="outlined"
                  sx={{ color: '#7C7CFF', borderColor: '#7C7CFF' }}
                />
              </Box>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};

export default AuditPage;
