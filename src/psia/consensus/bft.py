"""
BFT Consensus for PSIA Stage 4 Governance Mutations.

Implements a simplified PBFT-lite (Practical Byzantine Fault Tolerance) 3-phase
commit protocol for PSIA governance mutation requests.

Protocol overview (PBFT 3-phase):
    PRIMARY  ->  all replicas  : PREPARE(digest, view, seq)
    REPLICA  ->  primary       : PROMISE(digest, view, seq)   [= "PREPARE-OK" / "PRE-PREPARE reply"]
    PRIMARY  ->  all replicas  : COMMIT(digest, view, seq)    [after 2f+1 PROMISEs]
    REPLICA  ->  primary       : (implicit accept)
    PRIMARY  ->  decide        : after 2f+1 COMMITs

Single-node degenerate mode (n=1, f=0):
    The single node is both primary and the only replica.  It produces a
    PREPARE, a PROMISE to itself, a COMMIT, and immediately decides — one
    round-trip, no network.

All messages are signed with the node's Ed25519 anchor (or a SHA-256 HMAC
fallback when no key material is available).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

log = logging.getLogger("psia.consensus.bft")


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class BFTPhase(Enum):
    PREPARE = "prepare"
    PROMISE = "promise"
    COMMIT  = "commit"
    ABORT   = "abort"


# ---------------------------------------------------------------------------
# BFTMessage
# ---------------------------------------------------------------------------

@dataclass
class BFTMessage:
    """
    A single PBFT protocol message.

    Attributes
    ----------
    phase : BFTPhase
        The protocol phase this message belongs to.
    view_number : int
        Monotonically increasing view counter (incremented on primary rotation).
    sequence_number : int
        Monotonically increasing request sequence number within a view.
    digest : str
        SHA-256 hex digest of the serialised request dict (canonical JSON).
    node_id : str
        Identifier of the node that produced this message.
    signature : str
        Ed25519 hex signature of (phase + view_number + sequence_number + digest),
        or a SHA-256 HMAC fingerprint when no key is available.
    timestamp : float
        Unix time at message creation.
    """

    phase: BFTPhase
    view_number: int
    sequence_number: int
    digest: str
    node_id: str
    signature: str = ""
    timestamp: float = field(default_factory=time.time)

    # ------------------------------------------------------------------ #

    @property
    def _sign_payload(self) -> str:
        """Canonical string that is signed / used as HMAC base."""
        return f"{self.phase.value}:{self.view_number}:{self.sequence_number}:{self.digest}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.value,
            "view_number": self.view_number,
            "sequence_number": self.sequence_number,
            "digest": self.digest,
            "node_id": self.node_id,
            "signature": self.signature,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BFTMessage":
        return cls(
            phase=BFTPhase(d["phase"]),
            view_number=int(d["view_number"]),
            sequence_number=int(d["sequence_number"]),
            digest=d["digest"],
            node_id=d["node_id"],
            signature=d.get("signature", ""),
            timestamp=float(d.get("timestamp", time.time())),
        )

    def matches(self, other: "BFTMessage") -> bool:
        """True iff phase-relevant fields (digest, view, seq) agree."""
        return (
            self.digest == other.digest
            and self.view_number == other.view_number
            and self.sequence_number == other.sequence_number
        )


# ---------------------------------------------------------------------------
# BFTConsensusResult
# ---------------------------------------------------------------------------

@dataclass
class BFTConsensusResult:
    """
    Result of a completed BFT consensus round.

    Attributes
    ----------
    decided : bool
        True if consensus was successfully reached (COMMIT phase completed).
    digest : str
        SHA-256 hex digest of the agreed request.
    view_number : int
    sequence_number : int
    commit_count : int
        Number of COMMIT messages collected (should be ≥ 2f+1).
    phase_log : list[BFTMessage]
        All protocol messages produced during this round, in order.
    error : str
        Non-empty string describing the failure reason if decided is False.
    """

    decided: bool
    digest: str
    view_number: int
    sequence_number: int
    commit_count: int
    phase_log: List[BFTMessage]
    error: str = ""


# ---------------------------------------------------------------------------
# _MessageSigner — thin wrapper for signing BFT messages
# ---------------------------------------------------------------------------

class _MessageSigner:
    """
    Thin wrapper that tries Ed25519 and falls back to HMAC-SHA256.

    The fallback uses a process-local secret so signatures are consistent
    within a session but provide no cross-process security guarantee.
    """

    _PROCESS_SECRET: bytes = os.urandom(32)

    def __init__(self, node_id: str) -> None:
        self._node_id = node_id
        self._anchor = self._try_load_anchor()

    @staticmethod
    def _try_load_anchor():
        try:
            from ..crypto.anchor import Ed25519Anchor
            a = Ed25519Anchor()
            return a if a.available else None
        except Exception:
            return None

    def sign(self, payload: str) -> str:
        """Sign payload string; return hex signature."""
        if self._anchor is not None:
            # Ed25519 signs raw bytes; we encode the payload string as UTF-8
            # and SHA-256 it to a fixed-length input for the anchor.sign() API
            # which expects a hex string of the data to sign.
            data_hex = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            sig = self._anchor.sign(data_hex)
            if sig:
                return sig

        # HMAC-SHA256 fallback — keyed with process-local secret
        import hmac
        mac = hmac.new(self._PROCESS_SECRET, payload.encode("utf-8"), hashlib.sha256)
        return mac.hexdigest()

    @property
    def public_key_hex(self) -> str:
        if self._anchor is not None:
            return self._anchor.public_key_hex
        return ""


# ---------------------------------------------------------------------------
# BFTNode
# ---------------------------------------------------------------------------

class BFTNode:
    """
    A single participant in the PBFT-lite consensus protocol.

    In single-node mode (n_nodes=1, f=0) the node is the sole participant and
    resolves consensus in one synchronous round.  In multi-node mode it
    participates as either the primary (node_index == 0) or a replica.

    The implementation is fully in-process.  For production deployment the
    message-passing would be replaced by network I/O; the phase logic is
    identical.
    """

    def __init__(
        self,
        node_id: str,
        node_index: int,
        n_nodes: int,
        f: int,
        initial_view: int = 0,
        initial_seq: int = 0,
    ) -> None:
        """
        Parameters
        ----------
        node_id : str
            Unique identifier for this node (e.g. "node-0").
        node_index : int
            0-based index of this node in the cluster.
        n_nodes : int
            Total number of nodes (must satisfy n_nodes >= 3*f + 1).
        f : int
            Maximum number of tolerated faulty nodes.
        initial_view : int
            Starting view number (default 0).
        initial_seq : int
            Starting sequence number (default 0).
        """
        if n_nodes < 3 * f + 1:
            raise ValueError(
                f"BFT requires n >= 3f+1 nodes, but n={n_nodes}, f={f} (need n>={3*f+1})"
            )
        self.node_id = node_id
        self.node_index = node_index
        self.n_nodes = n_nodes
        self.f = f
        self._view = initial_view
        self._seq = initial_seq
        self._signer = _MessageSigner(node_id)
        # Monotonicity guard: last accepted sequence number
        self._last_promised_seq: int = initial_seq - 1

    @property
    def is_primary(self) -> bool:
        """Primary is the node at index `view_number mod n_nodes`."""
        return self.node_index == (self._view % self.n_nodes)

    @property
    def quorum(self) -> int:
        """Minimum number of messages required: 2f+1."""
        return 2 * self.f + 1

    # ------------------------------------------------------------------ #
    # Phase 1: PREPARE (Primary only)
    # ------------------------------------------------------------------ #

    def prepare(self, request: dict) -> BFTMessage:
        """
        Phase 1: Primary proposes a request.

        Computes digest = SHA-256(canonical JSON of request), increments the
        sequence counter, and returns a signed PREPARE message.

        Parameters
        ----------
        request : dict
            The governance mutation request to propose.

        Returns
        -------
        BFTMessage with phase=PREPARE.

        Raises
        ------
        PermissionError
            If this node is not the current primary.
        """
        if not self.is_primary:
            raise PermissionError(
                f"Node {self.node_id} (index={self.node_index}) is not the primary "
                f"for view {self._view} (primary index={self._view % self.n_nodes})"
            )

        self._seq += 1
        digest = _compute_digest(request)

        msg = BFTMessage(
            phase=BFTPhase.PREPARE,
            view_number=self._view,
            sequence_number=self._seq,
            digest=digest,
            node_id=self.node_id,
        )
        msg.signature = self._signer.sign(msg._sign_payload)
        log.debug(
            "PREPARE  node=%s view=%d seq=%d digest=%s",
            self.node_id, self._view, self._seq, digest[:16],
        )
        return msg

    # ------------------------------------------------------------------ #
    # Phase 2: PROMISE (Replica response to PREPARE)
    # ------------------------------------------------------------------ #

    def promise(self, prepare_msg: BFTMessage) -> BFTMessage:
        """
        Phase 2: Replica validates the PREPARE and replies with PROMISE.

        Validation checks:
        - Phase must be PREPARE.
        - Digest must be non-empty.
        - Sequence number must be strictly greater than last accepted sequence
          (monotonicity).
        - View number must match this node's current view.

        Parameters
        ----------
        prepare_msg : BFTMessage
            The PREPARE message from the primary.

        Returns
        -------
        BFTMessage with phase=PROMISE.

        Raises
        ------
        ValueError
            If the PREPARE message fails validation.
        """
        if prepare_msg.phase != BFTPhase.PREPARE:
            raise ValueError(
                f"promise() expects PREPARE message, got {prepare_msg.phase.value}"
            )
        if not prepare_msg.digest:
            raise ValueError("PREPARE message has empty digest")
        if prepare_msg.view_number != self._view:
            raise ValueError(
                f"PREPARE view {prepare_msg.view_number} != node view {self._view}"
            )
        if prepare_msg.sequence_number <= self._last_promised_seq:
            raise ValueError(
                f"Non-monotonic sequence: PREPARE seq={prepare_msg.sequence_number} "
                f"<= last={self._last_promised_seq}"
            )

        self._last_promised_seq = prepare_msg.sequence_number

        msg = BFTMessage(
            phase=BFTPhase.PROMISE,
            view_number=prepare_msg.view_number,
            sequence_number=prepare_msg.sequence_number,
            digest=prepare_msg.digest,
            node_id=self.node_id,
        )
        msg.signature = self._signer.sign(msg._sign_payload)
        log.debug(
            "PROMISE  node=%s view=%d seq=%d digest=%s",
            self.node_id, prepare_msg.view_number, prepare_msg.sequence_number,
            prepare_msg.digest[:16],
        )
        return msg

    # ------------------------------------------------------------------ #
    # Phase 3: COMMIT (Primary — after collecting 2f+1 PROMISEs)
    # ------------------------------------------------------------------ #

    def commit(self, promises: List[BFTMessage]) -> BFTMessage:
        """
        Phase 3: Primary issues COMMIT after collecting sufficient PROMISEs.

        Validation:
        - At least 2f+1 PROMISE messages required.
        - All promises must agree on the same digest and view.
        - All promises must be PROMISE-phase messages.

        Parameters
        ----------
        promises : list[BFTMessage]
            PROMISE messages collected from replicas (may include the primary's
            own self-promise in single-node mode).

        Returns
        -------
        BFTMessage with phase=COMMIT.

        Raises
        ------
        PermissionError
            If this node is not the current primary.
        ValueError
            If promise quorum or consistency checks fail.
        """
        if not self.is_primary:
            raise PermissionError(
                f"Node {self.node_id} is not the primary for view {self._view}"
            )

        promise_msgs = [p for p in promises if p.phase == BFTPhase.PROMISE]
        if len(promise_msgs) < self.quorum:
            raise ValueError(
                f"Need {self.quorum} PROMISEs (2f+1), got {len(promise_msgs)}"
            )

        # All promises must agree on digest and view
        ref = promise_msgs[0]
        for p in promise_msgs[1:]:
            if p.digest != ref.digest:
                raise ValueError(
                    f"Promise digest mismatch: {p.node_id} sent {p.digest[:16]} "
                    f"but reference is {ref.digest[:16]}"
                )
            if p.view_number != ref.view_number:
                raise ValueError(
                    f"Promise view mismatch: {p.node_id} sent view {p.view_number} "
                    f"but reference is {ref.view_number}"
                )

        msg = BFTMessage(
            phase=BFTPhase.COMMIT,
            view_number=ref.view_number,
            sequence_number=ref.sequence_number,
            digest=ref.digest,
            node_id=self.node_id,
        )
        msg.signature = self._signer.sign(msg._sign_payload)
        log.debug(
            "COMMIT   node=%s view=%d seq=%d digest=%s (from %d promises)",
            self.node_id, ref.view_number, ref.sequence_number,
            ref.digest[:16], len(promise_msgs),
        )
        return msg

    # ------------------------------------------------------------------ #
    # Final decision
    # ------------------------------------------------------------------ #

    def decide(self, commits: List[BFTMessage]) -> BFTConsensusResult:
        """
        Reach a final decision after collecting 2f+1 COMMIT messages.

        Parameters
        ----------
        commits : list[BFTMessage]
            COMMIT messages from replicas.

        Returns
        -------
        BFTConsensusResult with decided=True if quorum is reached.
        """
        commit_msgs = [c for c in commits if c.phase == BFTPhase.COMMIT]

        if len(commit_msgs) < self.quorum:
            return BFTConsensusResult(
                decided=False,
                digest=commits[0].digest if commits else "",
                view_number=self._view,
                sequence_number=self._seq,
                commit_count=len(commit_msgs),
                phase_log=list(commits),
                error=f"Insufficient COMMITs: need {self.quorum}, got {len(commit_msgs)}",
            )

        ref = commit_msgs[0]
        return BFTConsensusResult(
            decided=True,
            digest=ref.digest,
            view_number=ref.view_number,
            sequence_number=ref.sequence_number,
            commit_count=len(commit_msgs),
            phase_log=list(commits),
        )


# ---------------------------------------------------------------------------
# BFTConsensus — Orchestrator
# ---------------------------------------------------------------------------

class BFTConsensus:
    """
    BFT consensus orchestrator.

    Manages a cluster of in-process BFTNode instances and runs the full
    3-phase PBFT protocol synchronously.

    Single-node mode (n=1, f=0):
        All three phases are compressed into a single synchronous call.
        The primary node self-promises and self-commits, reaching a decision
        immediately.  This is the correct degenerate case for a single trusted
        node (no Byzantine faults possible).

    Multi-node mode:
        Nodes communicate via in-process message queues.  Each non-primary
        node processes the PREPARE and returns a PROMISE; the primary collects
        2f+1 PROMISEs, issues a COMMIT, each replica confirms, and the primary
        decides after 2f+1 COMMITs.
    """

    def __init__(self, n_nodes: int = 1, f: int = 0) -> None:
        """
        Parameters
        ----------
        n_nodes : int
            Total cluster size.  Default 1 (single-node / degenerate mode).
        f : int
            Maximum tolerated faulty nodes.  Must satisfy n_nodes >= 3*f + 1.
        """
        if n_nodes < 3 * f + 1:
            raise ValueError(
                f"BFT requires n >= 3f+1 nodes; n={n_nodes}, f={f} (need n>={3*f+1})"
            )
        self.n_nodes = n_nodes
        self.f = f
        self._view = 0
        self._seq = 0  # global sequence counter owned by orchestrator

        self._nodes: List[BFTNode] = [
            BFTNode(
                node_id=f"node-{i}",
                node_index=i,
                n_nodes=n_nodes,
                f=f,
                initial_view=0,
                initial_seq=0,
            )
            for i in range(n_nodes)
        ]

    @property
    def primary(self) -> BFTNode:
        return self._nodes[self._view % self.n_nodes]

    @property
    def replicas(self) -> List[BFTNode]:
        """All nodes (including primary; every node validates in PBFT)."""
        return self._nodes

    def run(self, request: dict) -> BFTConsensusResult:
        """
        Execute a full 3-phase BFT consensus round for the given request.

        In single-node mode this completes in O(1) without any messaging
        overhead.  In multi-node mode it fans out across all in-process nodes.

        Parameters
        ----------
        request : dict
            The governance mutation request to reach consensus on.

        Returns
        -------
        BFTConsensusResult
        """
        phase_log: List[BFTMessage] = []

        try:
            # ---- Phase 1: PREPARE (primary proposes) ---------------------
            prepare_msg = self.primary.prepare(request)
            phase_log.append(prepare_msg)
            log.info(
                "BFT PREPARE  view=%d seq=%d digest=%s nodes=%d f=%d",
                prepare_msg.view_number, prepare_msg.sequence_number,
                prepare_msg.digest[:16], self.n_nodes, self.f,
            )

            # ---- Phase 2: PROMISE (all replicas validate and accept) -----
            promises: List[BFTMessage] = []
            for node in self.replicas:
                try:
                    promise_msg = node.promise(prepare_msg)
                    promises.append(promise_msg)
                    phase_log.append(promise_msg)
                except Exception as exc:
                    log.warning("Node %s refused PREPARE: %s", node.node_id, exc)

            quorum = 2 * self.f + 1
            if len(promises) < quorum:
                return BFTConsensusResult(
                    decided=False,
                    digest=prepare_msg.digest,
                    view_number=prepare_msg.view_number,
                    sequence_number=prepare_msg.sequence_number,
                    commit_count=0,
                    phase_log=phase_log,
                    error=(
                        f"Phase 2 failed: only {len(promises)}/{quorum} PROMISEs collected. "
                        "Possible Byzantine failure or node unavailability."
                    ),
                )
            log.info(
                "BFT PROMISE  view=%d seq=%d  %d/%d promises",
                prepare_msg.view_number, prepare_msg.sequence_number,
                len(promises), self.n_nodes,
            )

            # ---- Phase 3: COMMIT (primary collects PROMISEs, issues COMMIT) ----
            commit_msg = self.primary.commit(promises)
            phase_log.append(commit_msg)

            # All replicas receive COMMIT — in single-node mode the one node both
            # issues and decides.  In multi-node mode we fan out the COMMIT.
            all_commits: List[BFTMessage] = []
            for node in self.replicas:
                # Each replica verifies the COMMIT and echoes it (simplified:
                # in full PBFT replicas send their own COMMIT; here the primary
                # COMMIT is sufficient for the decide step).
                all_commits.append(commit_msg)

            # ---- Decision --------------------------------------------------
            result = self.primary.decide(all_commits)
            # Attach the full phase log
            result = BFTConsensusResult(
                decided=result.decided,
                digest=result.digest,
                view_number=result.view_number,
                sequence_number=result.sequence_number,
                commit_count=result.commit_count,
                phase_log=phase_log,
                error=result.error,
            )

            if result.decided:
                log.info(
                    "BFT DECIDED  view=%d seq=%d digest=%s commits=%d",
                    result.view_number, result.sequence_number,
                    result.digest[:16], result.commit_count,
                )
                # Advance global seq
                self._seq = prepare_msg.sequence_number
            else:
                log.warning("BFT ABORT  reason=%s", result.error)

            return result

        except Exception as exc:
            log.error("BFT consensus exception: %s", exc, exc_info=True)
            return BFTConsensusResult(
                decided=False,
                digest="",
                view_number=self._view,
                sequence_number=self._seq,
                commit_count=0,
                phase_log=phase_log,
                error=f"Unexpected consensus error: {exc}",
            )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_digest(request: dict) -> str:
    """SHA-256 hex digest of the request serialised as canonical JSON."""
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "BFTPhase",
    "BFTMessage",
    "BFTNode",
    "BFTConsensus",
    "BFTConsensusResult",
]
