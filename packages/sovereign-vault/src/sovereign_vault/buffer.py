"""
sovereign_vault.buffer

LIMITATION (stated here rather than buried): CPython does not give you a
real guarantee against plaintext residue. Immutable `bytes` objects can be
copied by the interpreter, moved by the allocator, and are not reliably
overwritten. This module does the best available things in pure Python —
mutable `bytearray` storage, explicit overwrite-then-free, and best-effort
mlock on POSIX to keep the page out of swap — and refuses to pretend that
is equivalent to a hardware secure enclave. If you need a real guarantee,
the record key must never be materialized in a CPython `bytes` object at
all; that requires either a C extension or moving decryption into a
process boundary with its own memory hygiene (see deploy/ for the
isolation model this is meant to run inside).
"""

from __future__ import annotations

import contextlib
import ctypes
import ctypes.util
import sys


class SecureBuffer:
    """
    Mutable byte buffer meant to hold exactly one plaintext object for
    exactly as long as the consumer needs it, then be zeroized.

    Usage:
        with SecureBuffer(plaintext_bytes) as buf:
            consumer.handle(buf.view())
        # buf is zeroized here, even on exception
    """

    def __init__(self, data: bytes):
        self._buf = bytearray(data)
        self._locked = False
        self._freed = False
        self._mlock()

    def _mlock(self) -> None:
        if not sys.platform.startswith("linux"):
            return  # best-effort only; no-op on non-Linux rather than raising
        try:
            libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
            addr = (ctypes.c_char * len(self._buf)).from_buffer(self._buf)
            rc = libc.mlock(ctypes.byref(addr), ctypes.c_size_t(len(self._buf)))
            self._locked = rc == 0
        except Exception:
            # mlock is a hardening measure, not a correctness requirement —
            # failing to lock must never block zeroization or release.
            self._locked = False

    def _munlock(self) -> None:
        if not self._locked:
            return
        try:
            libc = ctypes.CDLL(ctypes.util.find_library("c") or "libc.so.6", use_errno=True)
            addr = (ctypes.c_char * len(self._buf)).from_buffer(self._buf)
            libc.munlock(ctypes.byref(addr), ctypes.c_size_t(len(self._buf)))
        except Exception:
            pass
        self._locked = False

    def view(self) -> memoryview:
        if self._freed:
            raise ValueError("SecureBuffer already zeroized")
        return memoryview(self._buf)

    def zeroize(self) -> None:
        if self._freed:
            return
        for i in range(len(self._buf)):
            self._buf[i] = 0
        self._munlock()
        self._buf = bytearray(0)
        self._freed = True

    def __enter__(self) -> SecureBuffer:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.zeroize()

    def __len__(self) -> int:
        return len(self._buf)

    def __del__(self) -> None:
        # Backstop only — do not rely on __del__ for security guarantees;
        # the `with` block is the real contract.
        with contextlib.suppress(Exception):
            self.zeroize()
