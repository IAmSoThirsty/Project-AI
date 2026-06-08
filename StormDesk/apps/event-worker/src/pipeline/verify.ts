/* ── Storm Desk — Incident Verification ─────────────────────────── */

import type { Incident } from './score';
import { cfg } from '../config';

export type VerificationResult = {
  canEscalate: boolean;
  reasons: string[];
};

/**
 * Evaluate whether an incident should trigger automatic escalation.
 * Returns both a boolean and human-readable reasons explaining the decision.
 */
export function evaluateEscalation(incident: Incident): VerificationResult {
  const reasons: string[] = [];
  let canEscalate = true;

  // Score threshold
  if (incident.score < cfg.escalation.minScore) {
    canEscalate = false;
    reasons.push(
      `Score ${incident.score} is below threshold ${cfg.escalation.minScore}`,
    );
  } else {
    reasons.push(`Score ${incident.score} meets threshold ${cfg.escalation.minScore}`);
  }

  // Source count threshold
  if (incident.verification.independent_sources < cfg.escalation.minSources) {
    canEscalate = false;
    reasons.push(
      `Only ${incident.verification.independent_sources} independent source(s), need ${cfg.escalation.minSources}`,
    );
  } else {
    reasons.push(
      `${incident.verification.independent_sources} independent sources meets minimum ${cfg.escalation.minSources}`,
    );
  }

  // Wire confirmation requirement
  if (cfg.escalation.requireWire && !incident.verification.wire_confirmed) {
    canEscalate = false;
    reasons.push('Wire confirmation required but not yet confirmed');
  } else if (incident.verification.wire_confirmed) {
    reasons.push('Wire service confirmed');
  }

  // Broadcaster confirmation (informational, not blocking)
  if (incident.verification.broadcaster_confirmed) {
    reasons.push('Broadcaster confirmed');
  }

  // Keyword analysis
  if (incident.keywords.length > 0) {
    reasons.push(`Keywords detected: ${incident.keywords.join(', ')}`);
  }

  return { canEscalate, reasons };
}

/**
 * Build a human-readable explanation string for the escalation trigger.
 */
export function buildEscalationExplanation(incident: Incident): string {
  const { reasons } = evaluateEscalation(incident);
  const parts: string[] = [];

  parts.push(
    `Triggered because ${incident.verification.independent_sources} sources mentioned`,
  );

  if (incident.keywords.length > 0) {
    parts.push(incident.keywords.join(' + '));
  } else {
    parts.push('this event');
  }

  const timestamps = incident.sources
    .map((s) => new Date(s.published_at).getTime())
    .sort();

  if (timestamps.length >= 2) {
    const windowMinutes = Math.round(
      (timestamps[timestamps.length - 1] - timestamps[0]) / 60_000,
    );
    parts.push(`within ${windowMinutes} minutes`);
  }

  return parts.join(' ') + '. ' + reasons.filter((r) => !r.startsWith('Score')).join('; ') + '.';
}
