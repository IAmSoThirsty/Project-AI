/* ── Storm Desk — MediaStack Source Adapter ──────────────────────── */

import { cfg } from '../config';
import type { RawArticle } from './newsdata';

const MEDIASTACK_BASE = 'http://api.mediastack.com/v1/news';

export async function fetchMediaStack(): Promise<RawArticle[]> {
  if (!cfg.mediastack.enabled) return [];

  const params = new URLSearchParams({
    access_key: cfg.mediastack.apiKey,
    languages: 'en',
    categories: 'general,science,technology,health',
    sort: 'published_desc',
    limit: '50',
  });

  try {
    const res = await fetch(`${MEDIASTACK_BASE}?${params.toString()}`, {
      signal: AbortSignal.timeout(15_000),
      headers: { 'Accept': 'application/json' },
    });

    if (!res.ok) {
      console.warn(`[mediastack] HTTP ${res.status}: ${res.statusText}`);
      return [];
    }

    const body = await res.json();
    if (body.error) {
      console.warn('[mediastack] API error:', body.error);
      return [];
    }

    const data: any[] = body.data ?? [];

    return data
      .filter((item: any) => item.title && item.url)
      .map((item: any): RawArticle => ({
        title: String(item.title).trim(),
        description: item.description ? String(item.description).trim() : undefined,
        source: item.source ?? 'MediaStack',
        url: String(item.url).trim(),
        publishedAt: item.published_at
          ? new Date(item.published_at).toISOString()
          : new Date().toISOString(),
        country: item.country ?? undefined,
        language: item.language ?? 'en',
      }));
  } catch (err) {
    console.error('[mediastack] Fetch error:', err);
    return [];
  }
}
