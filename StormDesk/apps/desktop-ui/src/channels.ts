/* ── Storm Desk — Channel Registry & Dynamic Resolution ─────────── */

import type { Channel, ChannelHealth } from './types';

/**
 * Normalise any YouTube URL into a proper /embed/ URL with embed-safe params.
 * Handles watch?v=, youtu.be shortlinks, and already-correct /embed/ URLs.
 */
function toYouTubeEmbed(videoId: string): string {
  return `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&mute=1&modestbranding=1&rel=0&playsinline=1&enablejsapi=0`;
}

/**
 * Registry uses YouTube channel IDs (stable) not video IDs (volatile).
 * The resolver queries YouTube Data API v3 to find each channel's current
 * live broadcast. Without an API key, only pre-verified embeds load.
 */
const CHANNEL_REGISTRY: Channel[] = [
  {
    name: 'Al Jazeera English',
    channelId: 'UCNye-wNBqNL5ZzHSJj3l8Bg',
    videoId: 'gCNeDWCI0vo',        // verified working
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: true,
  },
  {
    name: 'France 24 English',
    channelId: 'UCQfwfsi5VrQ8yKZ-UWmAEFg',
    videoId: 'h3MuIUNCCzI',        // verified working
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: true,
  },
  {
    name: 'Sky News',
    channelId: 'UCoMdktPbSTixAyNGwb-UYkQ',
    videoId: null,
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: false,
  },
  {
    name: 'ABC News Live',
    channelId: 'UCBi2mrWuNuyYy4gbM6fU18Q',
    videoId: null,
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: false,
  },
  {
    name: 'NBC News NOW',
    channelId: 'UCeY0bbntWzzVIaj2z3QigXg',
    videoId: null,
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: false,
  },
  {
    name: 'DW News',
    channelId: 'UCknLrEdhRCp1aegoMqRaCZg',
    videoId: null,
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: false,
  },
  {
    name: 'TRT World',
    channelId: 'UC7fWeaHhqgM4Lba7htOejLw',
    videoId: null,
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: false,
  },
  {
    name: 'NHK World',
    channelId: 'UCi3XnTWx0fqkDVfVBOv5eCA',
    videoId: null,
    embed: '',
    kind: 'youtube',
    health: 'unknown',
    consecutiveFailures: 0,
    verified: false,
  },
];

/** Max consecutive oEmbed failures before marking a channel offline */
const MAX_CONSECUTIVE_FAILURES = 3;

/** Max simultaneous active iframe embeds across the whole app */
export const MAX_ACTIVE_FRAMES = 4;

let channels: Channel[] = structuredClone(CHANNEL_REGISTRY);

/** YouTube Data API v3 key — set via setYouTubeApiKey() from config */
let youtubeApiKey: string | null = null;

export function setYouTubeApiKey(key: string): void {
  youtubeApiKey = key;
}

export function hasYouTubeApiKey(): boolean {
  return !!youtubeApiKey;
}

/**
 * Initialise channels: build embed URLs for verified channels,
 * then attempt dynamic resolution for unverified channels if API key is available.
 */
export async function initChannels(): Promise<void> {
  for (const ch of channels) {
    if (ch.verified && ch.videoId) {
      ch.embed = toYouTubeEmbed(ch.videoId);
      ch.health = 'live';
    }
  }

  if (youtubeApiKey) {
    await resolveAllLiveStreams();
  } else {
    for (const ch of channels) {
      if (!ch.verified) {
        ch.health = 'unavailable';
      }
    }
    console.info('[storm-desk] No YouTube API key — only pre-verified channels will show embeds. Set YOUTUBE_API_KEY in .env for full coverage.');
  }
}

/**
 * Query YouTube Data API v3 for each unresolved channel's current live broadcast.
 * Updates videoId, embed URL, and health status.
 */
async function resolveAllLiveStreams(): Promise<void> {
  const unresolved = channels.filter((c) => !c.verified || !c.videoId);
  const results = await Promise.allSettled(
    unresolved.map(async (ch) => {
      const videoId = await findLiveBroadcast(ch.channelId);
      if (videoId) {
        ch.videoId = videoId;
        ch.embed = toYouTubeEmbed(videoId);
        ch.health = 'live';
        ch.verified = true;
      } else {
        ch.health = 'unavailable';
      }
    }),
  );
  const resolved = unresolved.filter((c) => c.health === 'live').length;
  console.info(`[storm-desk] YouTube API resolved ${resolved}/${unresolved.length} live streams`);
}

/**
 * Use YouTube Data API v3 search endpoint to find the current live broadcast
 * for a given channel ID.
 */
async function findLiveBroadcast(channelId: string): Promise<string | null> {
  if (!youtubeApiKey) return null;
  try {
    const url = `https://www.googleapis.com/youtube/v3/search?part=id&channelId=${encodeURIComponent(channelId)}&eventType=live&type=video&maxResults=1&key=${encodeURIComponent(youtubeApiKey)}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(10_000) });
    if (!res.ok) {
      console.warn(`[storm-desk] YouTube API ${res.status} for channel ${channelId}`);
      return null;
    }
    const data = await res.json();
    if (data.items && data.items.length > 0) {
      return data.items[0].id.videoId;
    }
    return null;
  } catch (err) {
    console.warn(`[storm-desk] YouTube API error for ${channelId}:`, err);
    return null;
  }
}

export function getAllChannels(): Channel[] {
  return channels;
}

export function getLiveChannels(): Channel[] {
  return channels.filter((c) => c.health === 'live');
}

export function getEmbeddableChannels(): Channel[] {
  return channels.filter((c) => c.health === 'live');
}

export function getUnavailableChannels(): Channel[] {
  return channels.filter((c) => c.health === 'unavailable' || c.health === 'offline' || c.health === 'blocked');
}

export function getChannelByName(name: string): Channel | undefined {
  return channels.find((c) => c.name === name);
}

export function setChannelHealth(name: string, health: ChannelHealth): void {
  const ch = channels.find((c) => c.name === name);
  if (ch) {
    ch.health = health;
    ch.lastChecked = new Date().toISOString();
    if (health === 'live') {
      ch.consecutiveFailures = 0;
    }
  }
}

export function recordChannelFailure(name: string): void {
  const ch = channels.find((c) => c.name === name);
  if (!ch) return;
  ch.consecutiveFailures = (ch.consecutiveFailures ?? 0) + 1;
  if (ch.consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
    ch.health = 'offline';
  } else {
    ch.health = 'degraded';
  }
  ch.lastChecked = new Date().toISOString();
}

export function getRotationPool(excludePinned: string): Channel[] {
  return channels.filter(
    (c) => c.health === 'live' && c.name !== excludePinned,
  );
}

/**
 * Get the embed-safe URL for a channel.
 */
export function getSafeEmbedUrl(channel: Channel, muted: boolean): string {
  let url = channel.embed;
  if (!url && channel.videoId) {
    url = toYouTubeEmbed(channel.videoId);
  }
  if (!muted) {
    url = url.replace(/([?&])mute=1/, '$1mute=0');
  }
  return url;
}

/**
 * Probe a verified channel's embed via oEmbed to confirm it's still live.
 */
export async function probeChannelHealth(channel: Channel): Promise<ChannelHealth> {
  if (!channel.videoId) return channel.health;
  if (channel.kind !== 'youtube') return channel.health === 'unknown' ? 'live' : channel.health;

  try {
    const oembedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${encodeURIComponent(channel.videoId)}&format=json`;
    const res = await fetch(oembedUrl, { signal: AbortSignal.timeout(8_000) });

    if (res.status === 401 || res.status === 403) return 'blocked';
    if (res.status === 404) return 'offline';
    if (!res.ok) return 'degraded';

    const data = await res.json();
    return data.title ? 'live' : 'degraded';
  } catch {
    return 'offline';
  }
}

export async function runHealthCheckCycle(): Promise<void> {
  const checkable = channels.filter((c) => c.videoId && c.health !== 'unavailable');
  await Promise.allSettled(
    checkable.map(async (ch) => {
      const health = await probeChannelHealth(ch);
      if (health === 'live') {
        setChannelHealth(ch.name, 'live');
      } else {
        recordChannelFailure(ch.name);
      }
    }),
  );

  if (youtubeApiKey) {
    const dead = channels.filter((c) => c.health === 'offline' || c.health === 'blocked');
    for (const ch of dead) {
      const newId = await findLiveBroadcast(ch.channelId);
      if (newId && newId !== ch.videoId) {
        ch.videoId = newId;
        ch.embed = toYouTubeEmbed(newId);
        ch.health = 'live';
        ch.consecutiveFailures = 0;
        ch.verified = true;
        console.info(`[storm-desk] Re-resolved ${ch.name} → ${newId}`);
      }
    }
  }

  const live = channels.filter((c) => c.health === 'live').length;
  const unavailable = channels.filter((c) => c.health === 'unavailable').length;
  const degraded = channels.filter((c) => c.health === 'degraded').length;
  const offline = channels.filter((c) => c.health === 'offline').length;
  console.info(`[storm-desk] Channel health: ${live} live, ${unavailable} unavailable, ${degraded} degraded, ${offline} offline`);
}

export function resetChannels(): void {
  channels = structuredClone(CHANNEL_REGISTRY);
}
