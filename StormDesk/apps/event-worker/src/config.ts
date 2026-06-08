/* ── Storm Desk — Worker Configuration ──────────────────────────── */

import { config as dotenvConfig } from 'dotenv';
import { resolve } from 'node:path';

dotenvConfig({ path: resolve(process.cwd(), '.env') });

function envStr(key: string, fallback: string): string {
  return process.env[key]?.trim() || fallback;
}

function envInt(key: string, fallback: number): number {
  const raw = process.env[key];
  if (!raw) return fallback;
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function envBool(key: string, fallback: boolean): boolean {
  const raw = process.env[key]?.toLowerCase();
  if (!raw) return fallback;
  return raw === 'true' || raw === '1' || raw === 'yes';
}

function envList(key: string, fallback: string[]): string[] {
  const raw = process.env[key]?.trim();
  if (!raw) return fallback;
  return raw.split(',').map((s) => s.trim()).filter(Boolean);
}

export const cfg = {
  newsdata: {
    apiKey: envStr('NEWSDATA_API_KEY', ''),
    enabled: !!process.env.NEWSDATA_API_KEY,
  },
  mediastack: {
    apiKey: envStr('MEDIASTACK_API_KEY', ''),
    enabled: !!process.env.MEDIASTACK_API_KEY,
  },
  gnews: {
    apiKey: envStr('GNEWS_API_KEY', ''),
    enabled: !!process.env.GNEWS_API_KEY,
  },
  rss: {
    feeds: envList('RSS_FEEDS', [
      'https://feeds.bbci.co.uk/news/world/rss.xml',
      'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
      'https://www.aljazeera.com/xml/rss/all.xml',
    ]),
  },
  poll: {
    intervalSeconds: envInt('POLL_INTERVAL_SECONDS', 20),
  },
  escalation: {
    minScore: envInt('AUTO_TRIGGER_MIN_SCORE', 72),
    minSources: envInt('AUTO_TRIGGER_MIN_SOURCES', 2),
    requireWire: envBool('AUTO_TRIGGER_REQUIRE_WIRE', false),
  },
  server: {
    port: envInt('EVENT_WORKER_PORT', 4319),
  },
  youtube: {
    apiKey: envStr('YOUTUBE_API_KEY', ''),
  },
  store: {
    path: envStr('STORE_PATH', './data/incidents.db'),
    maxAgeDays: envInt('STORE_MAX_AGE_DAYS', 90),
  },
  log: {
    level: envStr('LOG_LEVEL', 'info') as 'debug' | 'info' | 'warn' | 'error',
    format: envStr('LOG_FORMAT', 'json') as 'json' | 'text',
  },
} as const;
