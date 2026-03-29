import {
  createCipheriv,
  createDecipheriv,
  createHash,
  createHmac,
  pbkdf2Sync,
  randomBytes,
  timingSafeEqual,
  randomUUID
} from 'crypto';
import type {
  WaterfallEncryptedProfileBundle,
  WaterfallProfileBundle
} from '../src/types/sovereign';

const PROFILE_BUNDLE_FORMAT = 'waterfall.bundle.v1' as const;
const PROFILE_BUNDLE_KDF_ITERATIONS = 600000;
const PROFILE_BUNDLE_SALT_BYTES = 16;
const PROFILE_BUNDLE_NONCE_BYTES = 12;
const PROFILE_BUNDLE_KEY_BYTES = 64;
const PROFILE_BUNDLE_MIN_PASSPHRASE_LENGTH = 8;

function assertPassphrase(passphrase: string) {
  if (typeof passphrase !== 'string' || passphrase.length < PROFILE_BUNDLE_MIN_PASSPHRASE_LENGTH) {
    throw new Error(
      `WaterFall backups require a passphrase with at least ${PROFILE_BUNDLE_MIN_PASSPHRASE_LENGTH} characters.`
    );
  }
}

function deriveBundleKeys(passphrase: string, salt: Buffer) {
  const derivedKeyMaterial = pbkdf2Sync(
    passphrase,
    salt,
    PROFILE_BUNDLE_KDF_ITERATIONS,
    PROFILE_BUNDLE_KEY_BYTES,
    'sha512'
  );

  return {
    encryptionKey: derivedKeyMaterial.subarray(0, 32),
    signatureKey: derivedKeyMaterial.subarray(32, 64)
  };
}

function computeEnvelopeSignature(
  signatureKey: Buffer,
  salt: Buffer,
  nonce: Buffer,
  ciphertext: Buffer,
  tag: Buffer
) {
  return createHmac('sha256', signatureKey)
    .update(salt)
    .update(nonce)
    .update(ciphertext)
    .update(tag)
    .digest();
}

function isEncryptedBundle(value: unknown): value is WaterfallEncryptedProfileBundle {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const candidate = value as Partial<WaterfallEncryptedProfileBundle>;
  return candidate.format === PROFILE_BUNDLE_FORMAT && candidate.version === 'v1';
}

function isLegacyProfileBundle(value: unknown): value is WaterfallProfileBundle {
  if (!value || typeof value !== 'object') {
    return false;
  }

  const candidate = value as Partial<WaterfallProfileBundle>;
  return (
    typeof candidate.version === 'number' &&
    typeof candidate.exportedAt === 'number' &&
    typeof candidate.settings === 'object' &&
    typeof candidate.session === 'object'
  );
}

export function createEncryptedPayloadEnvelope<T>(
  payload: T,
  passphrase: string,
  options?: {
    authMode?: WaterfallEncryptedProfileBundle['authMode'];
    signatureScope?: WaterfallEncryptedProfileBundle['signature']['scope'];
  }
): WaterfallEncryptedProfileBundle {
  assertPassphrase(passphrase);

  const serializedPayload = JSON.stringify(payload);
  const payloadSha256 = createHash('sha256').update(serializedPayload).digest('base64');
  const salt = randomBytes(PROFILE_BUNDLE_SALT_BYTES);
  const nonce = randomBytes(PROFILE_BUNDLE_NONCE_BYTES);
  const { encryptionKey, signatureKey } = deriveBundleKeys(passphrase, salt);

  const cipher = createCipheriv('aes-256-gcm', encryptionKey, nonce);
  const ciphertext = Buffer.concat([
    cipher.update(serializedPayload, 'utf8'),
    cipher.final()
  ]);
  const tag = cipher.getAuthTag();
  const signature = computeEnvelopeSignature(signatureKey, salt, nonce, ciphertext, tag);

  return {
    format: PROFILE_BUNDLE_FORMAT,
    version: 'v1',
    createdAt: new Date().toISOString(),
    exportId: randomUUID(),
    authMode: options?.authMode || 'passphrase-v1',
    cipher: 'aes-256-gcm',
    kdf: {
      algorithm: 'pbkdf2-sha512',
      iterations: PROFILE_BUNDLE_KDF_ITERATIONS,
      salt: salt.toString('base64')
    },
    nonce: nonce.toString('base64'),
    tag: tag.toString('base64'),
    payloadSha256,
    signature: {
      algorithm: 'hmac-sha256',
      value: signature.toString('base64'),
      scope: options?.signatureScope || 'export-passphrase'
    },
    ciphertext: ciphertext.toString('base64')
  };
}

function decryptEncryptedPayloadEnvelope<T>(parsed: unknown, passphrase: string): T {
  if (!isEncryptedBundle(parsed)) {
    throw new Error('WaterFall could not recognize that backup format.');
  }
  assertPassphrase(passphrase);

  const salt = Buffer.from(parsed.kdf.salt, 'base64');
  const nonce = Buffer.from(parsed.nonce, 'base64');
  const tag = Buffer.from(parsed.tag, 'base64');
  const ciphertext = Buffer.from(parsed.ciphertext, 'base64');
  const providedSignature = Buffer.from(parsed.signature.value, 'base64');
  const { encryptionKey, signatureKey } = deriveBundleKeys(passphrase, salt);
  const computedSignature = computeEnvelopeSignature(signatureKey, salt, nonce, ciphertext, tag);

  if (
    providedSignature.length !== computedSignature.length ||
    !timingSafeEqual(providedSignature, computedSignature)
  ) {
    throw new Error('WaterFall rejected that backup because the signature did not verify.');
  }

  const decipher = createDecipheriv('aes-256-gcm', encryptionKey, nonce);
  decipher.setAuthTag(tag);
  const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString('utf8');
  const payloadSha256 = createHash('sha256').update(plaintext).digest('base64');

  if (payloadSha256 !== parsed.payloadSha256) {
    throw new Error('WaterFall rejected that backup because the payload digest did not match.');
  }

  return JSON.parse(plaintext) as T;
}

export function createEncryptedProfileBundle(
  profile: WaterfallProfileBundle,
  passphrase: string
): WaterfallEncryptedProfileBundle {
  return createEncryptedPayloadEnvelope(profile, passphrase, {
    authMode: 'passphrase-v1',
    signatureScope: 'export-passphrase'
  });
}

export function parseEncryptedPayloadEnvelope<T>(rawContent: string, passphrase: string) {
  const parsed = JSON.parse(rawContent) as unknown;
  return {
    payload: decryptEncryptedPayloadEnvelope<T>(parsed, passphrase),
    format: PROFILE_BUNDLE_FORMAT
  };
}

export function parseProfileBundleContent(rawContent: string, passphrase: string) {
  const parsed = JSON.parse(rawContent) as unknown;

  if (isLegacyProfileBundle(parsed)) {
    return {
      profile: parsed,
      format: 'legacy-json' as const
    };
  }

  const profile = decryptEncryptedPayloadEnvelope<unknown>(parsed, passphrase);
  if (!isLegacyProfileBundle(profile)) {
    throw new Error('WaterFall decrypted the backup, but the embedded profile payload was invalid.');
  }

  return {
    profile,
    format: PROFILE_BUNDLE_FORMAT
  };
}
