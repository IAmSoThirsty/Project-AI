/* ── Storm Desk — Shared UI Types ───────────────────────────────── */

export type Article = {
  title: string;
  description?: string;
  source: string;
  url: string;
  publishedAt: string;
  country?: string;
  language?: string;
};

export type IncidentSource = {
  name: string;
  url: string;
  published_at: string;
  title: string;
};

export type IncidentVerification = {
  independent_sources: number;
  wire_confirmed: boolean;
  broadcaster_confirmed: boolean;
};

export type IncidentStatus = 'watch' | 'elevated' | 'major';

export type Incident = {
  id: string;
  headline: string;
  summary: string;
  keywords: string[];
  regions: string[];
  source_count: number;
  sources: IncidentSource[];
  score: number;
  status: IncidentStatus;
  verification: IncidentVerification;
  first_seen_at: string;
  updated_at: string;
};

export type ChannelKind = 'youtube' | 'direct' | 'hls';

export type ChannelHealth = 'live' | 'degraded' | 'blocked' | 'offline' | 'unavailable' | 'unknown';

export type Channel = {
  name: string;
  channelId: string;
  videoId: string | null;
  embed: string;
  kind: ChannelKind;
  health: ChannelHealth;
  fallbackEmbed?: string;
  lastChecked?: string;
  consecutiveFailures: number;
  verified: boolean;
};

export type EscalationTrigger = {
  incident: Incident;
  reason: string;
  triggeredAt: string;
};

export type UserSettings = {
  pinnedChannel: string;
  rotationIntervalMs: number;
  autoEscalate: boolean;
  minScoreForEscalation: number;
  minSourcesForEscalation: number;
  requireWireForEscalation: boolean;
  muteMicroFeeds: boolean;
  maxMicroViewers: number;
  theme: 'dark' | 'light';
  notificationsEnabled: boolean;
};

export const DEFAULT_SETTINGS: UserSettings = {
  pinnedChannel: 'Al Jazeera English',
  rotationIntervalMs: 30_000,
  autoEscalate: true,
  minScoreForEscalation: 72,
  minSourcesForEscalation: 2,
  requireWireForEscalation: false,
  muteMicroFeeds: true,
  maxMicroViewers: 6,
  theme: 'dark',
  notificationsEnabled: true,
};
