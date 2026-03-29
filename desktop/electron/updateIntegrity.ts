import { createHash, createHmac, timingSafeEqual } from 'crypto';
import { existsSync, promises as fs } from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import type { WaterfallUpdateManifest } from '../src/types/sovereign';

const WATERFALL_UPDATE_SIGNATURE_VERSION = 'waterfall-update-v1';
const WATERFALL_UPDATE_METADATA_PREFIX = 'wfmeta:';
const WATERFALL_UPDATE_STAGE_DIRECTORY = 'waterfall-updates';
const WATERFALL_UPDATE_STAGE_STATE_FILENAME = 'staged-update.json';

type ParsedUpdateManifestMetadata = {
  artifactSha256: string;
  artifactName: string;
  releasedAt: string;
  visibleNotes: string[];
};

type WaterfallStagedUpdateState = {
  version: string;
  channel: string;
  sourceUrl: string;
  artifactName: string;
  artifactSha256: string;
  artifactPath: string;
  stagedAt: string;
  rollbackVersion: string;
};

type VerifyWaterfallUpdateManifestOptions = {
  currentVersion: string;
  signingKey?: string;
  userDataPath: string;
};

type StageWaterfallUpdateOptions = {
  currentVersion: string;
  userDataPath: string;
};

function parseUpdateManifestMetadata(notes: string[]) {
  const metadata: ParsedUpdateManifestMetadata = {
    artifactSha256: '',
    artifactName: '',
    releasedAt: '',
    visibleNotes: []
  };

  notes.forEach((note) => {
    if (!note.startsWith(WATERFALL_UPDATE_METADATA_PREFIX)) {
      metadata.visibleNotes.push(note);
      return;
    }

    const rawEntry = note.slice(WATERFALL_UPDATE_METADATA_PREFIX.length);
    const separatorIndex = rawEntry.indexOf('=');
    if (separatorIndex <= 0) {
      return;
    }

    const key = rawEntry.slice(0, separatorIndex).trim().toLowerCase();
    const value = rawEntry.slice(separatorIndex + 1).trim();

    if (key === 'artifact_sha256') {
      metadata.artifactSha256 = value.toLowerCase();
      return;
    }

    if (key === 'artifact_name') {
      metadata.artifactName = value;
      return;
    }

    if (key === 'released_at') {
      metadata.releasedAt = value;
    }
  });

  return metadata;
}

function buildUpdateManifestSignaturePayload(
  manifest: Pick<WaterfallUpdateManifest, 'version' | 'url' | 'channel' | 'available'>,
  metadata: ParsedUpdateManifestMetadata
) {
  return [
    WATERFALL_UPDATE_SIGNATURE_VERSION,
    `version=${manifest.version}`,
    `url=${manifest.url}`,
    `channel=${manifest.channel}`,
    `available=${manifest.available ? 1 : 0}`,
    `artifact_sha256=${metadata.artifactSha256}`,
    `artifact_name=${metadata.artifactName}`,
    `released_at=${metadata.releasedAt}`,
    `notes=${JSON.stringify(metadata.visibleNotes)}`
  ].join('\n');
}

function compareVersionStrings(leftVersion: string, rightVersion: string) {
  const left = leftVersion.split(/[.-]/).map((segment) => Number.parseInt(segment, 10));
  const right = rightVersion.split(/[.-]/).map((segment) => Number.parseInt(segment, 10));
  const longest = Math.max(left.length, right.length);

  for (let index = 0; index < longest; index += 1) {
    const leftValue = Number.isFinite(left[index]) ? left[index] : 0;
    const rightValue = Number.isFinite(right[index]) ? right[index] : 0;

    if (leftValue > rightValue) {
      return 1;
    }

    if (leftValue < rightValue) {
      return -1;
    }
  }

  return 0;
}

function getUpdateStagePaths(userDataPath: string) {
  const baseDirectory = path.join(userDataPath, WATERFALL_UPDATE_STAGE_DIRECTORY);
  return {
    baseDirectory,
    artifactsDirectory: path.join(baseDirectory, 'artifacts'),
    statePath: path.join(baseDirectory, WATERFALL_UPDATE_STAGE_STATE_FILENAME)
  };
}

async function readStagedUpdateState(userDataPath: string) {
  const { statePath } = getUpdateStagePaths(userDataPath);
  if (!existsSync(statePath)) {
    return null;
  }

  try {
    const content = await fs.readFile(statePath, 'utf8');
    const parsed = JSON.parse(content) as Partial<WaterfallStagedUpdateState>;
    if (
      typeof parsed.version !== 'string' ||
      typeof parsed.channel !== 'string' ||
      typeof parsed.sourceUrl !== 'string' ||
      typeof parsed.artifactName !== 'string' ||
      typeof parsed.artifactSha256 !== 'string' ||
      typeof parsed.artifactPath !== 'string' ||
      typeof parsed.stagedAt !== 'string' ||
      typeof parsed.rollbackVersion !== 'string'
    ) {
      return null;
    }

    return parsed as WaterfallStagedUpdateState;
  } catch {
    return null;
  }
}

function computeManifestVerification(
  manifest: WaterfallUpdateManifest,
  signingKey: string | undefined,
  metadata: ParsedUpdateManifestMetadata
) {
  if (!manifest.signature) {
    return {
      integrityState: manifest.available ? ('unverified' as const) : ('unknown' as const),
      statusMessage: manifest.available
        ? 'WaterFall refused to trust an available update because the manifest is unsigned.'
        : 'No signed update manifest is currently available.'
    };
  }

  if (!signingKey) {
    return {
      integrityState: 'unknown' as const,
      statusMessage:
        'This WaterFall build does not have an update signing key configured, so manifest verification is unavailable.'
    };
  }

  const expectedSignature = createHmac(
    'sha256',
    Buffer.from(signingKey, 'utf8')
  )
    .update(buildUpdateManifestSignaturePayload(manifest, metadata), 'utf8')
    .digest('hex');
  const providedSignature = manifest.signature.trim().toLowerCase();
  const expectedBuffer = Buffer.from(expectedSignature, 'utf8');
  const providedBuffer = Buffer.from(providedSignature, 'utf8');

  if (
    expectedBuffer.length !== providedBuffer.length ||
    !timingSafeEqual(expectedBuffer, providedBuffer)
  ) {
    return {
      integrityState: 'unverified' as const,
      statusMessage: 'WaterFall rejected the update manifest because its signature did not verify.'
    };
  }

  if (!metadata.artifactSha256 || !manifest.url) {
    return {
      integrityState: 'unverified' as const,
      statusMessage:
        'WaterFall rejected the update manifest because it was missing an artifact hash or source URL.'
    };
  }

  return {
    integrityState: 'verified' as const,
    statusMessage: 'WaterFall verified the update manifest signature and artifact fingerprint.'
  };
}

function inferArtifactName(source: string, preferredName: string) {
  if (preferredName) {
    return preferredName;
  }

  try {
    const parsed = new URL(source);
    return path.basename(parsed.pathname) || 'waterfall-update.bin';
  } catch {
    return path.basename(source) || 'waterfall-update.bin';
  }
}

async function downloadUpdateArtifact(source: string) {
  if (source.startsWith('file://')) {
    return fs.readFile(fileURLToPath(source));
  }

  if (existsSync(source)) {
    return fs.readFile(source);
  }

  const response = await fetch(source, {
    headers: {
      'user-agent': 'WaterFall-Updater/1.0'
    }
  });

  if (!response.ok) {
    throw new Error(`WaterFall could not download the update artifact (${response.status}).`);
  }

  const payload = await response.arrayBuffer();
  return Buffer.from(payload);
}

export async function verifyWaterfallUpdateManifest(
  manifest: WaterfallUpdateManifest,
  options: VerifyWaterfallUpdateManifestOptions
): Promise<WaterfallUpdateManifest> {
  const metadata = parseUpdateManifestMetadata(manifest.notes || []);
  const stagedState = await readStagedUpdateState(options.userDataPath);
  const verification = computeManifestVerification(manifest, options.signingKey, metadata);
  const versionComparison = compareVersionStrings(manifest.version, options.currentVersion);
  const updateAvailable = Boolean(manifest.available) && versionComparison > 0;
  const stageStatus =
    stagedState && stagedState.version === manifest.version && existsSync(stagedState.artifactPath)
      ? 'staged'
      : 'idle';
  const statusMessage = updateAvailable
    ? verification.statusMessage
    : versionComparison <= 0
      ? 'WaterFall is already on this version or newer.'
      : verification.statusMessage;

  return {
    ...manifest,
    available: updateAvailable,
    notes: metadata.visibleNotes,
    integrityState: verification.integrityState,
    artifactSha256: metadata.artifactSha256 || undefined,
    artifactName: inferArtifactName(manifest.url, metadata.artifactName) || undefined,
    publishedAt: metadata.releasedAt || undefined,
    manifestVerifiedAt: verification.integrityState === 'verified' ? Date.now() : undefined,
    stageStatus,
    stagedArtifactPath: stageStatus === 'staged' ? stagedState?.artifactPath : undefined,
    rollbackReady: stageStatus === 'staged',
    statusMessage
  };
}

export async function stageWaterfallUpdate(
  manifest: WaterfallUpdateManifest,
  options: StageWaterfallUpdateOptions
): Promise<WaterfallUpdateManifest> {
  if (!manifest.available) {
    throw new Error('WaterFall did not receive an available update to stage.');
  }

  if (manifest.integrityState !== 'verified') {
    throw new Error('WaterFall will not stage an update whose manifest did not verify.');
  }

  if (!manifest.url || !manifest.artifactSha256) {
    throw new Error('WaterFall requires a verified update URL and artifact fingerprint.');
  }

  const artifactName = inferArtifactName(manifest.url, manifest.artifactName || '');
  const stagePaths = getUpdateStagePaths(options.userDataPath);
  const stagedState = await readStagedUpdateState(options.userDataPath);

  if (
    stagedState &&
    stagedState.version === manifest.version &&
    stagedState.artifactSha256 === manifest.artifactSha256 &&
    existsSync(stagedState.artifactPath)
  ) {
    return {
      ...manifest,
      stageStatus: 'staged',
      stagedArtifactPath: stagedState.artifactPath,
      rollbackReady: true,
      statusMessage: `WaterFall already staged update ${manifest.version}.`
    };
  }

  await fs.mkdir(stagePaths.artifactsDirectory, { recursive: true });
  const artifactBuffer = await downloadUpdateArtifact(manifest.url);
  const observedSha256 = createHash('sha256').update(artifactBuffer).digest('hex');

  if (observedSha256 !== manifest.artifactSha256.toLowerCase()) {
    throw new Error('WaterFall rejected the downloaded artifact because its SHA-256 did not match.');
  }

  const artifactPath = path.join(stagePaths.artifactsDirectory, artifactName);
  await fs.writeFile(artifactPath, artifactBuffer);

  const stagedUpdateState: WaterfallStagedUpdateState = {
    version: manifest.version,
    channel: manifest.channel,
    sourceUrl: manifest.url,
    artifactName,
    artifactSha256: observedSha256,
    artifactPath,
    stagedAt: new Date().toISOString(),
    rollbackVersion: options.currentVersion
  };

  await fs.writeFile(stagePaths.statePath, JSON.stringify(stagedUpdateState, null, 2), 'utf8');

  return {
    ...manifest,
    artifactName,
    artifactSha256: observedSha256,
    stageStatus: 'staged',
    stagedArtifactPath: artifactPath,
    rollbackReady: true,
    statusMessage: `WaterFall staged update ${manifest.version} and captured rollback metadata for ${options.currentVersion}.`
  };
}
