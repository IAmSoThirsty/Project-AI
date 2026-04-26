import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

export interface Intent {
  actor: 'human' | 'agent' | 'system';
  action: 'read' | 'write' | 'execute' | 'mutate';
  target: string;
  context?: Record<string, any>;
  origin: string;
}

export interface PillarVote {
  pillar: string;
  verdict: 'allow' | 'deny' | 'degrade';
  reason: string;
}

export interface GovernanceResult {
  intent_hash: string;
  tarl_version: string;
  votes: PillarVote[];
  final_verdict: 'allow' | 'deny' | 'degrade';
  timestamp: number;
}

export interface IntentResponse {
  message: string;
  governance: GovernanceResult;
}

export interface AuditRecord {
  intent_hash: string;
  tarl_version: string;
  votes: any[];
  final_verdict: string;
  timestamp: number;
}

export interface AuditResponse {
  tarl_version: string;
  tarl_signature: string;
  records: AuditRecord[];
}

export interface TarlRule {
  action: string;
  allowed_actors: string[];
  risk: string;
  default: string;
}

export interface TarlResponse {
  version: string;
  rules: TarlRule[];
}

export interface HealthResponse {
  status: string;
  tarl: string;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const governanceApi = {
  getHealth: async (): Promise<HealthResponse> => {
    const { data } = await api.get<HealthResponse>('/health');
    return data;
  },

  getTarl: async (): Promise<TarlResponse> => {
    const { data } = await api.get<TarlResponse>('/tarl');
    return data;
  },

  getAudit: async (limit: number = 50): Promise<AuditResponse> => {
    const { data } = await api.get<AuditResponse>(`/audit?limit=${limit}`);
    return data;
  },

  submitIntent: async (intent: Intent): Promise<IntentResponse> => {
    const { data } = await api.post<IntentResponse>('/intent', intent);
    return data;
  },
};

export default api;
