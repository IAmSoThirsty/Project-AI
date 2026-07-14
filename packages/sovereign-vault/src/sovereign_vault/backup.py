"""
sovereign_vault.backup

A backup that can be restored without anti-rollback state, audit
continuity, revocation history, and key-epoch information becomes a
bypass path — restoring it is indistinguishable from a rollback attack.
So a BackupBundle is required to carry all of those components, and
import_bundle() runs the SAME state.verify_advance() rollback check used
for any other untrusted state input. There is no separate, weaker path
for "it's just a backup."
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .errors import BackupIntegrityError
from .interfaces import AuditChainProvider
from .state import AntiRollbackState, Checkpoint


@dataclass(frozen=True)
class BackupBundle:
    vault_id: str
    epoch: int
    checkpoint: Checkpoint
    sealed_objects_blob: bytes  # opaque — however the store serializes SealedObjectRef entries
    metadata_index_nonce: bytes
    metadata_index_ciphertext: bytes
    revocation_list_hash: str
    audit_chain_tail_hash: str
    manifest_signature: bytes
    manifest_signer_public_key: bytes


REQUIRED_COMPONENTS = (
    "checkpoint",
    "sealed_objects_blob",
    "metadata_index_nonce",
    "metadata_index_ciphertext",
    "revocation_list_hash",
    "audit_chain_tail_hash",
)


def export_bundle(bundle: BackupBundle) -> bytes:
    for field_name in REQUIRED_COMPONENTS:
        if getattr(bundle, field_name) in (None, b"", ""):
            raise BackupIntegrityError(
                f"export refused: component '{field_name}' missing — a backup without "
                f"this component is a bypass path, not a backup"
            )
    payload = {
        "vault_id": bundle.vault_id,
        "epoch": bundle.epoch,
        "checkpoint": bundle.checkpoint.body(),
        "checkpoint_signature": bundle.checkpoint.signature.hex(),
        "checkpoint_signer": bundle.checkpoint.signer_public_key.hex(),
        "sealed_objects_blob": bundle.sealed_objects_blob.hex(),
        "metadata_index_nonce": bundle.metadata_index_nonce.hex(),
        "metadata_index_ciphertext": bundle.metadata_index_ciphertext.hex(),
        "revocation_list_hash": bundle.revocation_list_hash,
        "audit_chain_tail_hash": bundle.audit_chain_tail_hash,
        "manifest_signature": bundle.manifest_signature.hex(),
        "manifest_signer_public_key": bundle.manifest_signer_public_key.hex(),
    }
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def import_bundle(
    raw: bytes,
    rollback_state: AntiRollbackState,
    audit: AuditChainProvider,
    current_vault_id: str,
    current_epoch: int,
) -> BackupBundle:
    """
    Raises BackupIntegrityError (a SafeHaltError subclass) on:
      - missing required component
      - vault_id mismatch (refuses cross-vault restore-as-bypass)
      - epoch behind current epoch (refuses restoring a pre-recovery identity)
      - checkpoint that fails rollback_state.verify_advance() (same check
        used for any untrusted state input — a backup gets no exception)
      - audit unavailable to record the restore itself
    """
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise BackupIntegrityError(f"backup payload not parseable: {e}") from e

    for field_name in REQUIRED_COMPONENTS:
        json_key = field_name if field_name != "checkpoint" else "checkpoint"
        if json_key not in payload or payload[json_key] in (None, "", []):
            raise BackupIntegrityError(f"backup missing required component '{field_name}'")

    if payload["vault_id"] != current_vault_id:
        raise BackupIntegrityError(
            f"backup vault_id {payload['vault_id']!r} does not match current vault "
            f"{current_vault_id!r} — refusing cross-vault restore"
        )

    if payload["epoch"] < current_epoch:
        raise BackupIntegrityError(
            f"backup epoch {payload['epoch']} < current epoch {current_epoch} — "
            f"this backup predates a recovery event; restoring it would resurrect "
            f"an invalidated identity"
        )

    body = payload["checkpoint"]
    checkpoint = Checkpoint(
        sequence=body["sequence"],
        prev_hash=body["prev_hash"],
        state_summary=body["state_summary"],
        timestamp_ns=body["timestamp_ns"],
        signature=bytes.fromhex(payload["checkpoint_signature"]),
        signer_public_key=bytes.fromhex(payload["checkpoint_signer"]),
    )

    # Same rollback check as any other untrusted state input.
    rollback_state.verify_advance(checkpoint)

    if not audit.has_capacity():
        raise BackupIntegrityError("audit chain unavailable — refusing an unaudited restore")

    audit.append(
        "BACKUP_RESTORED",
        {
            "vault_id": payload["vault_id"],
            "epoch": payload["epoch"],
            "checkpoint_sequence": checkpoint.sequence,
        },
    )

    return BackupBundle(
        vault_id=payload["vault_id"],
        epoch=payload["epoch"],
        checkpoint=checkpoint,
        sealed_objects_blob=bytes.fromhex(payload["sealed_objects_blob"]),
        metadata_index_nonce=bytes.fromhex(payload["metadata_index_nonce"]),
        metadata_index_ciphertext=bytes.fromhex(payload["metadata_index_ciphertext"]),
        revocation_list_hash=payload["revocation_list_hash"],
        audit_chain_tail_hash=payload["audit_chain_tail_hash"],
        manifest_signature=bytes.fromhex(payload["manifest_signature"]),
        manifest_signer_public_key=bytes.fromhex(payload["manifest_signer_public_key"]),
    )
