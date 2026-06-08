/* ── Storm Desk — Event Worker Entry Point ──────────────────────── */

import express from 'express';
import cors from 'cors';
import { cfg } from './config';
import { fetchNewsData } from './sources/newsdata';
import { fetchMediaStack } from './sources/mediastack';
import { fetchRssFeeds } from './sources/rss';
import { normalizeBatch } from './pipeline/normalize';
import { clusterArticles, mergeNewArticlesIntoClusters, type ArticleCluster } from './pipeline/dedupe';
import { buildIncidentFromCluster, type Incident } from './pipeline/score';
import { evaluateEscalation, buildEscalationExplanation } from './pipeline/verify';
import {
  upsertIncident,
  getAllIncidents,
  getMajorIncidents,
  getIncidentById,
  pruneExpiredIncidents,
  getStoreStats,
} from './pipeline/store';

const app = express();

app.use(cors({
  origin: [
    'http://localhost:4318',
    'http://127.0.0.1:4318',
    'tauri://localhost',
    'https://tauri.localhost',
  ],
  methods: ['GET'],
}));

app.use(express.json());

let activeClusters: ArticleCluster[] = [];
let lastPollAt: string | null = null;
let pollErrors: string[] = [];
let pollCount = 0;

/* ── Source Aggregation ─────────────────────────────────────── */

async function fetchAllSources() {
  const results = await Promise.allSettled([
    fetchNewsData(),
    fetchMediaStack(),
    fetchRssFeeds(),
  ]);

  const articles = results.flatMap((r) => {
    if (r.status === 'fulfilled') return r.value;
    pollErrors.push(String(r.reason));
    return [];
  });

  // Trim error history
  if (pollErrors.length > 50) pollErrors = pollErrors.slice(-50);

  return articles;
}

/* ── Pipeline Refresh ───────────────────────────────────────── */

async function refreshLoop(): Promise<void> {
  pollCount++;
  const startMs = Date.now();

  try {
    const rawArticles = await fetchAllSources();
    const normalized = normalizeBatch(rawArticles);

    if (normalized.length === 0) {
      console.warn(`[worker] Poll #${pollCount}: No articles returned from any source`);
      lastPollAt = new Date().toISOString();
      return;
    }

    // Cluster incoming articles and merge with existing clusters
    if (activeClusters.length === 0) {
      activeClusters = clusterArticles(normalized);
    } else {
      activeClusters = mergeNewArticlesIntoClusters(activeClusters, normalized);
    }

    // Build/update incidents from clusters
    for (const cluster of activeClusters) {
      const incident = buildIncidentFromCluster(cluster);
      upsertIncident(incident);

      // Log escalation-worthy events
      if (incident.status === 'major') {
        const { canEscalate, reasons } = evaluateEscalation(incident);
        if (canEscalate) {
          const explanation = buildEscalationExplanation(incident);
          console.info(
            `[worker] MAJOR EVENT DETECTED: "${incident.headline}" — ${explanation}`,
          );
        }
      }
    }

    const elapsedMs = Date.now() - startMs;
    const stats = getStoreStats();
    console.info(
      `[worker] Poll #${pollCount}: ${normalized.length} articles → ${activeClusters.length} clusters → ` +
      `${stats.total} incidents (${stats.major} major, ${stats.elevated} elevated) in ${elapsedMs}ms`,
    );

    lastPollAt = new Date().toISOString();
  } catch (err) {
    console.error(`[worker] Poll #${pollCount} failed:`, err);
    pollErrors.push(String(err));
  }
}

/* ── API Routes ─────────────────────────────────────────────── */

app.get('/health', (_req, res) => {
  const stats = getStoreStats();
  res.json({
    ok: true,
    pollCount,
    lastPollAt,
    incidents: stats.total,
    major: stats.major,
    elevated: stats.elevated,
    errors: pollErrors.length,
    uptime: process.uptime(),
  });
});

app.get('/config', (_req, res) => {
  res.json({
    youtubeApiKey: cfg.youtube?.apiKey ?? null,
  });
});

app.get('/incidents', (_req, res) => {
  res.json(getAllIncidents());
});

app.get('/incidents/:id', (req, res) => {
  const incident = getIncidentById(req.params.id);
  if (!incident) {
    res.status(404).json({ error: 'Incident not found' });
    return;
  }
  res.json(incident);
});

app.get('/major', (_req, res) => {
  res.json(getMajorIncidents());
});

app.get('/stats', (_req, res) => {
  res.json({
    ...getStoreStats(),
    pollCount,
    lastPollAt,
    pollIntervalSeconds: cfg.poll.intervalSeconds,
    recentErrors: pollErrors.slice(-10),
    config: {
      newsdata: cfg.newsdata.enabled,
      mediastack: cfg.mediastack.enabled,
      gnews: cfg.gnews.enabled,
      rssFeeds: cfg.rss.feeds.length,
    },
  });
});

/* ── Bootstrap ──────────────────────────────────────────────── */

const pollIntervalMs = cfg.poll.intervalSeconds * 1000;

console.info(`[worker] Starting Storm Desk event worker on port ${cfg.server.port}`);
console.info(`[worker] Poll interval: ${cfg.poll.intervalSeconds}s`);
console.info(`[worker] Sources: NewsData=${cfg.newsdata.enabled} MediaStack=${cfg.mediastack.enabled} GNews=${cfg.gnews.enabled} RSS=${cfg.rss.feeds.length} feeds`);
console.info(`[worker] Escalation: minScore=${cfg.escalation.minScore} minSources=${cfg.escalation.minSources} requireWire=${cfg.escalation.requireWire}`);

refreshLoop().catch(console.error);
setInterval(() => {
  refreshLoop().catch(console.error);
}, pollIntervalMs);

// Prune expired incidents every hour
setInterval(() => {
  const pruned = pruneExpiredIncidents();
  if (pruned > 0) {
    console.info(`[worker] Pruned ${pruned} expired incidents`);
  }
}, 3_600_000);

app.listen(cfg.server.port, '127.0.0.1', () => {
  console.info(`[worker] Listening on http://127.0.0.1:${cfg.server.port}`);
});
