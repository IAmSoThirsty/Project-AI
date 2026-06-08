/* ── Storm Desk — Application Core ──────────────────────────────── */

import type { Incident, UserSettings, EscalationTrigger } from './types';
import { DEFAULT_SETTINGS } from './types';
import { runHealthCheckCycle, initChannels, setYouTubeApiKey } from './channels';
import { initLayout, renderIncidentTicker, triggerEscalation, updateSettings } from './ui/layout';
import { loadPersistedSettings } from './ui/settings';

const API_BASE = 'http://127.0.0.1:4319';
const POLL_MS = 5_000;
const HEALTH_CHECK_MS = 120_000;

let lastMajorId = '';
let settings: UserSettings;

export async function boot(): Promise<void> {
  settings = loadPersistedSettings() ?? DEFAULT_SETTINGS;

  document.documentElement.setAttribute('data-theme', settings.theme);

  /* Try to load YouTube API key from the worker config endpoint */
  try {
    const cfgRes = await fetch(`${API_BASE}/config`, { signal: AbortSignal.timeout(5_000) });
    if (cfgRes.ok) {
      const cfgData = await cfgRes.json();
      if (cfgData.youtubeApiKey) {
        setYouTubeApiKey(cfgData.youtubeApiKey);
      }
    }
  } catch { /* worker may not have /config yet, that's fine */ }

  await initChannels();
  initLayout(settings);

  scheduleIncidentPoll();
  scheduleChannelHealthCheck();
}

async function pollIncidents(): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/incidents`, {
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) {
      console.warn(`[storm-desk] Worker responded ${res.status}`);
      return;
    }
    const incidents: Incident[] = await res.json();
    renderIncidentTicker(incidents);
    evaluateEscalation(incidents);
  } catch (err) {
    console.warn('[storm-desk] Failed to reach event worker:', err);
  }
}

function evaluateEscalation(incidents: Incident[]): void {
  if (!settings.autoEscalate) return;

  const major = incidents.find(
    (i) =>
      i.status === 'major' &&
      i.score >= settings.minScoreForEscalation &&
      i.verification.independent_sources >= settings.minSourcesForEscalation &&
      (!settings.requireWireForEscalation || i.verification.wire_confirmed),
  );

  if (!major) return;
  if (major.id === lastMajorId) return;

  lastMajorId = major.id;

  const trigger: EscalationTrigger = {
    incident: major,
    reason: buildTriggerReason(major),
    triggeredAt: new Date().toISOString(),
  };

  console.info('[storm-desk] ESCALATION:', trigger.reason);
  triggerEscalation(major);
  notifyDesktop(major);
}

function buildTriggerReason(inc: Incident): string {
  const parts: string[] = [];
  parts.push(`${inc.verification.independent_sources} independent sources`);
  if (inc.keywords.length > 0) {
    parts.push(`keywords: ${inc.keywords.join(', ')}`);
  }
  if (inc.verification.wire_confirmed) parts.push('wire confirmed');
  if (inc.verification.broadcaster_confirmed) parts.push('broadcaster confirmed');
  parts.push(`score ${inc.score}/100`);
  return `Triggered because ${parts.join(' · ')}`;
}

async function notifyDesktop(incident: Incident): Promise<void> {
  if (!settings.notificationsEnabled) return;

  if ('__TAURI__' in window) {
    try {
      const { invoke } = (window as any).__TAURI__.core;
      await invoke('notify', {
        title: `⚠ MAJOR EVENT — Score ${incident.score}`,
        body: incident.headline,
      });
    } catch (err) {
      console.warn('[storm-desk] Tauri notification failed:', err);
    }
  } else if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`⚠ MAJOR EVENT — Score ${incident.score}`, {
      body: incident.headline,
    });
  }
}

function scheduleIncidentPoll(): void {
  pollIncidents();
  setInterval(() => {
    pollIncidents().catch(console.error);
  }, POLL_MS);
}

function scheduleChannelHealthCheck(): void {
  runHealthCheckCycle();
  setInterval(() => {
    runHealthCheckCycle().catch(console.error);
  }, HEALTH_CHECK_MS);
}

export function applySettings(updated: UserSettings): void {
  settings = updated;
  document.documentElement.setAttribute('data-theme', updated.theme);
  updateSettings(updated);
}
