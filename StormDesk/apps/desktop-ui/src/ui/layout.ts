/* ── Storm Desk — Layout Engine ──────────────────────────────────── */

import type { Channel, Incident, UserSettings } from '../types';
import { getAllChannels, getLiveChannels, getEmbeddableChannels, getUnavailableChannels, getChannelByName, getRotationPool, MAX_ACTIVE_FRAMES, hasYouTubeApiKey } from '../channels';
import { renderViewerFrame, renderMicroViewer, destroyAllMicroViewers, getActiveFrameCount } from './viewers';
import { renderAlertOverlay, renderReasonPanel, hideEscalation } from './alerts';
import { renderSettingsPanel } from './settings';

let currentSettings: UserSettings;
let rotationTimer: ReturnType<typeof setInterval> | null = null;
let rotationIndex = 0;

export function initLayout(settings: UserSettings): void {
  currentSettings = settings;

  const root = document.getElementById('app');
  if (!root) throw new Error('Missing #app root element');

  root.innerHTML = '';

  root.appendChild(buildShell());
  applyLayoutMode();
  mountPinnedViewer();
  startMicroRotation();
  startSourceHealthIndicators();
}

/**
 * Adapt the grid layout based on how many live video feeds are available.
 * - 0 feeds: full-width incident panel, no video
 * - 1 feed:  video left, incidents right, no micro-grid
 * - 2+ feeds: video left, incidents center, micro-grid right
 */
function applyLayoutMode(): void {
  const main = document.getElementById('storm-main');
  if (!main) return;

  const liveCount = getLiveChannels().length;
  const microGrid = document.getElementById('micro-grid');
  const pinnedViewer = document.getElementById('pinned-viewer');

  if (liveCount === 0) {
    main.className = 'storm-main storm-layout-incidents-only';
    if (pinnedViewer) pinnedViewer.classList.add('hidden');
    if (microGrid) microGrid.classList.add('hidden');
  } else if (liveCount === 1) {
    main.className = 'storm-main storm-layout-single-feed';
    if (microGrid) microGrid.classList.add('hidden');
  } else {
    main.className = 'storm-main storm-layout-full';
  }
}

function buildShell(): HTMLElement {
  const shell = document.createElement('div');
  shell.className = 'storm-shell';
  shell.innerHTML = `
    <header class="storm-header">
      <div class="storm-logo">STORM DESK</div>
      <div class="storm-header-controls">
        <span class="storm-source-health" id="source-health-strip"></span>
        <button class="storm-btn" id="btn-settings" title="Settings">⚙</button>
      </div>
    </header>
    <main class="storm-main" id="storm-main">
      <section class="storm-pinned" id="pinned-viewer"></section>
      <section class="storm-incident-panel" id="incident-panel">
        <div class="incident-panel-header">
          <h2 class="incident-panel-title">Live Incidents</h2>
          <span class="incident-count" id="incident-count">0</span>
        </div>
        <div class="incident-list" id="incident-list"></div>
      </section>
      <aside class="storm-micro-grid" id="micro-grid"></aside>
    </main>
    <footer class="storm-ticker" id="incident-ticker"></footer>
    <div class="storm-escalation-overlay hidden" id="escalation-overlay"></div>
    <div class="storm-settings-drawer hidden" id="settings-drawer"></div>
    <div class="storm-reason-panel hidden" id="reason-panel"></div>
  `;

  const settingsBtn = shell.querySelector('#btn-settings') as HTMLButtonElement;
  settingsBtn.addEventListener('click', () => toggleSettingsDrawer());

  return shell;
}

function mountPinnedViewer(): void {
  const container = document.getElementById('pinned-viewer');
  if (!container) return;

  container.innerHTML = '';

  const pinned = getChannelByName(currentSettings.pinnedChannel);
  if (pinned && (pinned.health === 'live' || pinned.health === 'unknown')) {
    container.appendChild(renderViewerFrame(pinned, false));
    return;
  }

  const fallback = getEmbeddableChannels()[0];
  if (fallback) {
    container.appendChild(renderViewerFrame(fallback, false));
  } else {
    container.innerHTML = '<div class="storm-no-signal">No embeddable channels available</div>';
  }
}

export function startMicroRotation(): void {
  if (rotationTimer) clearInterval(rotationTimer);
  refreshMicroGrid();
  rotationTimer = setInterval(refreshMicroGrid, currentSettings.rotationIntervalMs);
}

function refreshMicroGrid(): void {
  const grid = document.getElementById('micro-grid');
  if (!grid) return;

  destroyAllMicroViewers(grid);

  const pool = getRotationPool(currentSettings.pinnedChannel);
  const frameBudget = MAX_ACTIVE_FRAMES - getActiveFrameCount();
  const maxSlots = Math.min(currentSettings.maxMicroViewers, pool.length, frameBudget);

  if (maxSlots <= 0) {
    grid.innerHTML = '<div class="storm-no-signal">Frame budget exhausted — reduce active viewers</div>';
    return;
  }

  const startIdx = rotationIndex % pool.length;
  for (let i = 0; i < maxSlots; i++) {
    const ch = pool[(startIdx + i) % pool.length];
    grid.appendChild(renderMicroViewer(ch, currentSettings.muteMicroFeeds));
  }
  rotationIndex += maxSlots;
}

export function renderIncidentTicker(incidents: Incident[]): void {
  const ticker = document.getElementById('incident-ticker');
  const list = document.getElementById('incident-list');
  const countEl = document.getElementById('incident-count');

  const sorted = [...incidents].sort((a, b) => b.score - a.score);

  if (countEl) countEl.textContent = String(sorted.length);

  /* ── Main incident panel (always visible, scrollable) ──────── */
  if (list) {
    list.innerHTML = '';
    const top = sorted.slice(0, 50);
    for (const inc of top) {
      const card = document.createElement('div');
      card.className = `incident-card storm-status-${inc.status}`;
      card.innerHTML = `
        <div class="incident-card-header">
          <span class="incident-card-score">${inc.score}</span>
          <span class="incident-card-headline">${escapeHtml(inc.headline)}</span>
          <span class="incident-card-status">${inc.status.toUpperCase()}</span>
        </div>
        <div class="incident-card-meta">
          <span>${inc.source_count} sources</span>
          <span>${inc.regions.join(', ') || 'Global'}</span>
          <span>${new Date(inc.updated_at).toLocaleTimeString()}</span>
        </div>
      `;
      card.addEventListener('click', () => showIncidentDetail(inc));
      list.appendChild(card);
    }
  }

  /* ── Bottom ticker strip (scrolling headlines) ─────────────── */
  if (ticker) {
    ticker.innerHTML = '';
    const tickerItems = sorted.slice(0, 20);
    for (const inc of tickerItems) {
      const item = document.createElement('div');
      item.className = `storm-ticker-item storm-status-${inc.status}`;
      item.innerHTML = `
        <span class="ticker-score">${inc.score}</span>
        <span class="ticker-headline">${escapeHtml(inc.headline)}</span>
        <span class="ticker-sources">${inc.source_count} src</span>
        <span class="ticker-status">${inc.status.toUpperCase()}</span>
      `;
      item.addEventListener('click', () => showIncidentDetail(inc));
      ticker.appendChild(item);
    }
  }
}

function showIncidentDetail(incident: Incident): void {
  renderReasonPanel(incident);
}

export function triggerEscalation(incident: Incident): void {
  renderAlertOverlay(incident);
  renderReasonPanel(incident);
}

export function dismissEscalation(): void {
  hideEscalation();
}

function toggleSettingsDrawer(): void {
  const drawer = document.getElementById('settings-drawer');
  if (!drawer) return;
  if (drawer.classList.contains('hidden')) {
    renderSettingsPanel(drawer, currentSettings, (updated) => {
      currentSettings = updated;
      mountPinnedViewer();
      startMicroRotation();
      startSourceHealthIndicators();
    });
    drawer.classList.remove('hidden');
  } else {
    drawer.classList.add('hidden');
  }
}

function startSourceHealthIndicators(): void {
  const strip = document.getElementById('source-health-strip');
  if (!strip) return;

  const refresh = () => {
    const channels = getAllChannels();
    const frameInfo = `<span class="health-frame-count" title="Active iframes">${getActiveFrameCount()}/${MAX_ACTIVE_FRAMES}</span>`;
    const dots = channels
      .map(
        (c) =>
          `<span class="health-dot health-${c.health}" title="${escapeHtml(c.name)}: ${c.health}${c.consecutiveFailures > 0 ? ` (${c.consecutiveFailures} failures)` : ''}"></span>`,
      )
      .join('');
    strip.innerHTML = dots + frameInfo;
  };

  refresh();
  setInterval(refresh, 15_000);
}

export function updateSettings(settings: UserSettings): void {
  currentSettings = settings;
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}
