import { useState, useEffect } from 'react';
import { governanceApi, HealthResponse, TarlResponse, AuditResponse } from '../api/governance';

interface UseHealthResult {
  health: HealthResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useHealth = (): UseHealthResult => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governanceApi.getHealth();
      setHealth(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch health');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return { health, loading, error, refetch: fetchHealth };
};

interface UseTarlResult {
  tarl: TarlResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useTarl = (): UseTarlResult => {
  const [tarl, setTarl] = useState<TarlResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTarl = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governanceApi.getTarl();
      setTarl(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch TARL');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTarl();
  }, []);

  return { tarl, loading, error, refetch: fetchTarl };
};

interface UseAuditResult {
  audit: AuditResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useAudit = (limit: number = 50): UseAuditResult => {
  const [audit, setAudit] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAudit = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await governanceApi.getAudit(limit);
      setAudit(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch audit');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, [limit]);

  return { audit, loading, error, refetch: fetchAudit };
};
