/* ── Storm Desk — RSS Source Adapter ─────────────────────────────── */

import { cfg } from '../config';
import type { RawArticle } from './newsdata';

/**
 * Lightweight RSS/Atom parser.  Avoids heavy XML dependencies by using
 * regex extraction on the raw XML text.  Handles both RSS 2.0 <item>
 * and Atom <entry> structures.
 */
export async function fetchRssFeeds(): Promise<RawArticle[]> {
  const results = await Promise.allSettled(
    cfg.rss.feeds.map((feedUrl) => fetchSingleFeed(feedUrl)),
  );

  return results.flatMap((r) => (r.status === 'fulfilled' ? r.value : []));
}

async function fetchSingleFeed(feedUrl: string): Promise<RawArticle[]> {
  try {
    const res = await fetch(feedUrl, {
      signal: AbortSignal.timeout(12_000),
      headers: {
        'Accept': 'application/rss+xml, application/xml, text/xml',
        'User-Agent': 'StormDesk/1.0',
      },
    });

    if (!res.ok) {
      console.warn(`[rss] HTTP ${res.status} for ${feedUrl}`);
      return [];
    }

    const xml = await res.text();
    const sourceName = extractFeedTitle(xml) || new URL(feedUrl).hostname;

    const items = extractItems(xml);
    return items
      .filter((item) => item.title && item.link)
      .map(
        (item): RawArticle => ({
          title: item.title.trim(),
          description: item.description?.trim(),
          source: sourceName,
          url: item.link.trim(),
          publishedAt: item.pubDate
            ? new Date(item.pubDate).toISOString()
            : new Date().toISOString(),
          language: 'en',
        }),
      );
  } catch (err) {
    console.error(`[rss] Fetch error for ${feedUrl}:`, err);
    return [];
  }
}

type FeedItem = {
  title: string;
  link: string;
  description?: string;
  pubDate?: string;
};

function extractFeedTitle(xml: string): string | null {
  const channelTitle = xml.match(/<channel[^>]*>[\s\S]*?<title[^>]*>([\s\S]*?)<\/title>/i);
  if (channelTitle) return decodeEntities(channelTitle[1]);
  const feedTitle = xml.match(/<feed[^>]*>[\s\S]*?<title[^>]*>([\s\S]*?)<\/title>/i);
  if (feedTitle) return decodeEntities(feedTitle[1]);
  return null;
}

function extractItems(xml: string): FeedItem[] {
  const items: FeedItem[] = [];

  // RSS 2.0 <item> blocks
  const rssItems = xml.matchAll(/<item[^>]*>([\s\S]*?)<\/item>/gi);
  for (const match of rssItems) {
    items.push(parseRssItem(match[1]));
  }

  // Atom <entry> blocks (if no RSS items found)
  if (items.length === 0) {
    const atomEntries = xml.matchAll(/<entry[^>]*>([\s\S]*?)<\/entry>/gi);
    for (const match of atomEntries) {
      items.push(parseAtomEntry(match[1]));
    }
  }

  return items;
}

function parseRssItem(block: string): FeedItem {
  return {
    title: extractTag(block, 'title') ?? '',
    link: extractTag(block, 'link') ?? '',
    description: extractTag(block, 'description') ?? undefined,
    pubDate: extractTag(block, 'pubDate') ?? extractTag(block, 'dc:date') ?? undefined,
  };
}

function parseAtomEntry(block: string): FeedItem {
  const linkMatch = block.match(/<link[^>]+href=["']([^"']+)["']/i);
  return {
    title: extractTag(block, 'title') ?? '',
    link: linkMatch ? linkMatch[1] : '',
    description: extractTag(block, 'summary') ?? extractTag(block, 'content') ?? undefined,
    pubDate: extractTag(block, 'published') ?? extractTag(block, 'updated') ?? undefined,
  };
}

function extractTag(block: string, tag: string): string | null {
  const cdataMatch = block.match(new RegExp(`<${tag}[^>]*><!\\[CDATA\\[([\\s\\S]*?)\\]\\]><\\/${tag}>`, 'i'));
  if (cdataMatch) return cdataMatch[1].trim();
  const plainMatch = block.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, 'i'));
  if (plainMatch) return decodeEntities(plainMatch[1].trim());
  return null;
}

function decodeEntities(str: string): string {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x27;/g, "'")
    .replace(/<[^>]+>/g, '');
}
