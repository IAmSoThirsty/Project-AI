// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

// App Configuration
export const APP_NAME = 'Project AI';
export const APP_VERSION = '1.0.0';

// Colors
export const COLORS = {
  // Governance Colors
  governancePurple: '#7C7CFF',
  governanceRed: '#FF5757',
  governanceGreen: '#57FF57',
  
  // Pillar Colors
  galahad: '#9D7CFF',
  cerberus: '#FF4444',
  codexDeus: '#44FF88',
  
  // Verdict Colors
  allow: '#4CAF50',
  deny: '#F44336',
  degrade: '#FF9800',
  
  // Background
  backgroundDark: '#0B0E14',
  backgroundDarkSecondary: '#1A1F36',
  surfaceDark: '#1E1E2E',
  
  // Status
  online: '#00E676',
  offline: '#FF5252',
  degraded: '#FFAB00',
} as const;

// Actor Types
export const ACTOR_TYPES = {
  HUMAN: 'human',
  AGENT: 'agent',
  SYSTEM: 'system',
} as const;

// Action Types
export const ACTION_TYPES = {
  READ: 'read',
  WRITE: 'write',
  EXECUTE: 'execute',
  MUTATE: 'mutate',
} as const;

// Verdict Types
export const VERDICT_TYPES = {
  ALLOW: 'allow',
  DENY: 'deny',
  DEGRADE: 'degrade',
} as const;

// Refresh Intervals (ms)
export const REFRESH_INTERVALS = {
  DASHBOARD: 10000,  // 10 seconds
  AUDIT: 30000,      // 30 seconds
  HEALTH: 5000,      // 5 seconds
} as const;
