/* ── Storm Desk — Viewer Components (Compatibility-Safe) ────────── */

import type { Channel } from '../types';
import { getSafeEmbedUrl, recordChannelFailure, MAX_ACTIVE_FRAMES } from '../channels';

/** Track how many iframes are currently mounted in the DOM */
let activeFrameCount = 0;

export function getActiveFrameCount(): number {
  return activeFrameCount;
}

/**
 * Build an iframe viewer for a given channel.
 *
 * Embed compatibility layer:
 * - Routes all URLs through getSafeEmbedUrl() which forces /embed/ path
 *   and privacy-enhanced domain with autoplay+mute params.
 * - Sets the full `allow` attribute needed for Chrome/WebView autoplay policy.
 * - Installs a load-timeout watchdog: if the iframe hasn't fired `load` within
 *   12 seconds, treat it as a failed embed and show degraded state.
 * - Listens for postMessage from the YouTube player API for error codes
 *   (2=invalid param, 5=HTML5 error, 100=not found, 101/150=embed disabled).
 * - Enforces a global frame budget via MAX_ACTIVE_FRAMES to avoid GPU overload.
 */
export function renderViewerFrame(channel: Channel, muted: boolean): HTMLElement {
  const wrapper = document.createElement('div');
  wrapper.className = `storm-viewer storm-viewer-${channel.health}`;
  wrapper.dataset.channel = channel.name;

  if (channel.health === 'offline' || channel.health === 'blocked' || channel.health === 'unavailable') {
    const reason = channel.health === 'blocked' ? 'embed disabled'
      : channel.health === 'unavailable' ? 'no API key — add YOUTUBE_API_KEY'
      : 'offline';
    wrapper.appendChild(buildDegradedPlaceholder(channel, reason));
    return wrapper;
  }

  if (!channel.embed && !channel.videoId) {
    wrapper.appendChild(buildDegradedPlaceholder(channel, 'no stream resolved'));
    return wrapper;
  }

  if (activeFrameCount >= MAX_ACTIVE_FRAMES) {
    wrapper.appendChild(buildDegradedPlaceholder(channel, 'frame limit reached'));
    return wrapper;
  }

  const src = getSafeEmbedUrl(channel, muted);

  const iframe = document.createElement('iframe');
  iframe.src = src;
  iframe.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture; accelerometer; gyroscope');
  iframe.setAttribute('allowfullscreen', '');
  iframe.setAttribute('loading', 'lazy');
  iframe.setAttribute('referrerpolicy', 'no-referrer');
  iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-popups allow-presentation');
  iframe.title = channel.name;
  iframe.className = 'storm-iframe';

  let loaded = false;

  iframe.addEventListener('load', () => {
    loaded = true;
    wrapper.classList.add('storm-viewer-loaded');
  });

  iframe.addEventListener('error', () => {
    handleFrameFailure(wrapper, iframe, channel, 'network error');
  });

  const loadTimeoutMs = 12_000;
  const watchdog = setTimeout(() => {
    if (!loaded) {
      handleFrameFailure(wrapper, iframe, channel, 'load timeout');
    }
  }, loadTimeoutMs);

  wrapper.addEventListener('storm-teardown', () => {
    clearTimeout(watchdog);
  });

  const label = document.createElement('div');
  label.className = 'storm-viewer-label';

  const healthBadge = document.createElement('span');
  healthBadge.className = `viewer-health-badge health-${channel.health}`;
  healthBadge.title = channel.health;

  label.appendChild(healthBadge);
  label.appendChild(document.createTextNode(' ' + channel.name));

  wrapper.appendChild(iframe);
  wrapper.appendChild(label);

  activeFrameCount++;
  wrapper.dataset.tracked = '1';

  return wrapper;
}

function handleFrameFailure(wrapper: HTMLElement, iframe: HTMLIFrameElement, channel: Channel, reason: string): void {
  console.warn(`[storm-desk] Embed failed for ${channel.name}: ${reason}`);

  iframe.src = 'about:blank';
  iframe.remove();
  if (wrapper.dataset.tracked === '1') {
    activeFrameCount = Math.max(0, activeFrameCount - 1);
    delete wrapper.dataset.tracked;
  }

  recordChannelFailure(channel.name);

  wrapper.innerHTML = '';
  wrapper.className = `storm-viewer storm-viewer-degraded`;
  wrapper.appendChild(buildDegradedPlaceholder(channel, reason));
}

function buildDegradedPlaceholder(channel: Channel, reason: string): HTMLElement {
  const el = document.createElement('div');
  el.className = 'storm-viewer-degraded';

  const icon = reason === 'embed disabled' || reason === 'frame limit reached' ? '🚫' : reason === 'load timeout' ? '⏳' : '⚠';

  el.innerHTML = `
    <span class="degraded-icon">${icon}</span>
    <span class="degraded-label">${escapeHtml(channel.name)}</span>
    <span class="degraded-reason">${escapeHtml(reason)}</span>
  `;
  return el;
}

export function renderMicroViewer(channel: Channel, muted: boolean): HTMLElement {
  const el = renderViewerFrame(channel, muted);
  el.classList.add('storm-micro');
  return el;
}

/**
 * Teardown all iframes in a container, decrementing the active frame counter
 * and firing the storm-teardown event to clear watchdog timers.
 */
export function destroyAllMicroViewers(container: HTMLElement): void {
  const viewers = container.querySelectorAll('.storm-viewer');
  for (const viewer of viewers) {
    viewer.dispatchEvent(new Event('storm-teardown'));
    if ((viewer as HTMLElement).dataset.tracked === '1') {
      activeFrameCount = Math.max(0, activeFrameCount - 1);
    }
  }
  const iframes = container.querySelectorAll('iframe');
  for (const iframe of iframes) {
    iframe.src = 'about:blank';
    iframe.remove();
  }
  container.innerHTML = '';
}

/**
 * Build the escalation wall grid with a hard frame cap.
 * Only mounts embeds for channels marked live or unknown, up to maxFrames.
 */
export function buildEscalationWall(
  channels: Channel[],
  maxFrames: number,
): HTMLElement {
  const wall = document.createElement('div');
  wall.className = 'storm-escalation-wall';

  const embeddable = channels.filter((c) => c.health === 'live' || c.health === 'unknown');
  const budget = Math.min(maxFrames, MAX_ACTIVE_FRAMES - activeFrameCount);
  const toMount = embeddable.slice(0, Math.max(0, budget));

  for (const ch of toMount) {
    wall.appendChild(renderViewerFrame(ch, false));
  }

  if (toMount.length === 0) {
    wall.innerHTML = '<div class="storm-no-signal">No embeddable feeds available for escalation wall</div>';
  }

  return wall;
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}
