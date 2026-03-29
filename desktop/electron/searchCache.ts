import { app } from 'electron';
import { createHash } from 'crypto';
import { promises as fs } from 'fs';
import * as path from 'path';
import type {
  WaterfallSearchProvider,
  WaterfallSearchResponse
} from '../src/types/sovereign';
import {
  createEncryptedPayloadEnvelope,
  parseEncryptedPayloadEnvelope
} from './profileBundles';

const SEARCH_CACHE_DIRECTORY = 'search-cache';
const SEARCH_CACHE_EXTENSION = '.waterfallcache';
const SEARCH_CACHE_MAX_AGE_MS = 1000 * 60 * 60 * 24 * 7;

interface WaterfallSearchCacheEntry {
  query: string;
  providers: string[];
  response: WaterfallSearchResponse;
  cachedAt: number;
}

export interface WaterfallCachedSearchResult {
  cacheKey: string;
  cachedAt: number;
  response: WaterfallSearchResponse;
}

const inMemorySearchCache = new Map<string, WaterfallSearchCacheEntry>();

function getSearchCacheDirectory() {
  return path.join(app.getPath('userData'), SEARCH_CACHE_DIRECTORY);
}

function normalizeProviders(providers: WaterfallSearchProvider[]) {
  return Array.from(
    new Set(
      providers
        .map((provider) => String(provider).trim())
        .filter(Boolean)
    )
  ).sort();
}

function withCacheWarning(response: WaterfallSearchResponse): WaterfallSearchResponse {
  return {
    ...response,
    warnings: response.warnings.includes('served-from-private-cache')
      ? response.warnings
      : [...response.warnings, 'served-from-private-cache']
  };
}

function isExpired(timestamp: number) {
  return Date.now() - timestamp > SEARCH_CACHE_MAX_AGE_MS;
}

function getCachePath(cacheKey: string) {
  return path.join(getSearchCacheDirectory(), `${cacheKey}${SEARCH_CACHE_EXTENSION}`);
}

export function obfuscateQuery(original: string) {
  return original.trim().replace(/\s+/g, ' ');
}

export function getSearchCacheKey(query: string, providers: WaterfallSearchProvider[]) {
  return createHash('sha256')
    .update(`${obfuscateQuery(query)}|${normalizeProviders(providers).join(',')}`)
    .digest('hex');
}

export async function cacheSearchResults(options: {
  query: string;
  providers: WaterfallSearchProvider[];
  response: WaterfallSearchResponse;
  secret: string;
}) {
  const normalizedQuery = obfuscateQuery(options.query);
  const normalizedProviders = normalizeProviders(options.providers);
  const cacheKey = getSearchCacheKey(normalizedQuery, normalizedProviders);
  const cachedAt = Date.now();
  const entry: WaterfallSearchCacheEntry = {
    query: normalizedQuery,
    providers: normalizedProviders,
    response: options.response,
    cachedAt
  };

  inMemorySearchCache.set(cacheKey, entry);

  await fs.mkdir(getSearchCacheDirectory(), {
    recursive: true
  });
  await fs.writeFile(
    getCachePath(cacheKey),
    JSON.stringify(
      createEncryptedPayloadEnvelope(entry, options.secret, {
        authMode: 'local-secret-v1',
        signatureScope: 'local-cache-secret'
      }),
      null,
      2
    ),
    'utf8'
  );

  return {
    cacheKey,
    cachedAt
  };
}

export async function getCachedSearchResults(options: {
  query: string;
  providers: WaterfallSearchProvider[];
  secret: string;
}): Promise<WaterfallCachedSearchResult | null> {
  const normalizedQuery = obfuscateQuery(options.query);
  if (!normalizedQuery) {
    return null;
  }

  const normalizedProviders = normalizeProviders(options.providers);
  const cacheKey = getSearchCacheKey(normalizedQuery, normalizedProviders);
  const memoryEntry = inMemorySearchCache.get(cacheKey);

  if (memoryEntry) {
    if (isExpired(memoryEntry.cachedAt)) {
      inMemorySearchCache.delete(cacheKey);
    } else {
      return {
        cacheKey,
        cachedAt: memoryEntry.cachedAt,
        response: withCacheWarning(memoryEntry.response)
      };
    }
  }

  try {
    const rawContent = await fs.readFile(getCachePath(cacheKey), 'utf8');
    const parsed = parseEncryptedPayloadEnvelope<WaterfallSearchCacheEntry>(
      rawContent,
      options.secret
    );
    const entry = parsed.payload;

    if (
      !entry ||
      typeof entry.cachedAt !== 'number' ||
      !Array.isArray(entry.providers) ||
      !entry.response
    ) {
      return null;
    }

    if (isExpired(entry.cachedAt)) {
      inMemorySearchCache.delete(cacheKey);
      await fs.rm(getCachePath(cacheKey), {
        force: true
      });
      return null;
    }

    inMemorySearchCache.set(cacheKey, entry);
    return {
      cacheKey,
      cachedAt: entry.cachedAt,
      response: withCacheWarning(entry.response)
    };
  } catch {
    return null;
  }
}

export async function clearSearchCache() {
  inMemorySearchCache.clear();
  await fs.rm(getSearchCacheDirectory(), {
    recursive: true,
    force: true
  });
}
