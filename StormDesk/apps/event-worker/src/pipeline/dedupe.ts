/* ── Storm Desk — Deduplication & Clustering ────────────────────── */

import type { NormalizedArticle } from './normalize';

export type ArticleCluster = {
  representative: NormalizedArticle;
  articles: NormalizedArticle[];
};

const JACCARD_THRESHOLD = 0.42;

export function clusterArticles(articles: NormalizedArticle[]): ArticleCluster[] {
  const clusters: ArticleCluster[] = [];

  for (const article of articles) {
    const tokens = tokenSet(article.titleNormalized);
    let placed = false;

    for (const cluster of clusters) {
      const repTokens = tokenSet(cluster.representative.titleNormalized);
      if (jaccard(tokens, repTokens) >= JACCARD_THRESHOLD) {
        cluster.articles.push(article);
        placed = true;
        break;
      }
    }

    if (!placed) {
      clusters.push({
        representative: article,
        articles: [article],
      });
    }
  }

  return clusters;
}

export function mergeNewArticlesIntoClusters(
  existing: ArticleCluster[],
  incoming: NormalizedArticle[],
): ArticleCluster[] {
  const merged = [...existing];

  for (const article of incoming) {
    const tokens = tokenSet(article.titleNormalized);
    let placed = false;

    for (const cluster of merged) {
      const repTokens = tokenSet(cluster.representative.titleNormalized);
      if (jaccard(tokens, repTokens) >= JACCARD_THRESHOLD) {
        const existingUrls = new Set(cluster.articles.map((a) => a.url));
        if (!existingUrls.has(article.url)) {
          cluster.articles.push(article);
        }
        placed = true;
        break;
      }
    }

    if (!placed) {
      merged.push({
        representative: article,
        articles: [article],
      });
    }
  }

  return merged;
}

function tokenSet(s: string): Set<string> {
  return new Set(s.split(' ').filter((w) => w.length > 2));
}

function jaccard(a: Set<string>, b: Set<string>): number {
  let intersection = 0;
  for (const item of a) {
    if (b.has(item)) intersection++;
  }
  const union = new Set([...a, ...b]).size;
  return union > 0 ? intersection / union : 0;
}
