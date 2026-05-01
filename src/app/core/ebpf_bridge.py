"""
eBPF bridge stub — kernel-level execution pinning (requires Linux/WSL2).

On Windows this module provides a safe no-op stub that records the attempted
pin but does not interact with the kernel.  When the system runs on Linux with
CAP_BPF and a loaded LSM program, replace the stub body with actual eBPF map
writes via the bcc or libbpf Python bindings.
"""

from __future__ import annotations

import logging
import platform

logger = logging.getLogger(__name__)

_IS_LINUX = platform.system() == "Linux"


class EBPFBridge:
    """
    Mediates between the execution router and the kernel-level LSM/BPF layer.

    On Linux: intended to write pid→expected_hash mappings into a BPF map so
    that the LSM hook can block any execve whose SHA-256 does not match.

    On Windows / macOS (and whenever the BPF map is not loaded): the stub logs
    the attempted pin and returns True so execution is not blocked in dev.
    """

    def __init__(self) -> None:
        if _IS_LINUX:
            logger.info("EBPFBridge: running on Linux — BPF pinning stub active (wire real BPF here)")
        else:
            logger.info("EBPFBridge: non-Linux platform (%s) — stub mode", platform.system())

    def pin_allowed_execution(self, pid: int, expected_hash: str, domain: str) -> bool:
        """
        Record that `pid` is authorised to execute the binary whose SHA-256 is
        `expected_hash`.

        Returns:
            True  — pinning accepted (stub always succeeds; real impl writes BPF map)
            False — pinning rejected (real impl: BPF map write failed)
        """
        if _IS_LINUX:
            # TODO: replace with actual BPF map write, e.g.:
            #   bpf["allowed_hashes"][pid] = expected_hash.encode()
            logger.debug(
                "EBPFBridge.pin_allowed_execution [stub] pid=%s domain=%s hash=%s",
                pid, domain, expected_hash[:16],
            )
        else:
            logger.debug(
                "EBPFBridge.pin_allowed_execution [windows-stub] pid=%s domain=%s",
                pid, domain,
            )

        return True

    def clear_pin(self, pid: int) -> None:
        """Remove an execution pin after the gate releases control."""
        logger.debug("EBPFBridge.clear_pin pid=%s", pid)


_ebpf_bridge_instance: EBPFBridge | None = None


def get_ebpf_bridge() -> EBPFBridge:
    global _ebpf_bridge_instance
    if _ebpf_bridge_instance is None:
        _ebpf_bridge_instance = EBPFBridge()
    return _ebpf_bridge_instance


__all__ = ["EBPFBridge", "get_ebpf_bridge"]
