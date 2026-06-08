/* ── Storm Desk — Alert & Escalation UI ─────────────────────────── */

import type { Incident } from '../types';
import { getLiveChannels } from '../channels';
import { buildEscalationWall } from './viewers';

/**
 * Render the full-screen escalation overlay with the multi-channel wall
 * and the incident headline bar.
 */
export function renderAlertOverlay(incident: Incident): void {
  const overlay = document.getElementById('escalation-overlay');
  if (!overlay) return;

  overlay.innerHTML = '';
  overlay.classList.remove('hidden');

  const headlineBar = document.createElement('div');
  headlineBar.className = 'escalation-headline-bar';
  headlineBar.innerHTML = `
    <span class="escalation-badge">MAJOR EVENT</span>
    <span class="escalation-headline">${escapeHtml(incident.headline)}</span>
    <button class="storm-btn escalation-dismiss" id="dismiss-escalation">✕ DISMISS</button>
  `;
  overlay.appendChild(headlineBar);

  const wall = buildEscalationWall(getLiveChannels(), 6);
  overlay.appendChild(wall);

  const dismissBtn = overlay.querySelector('#dismiss-escalation') as HTMLButtonElement;
  dismissBtn.addEventListener('click', () => hideEscalation());
}

/**
 * Render the transparent reason panel showing why escalation was triggered.
 * Displays source count, keyword hits, wire/broadcaster confirmation status.
 */
export function renderReasonPanel(incident: Incident): void {
  const panel = document.getElementById('reason-panel');
  if (!panel) return;

  panel.classList.remove('hidden');

  const keywordsDisplay = incident.keywords.length > 0
    ? incident.keywords.map((k) => `<span class="reason-keyword">${escapeHtml(k)}</span>`).join(' ')
    : '<em>none</em>';

  const sourcesDisplay = incident.sources
    .map(
      (s) =>
        `<li><a href="${escapeAttr(s.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(s.name)}</a> — ${escapeHtml(s.title)}</li>`,
    )
    .join('');

  const wireIcon = incident.verification.wire_confirmed ? '✓' : '✗';
  const bcastIcon = incident.verification.broadcaster_confirmed ? '✓' : '✗';

  panel.innerHTML = `
    <div class="reason-card">
      <div class="reason-header">
        <h3 class="reason-title">${escapeHtml(incident.headline)}</h3>
        <button class="storm-btn reason-close" id="close-reason">✕</button>
      </div>
      <div class="reason-body">
        <p class="reason-summary">${escapeHtml(incident.summary)}</p>
        <div class="reason-meta">
          <div class="reason-row"><strong>Score:</strong> ${incident.score}/100</div>
          <div class="reason-row"><strong>Status:</strong> <span class="storm-status-${incident.status}">${incident.status.toUpperCase()}</span></div>
          <div class="reason-row"><strong>Independent sources:</strong> ${incident.verification.independent_sources}</div>
          <div class="reason-row"><strong>Wire confirmed:</strong> ${wireIcon}</div>
          <div class="reason-row"><strong>Broadcaster confirmed:</strong> ${bcastIcon}</div>
          <div class="reason-row"><strong>Keywords:</strong> ${keywordsDisplay}</div>
          <div class="reason-row"><strong>Regions:</strong> ${incident.regions.map(escapeHtml).join(', ') || 'Global'}</div>
          <div class="reason-row"><strong>First seen:</strong> ${new Date(incident.first_seen_at).toLocaleString()}</div>
        </div>
        <div class="reason-sources">
          <h4>Contributing Sources</h4>
          <ul>${sourcesDisplay}</ul>
        </div>
        <p class="reason-explanation">
          Triggered because <strong>${incident.verification.independent_sources}</strong> sources mentioned
          <strong>${incident.keywords.join(' + ') || 'this event'}</strong> within the clustering window.
        </p>
      </div>
    </div>
  `;

  const closeBtn = panel.querySelector('#close-reason') as HTMLButtonElement;
  closeBtn.addEventListener('click', () => {
    panel.classList.add('hidden');
    panel.innerHTML = '';
  });
}

export function hideEscalation(): void {
  const overlay = document.getElementById('escalation-overlay');
  if (overlay) {
    const iframes = overlay.querySelectorAll('iframe');
    for (const iframe of iframes) {
      iframe.src = 'about:blank';
    }
    overlay.innerHTML = '';
    overlay.classList.add('hidden');
  }
  const panel = document.getElementById('reason-panel');
  if (panel) {
    panel.innerHTML = '';
    panel.classList.add('hidden');
  }
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function escapeAttr(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
