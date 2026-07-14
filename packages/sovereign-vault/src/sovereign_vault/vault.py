"""
sovereign_vault.vault

SovereignVault wires the modules together. It does not add new security
logic of its own beyond sequencing — every actual check still lives in
the module that owns it (deny.py owns uncertainty, state.py owns
rollback, tamper.py owns tamper response, recovery.py owns quorum, etc).
This file exists so a caller doesn't have to hand-assemble the pipeline
correctly every time, which is itself a blind spot: a correct component
wired incorrectly is still a broken vault.
"""

from __future__ import annotations

import contextlib
import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field

from .admission import AdmissionRecord, ProvenanceVerifier, admit_object
from .buffer import SecureBuffer
from .deny import RuntimeConditions
from .errors import SafeHaltError
from .interfaces import AttestationProvider, AuditChainProvider, AuthorityProvider, AuthorityToken
from .keys import KeyHierarchy, RootKekSession
from .metadata import Category, MetadataIndex
from .primitives import seal
from .recovery import RecoveryQuorumPolicy, RecoveryRequest, execute_recovery
from .regeneration import ComponentBlueprint, LoopGuard, RegenerationEngine, RegenerationRecord
from .release import ObjectReleaseManager, SealedObjectRef
from .state import AntiRollbackState
from .tamper import TamperEvent, TamperHandler, TamperPolicy, TamperResponse


@dataclass
class VaultObjectStore:
    """In-memory sealed-object store. Swap for real disk/object-storage
    persistence; the sealing/release discipline above does not change —
    only where the ciphertext bytes physically live."""

    objects: dict[str, SealedObjectRef] = field(
        default_factory=dict
    )  # object_id -> SealedObjectRef

    def put(self, ref: SealedObjectRef) -> None:
        if ref.object_id in self.objects:
            raise ValueError(f"object {ref.object_id} already stored — no silent overwrite")
        self.objects[ref.object_id] = ref

    def get(self, object_id: str) -> SealedObjectRef:
        if object_id not in self.objects:
            raise KeyError(f"object {object_id} not found")
        return self.objects[object_id]


@dataclass
class SovereignVault:
    vault_id: str
    authority: AuthorityProvider
    audit: AuditChainProvider
    attestation: AttestationProvider
    provenance: ProvenanceVerifier
    rollback_state: AntiRollbackState
    epoch: int = 0

    def __post_init__(self) -> None:
        self._hierarchy = KeyHierarchy(vault_id=self.vault_id, epoch=self.epoch)
        self._store = VaultObjectStore()
        self._metadata: MetadataIndex | None = None
        self._release_manager: ObjectReleaseManager | None = None
        self._tamper_handler: TamperHandler | None = None
        self._sealed = False

    # ---- lifecycle -------------------------------------------------

    def bootstrap(self, root_kek: bytes, initial_state_summary: dict[str, object]) -> None:
        if self.rollback_state._last is not None:
            raise SafeHaltError("bootstrap() called on a vault that already has a checkpoint")
        with RootKekSession(root_kek) as session:
            metadata_key = self._hierarchy.metadata_key(session.bytes())
        self._metadata = MetadataIndex(metadata_key=metadata_key)
        self._release_manager = ObjectReleaseManager(
            authority=self.authority,
            audit=self.audit,
            rollback_state=self.rollback_state,
            metadata=self._metadata,
        )
        self._tamper_handler = TamperHandler(
            policy=TamperPolicy(),
            audit=self.audit,
            on_seal=lambda ev: self._seal(),
            on_revoke=lambda ev: self._seal(),
            on_force_recovery=lambda ev: self._seal(),
        )
        self.rollback_state.genesis(initial_state_summary)
        self.audit.append("VAULT_BOOTSTRAPPED", {"vault_id": self.vault_id, "epoch": self.epoch})

    def _seal(self) -> None:
        self._sealed = True

    def _require_unsealed(self) -> None:
        if self._sealed:
            raise SafeHaltError(
                f"vault {self.vault_id} is SEALED — no operations permitted "
                f"until re-attestation/recovery clears the seal"
            )

    # ---- admission ---------------------------------------------------

    def admit(
        self,
        object_id: str,
        tool_id: str,
        real_name: str,
        category: Category,
        category_detail: str,
        plaintext: bytes,
        record: AdmissionRecord,
        root_kek: bytes,
    ) -> str:
        self._require_unsealed()
        assert self._metadata is not None, "call bootstrap() first"

        audit_entry = admit_object(record, plaintext, self.provenance, self.authority, self.audit)

        with RootKekSession(root_kek) as session:
            record_key = self._hierarchy.record_key(session.bytes(), tool_id, object_id)
        try:
            content_hash = hashlib.sha256(plaintext).hexdigest()
            nonce, ciphertext = seal(record_key, plaintext, aad=object_id.encode("utf-8"))
        finally:
            record_key = b"\x00" * len(record_key)  # best-effort; see buffer.py limitation note

        self._store.put(
            SealedObjectRef(
                object_id=object_id,
                tool_id=tool_id,
                nonce=nonce,
                ciphertext=ciphertext,
                aad=object_id.encode("utf-8"),
            )
        )
        self._metadata.admit(
            object_id=object_id,
            real_name=real_name,
            category=category,
            category_detail=category_detail,
            tool_id=tool_id,
            created_epoch=self.epoch,
            real_size=len(plaintext),
            content_sha256=content_hash,
        )
        self.rollback_state.advance({"last_admission": object_id, "audit_entry": audit_entry})
        return audit_entry

    # ---- release -------------------------------------------------------

    @contextlib.contextmanager
    def release(
        self,
        object_id: str,
        tool_id: str,
        token: AuthorityToken,
        conditions: RuntimeConditions,
        root_kek: bytes,
    ) -> Iterator[SecureBuffer]:
        self._require_unsealed()
        assert self._release_manager is not None, "call bootstrap() first"
        sealed = self._store.get(object_id)
        with RootKekSession(root_kek) as session:
            record_key = self._hierarchy.record_key(session.bytes(), tool_id, object_id)
        with self._release_manager.release(
            sealed=sealed,
            record_key=record_key,
            token=token,
            conditions=conditions,
            expected_state_sequence=self.rollback_state.last_sequence,
        ) as buf:
            yield buf

    # ---- tamper ----------------------------------------------------

    def report_tamper(self, event: TamperEvent, detail: dict[str, object]) -> TamperResponse:
        assert self._tamper_handler is not None, "call bootstrap() first"
        return self._tamper_handler.handle(event, detail)

    def regenerate_component(
        self,
        component_id: str,
        blueprint: ComponentBlueprint,
        trusted_signers: set[bytes],
        attestation_nonce: bytes,
        loop_guard: LoopGuard | None = None,
    ) -> RegenerationRecord:
        engine = RegenerationEngine(
            trusted_blueprint_signers=trusted_signers,
            attestation=self.attestation,
            audit=self.audit,
            loop_guard=loop_guard,
        )
        return engine.regenerate(component_id, blueprint, attestation_nonce)

    # ---- recovery --------------------------------------------------

    def recover(
        self,
        request: RecoveryRequest,
        policy: RecoveryQuorumPolicy,
        fresh_factors: tuple[bytes, ...],
    ) -> bytes:
        new_root_kek, result = execute_recovery(
            request=request,
            policy=policy,
            audit=self.audit,
            current_epoch=self.epoch,
            fresh_factors=fresh_factors,
            factor_combine_info=f"vault-root:{self.vault_id}".encode(),
        )
        self.epoch = result.new_epoch
        self._hierarchy = KeyHierarchy(vault_id=self.vault_id, epoch=self.epoch)
        self._sealed = False
        self.rollback_state.advance(
            {"recovery_epoch": self.epoch, "audit_entry": result.audit_entry_id}
        )
        return new_root_kek
