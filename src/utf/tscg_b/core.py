from __future__ import annotations

import binascii
import hashlib
import struct

from tscg.core import Combine, Expr, Pipeline, Symbol, canonical, parse, validate

MAGIC = b"TSGB"
VERSION = 1

OPCODES = {
    "COG": 0x02,
    "DNT": 0x03,
    "SHD": 0x04,
    "INV": 0x05,
    "CAP": 0x06,
    "QRM": 0x07,
    "COM": 0x08,
    "ANC": 0x09,
    "RFX": 0x0B,
    "SAFE": 0x0D,
    "->": 0x10,
    "^": 0x11,
    "||": 0x14,
}
REVERSE = {v: k for k, v in OPCODES.items()}


class TSCGBError(ValueError):
    pass


def encode_expr(expr: Expr) -> bytes:
    if isinstance(expr, Symbol):
        if expr.name not in OPCODES:
            raise TSCGBError(f"unsupported symbol {expr.name!r}")
        out = bytearray([OPCODES[expr.name], len(expr.args)])
        for arg in expr.args:
            data = arg.encode("utf-8")
            if len(data) > 255:
                raise TSCGBError("arg too long")
            out.append(len(data))
            out.extend(data)
        return bytes(out)
    if isinstance(expr, Pipeline):
        out = bytearray()
        for idx, item in enumerate(expr.items):
            if idx:
                out.extend(encode_expr(Symbol("->")))
            out.extend(encode_expr(item))
        return bytes(out)
    if isinstance(expr, Combine):
        return (
            encode_expr(expr.left)
            + encode_expr(Symbol(expr.op))
            + encode_expr(expr.right)
        )
    raise TypeError(expr)


def decode_expr(payload: bytes) -> str:
    parts: list[str] = []
    i = 0
    while i < len(payload):
        opcode = payload[i]
        i += 1
        if opcode not in REVERSE:
            raise TSCGBError(f"invalid opcode 0x{opcode:02x}")
        symbol = REVERSE[opcode]
        argc = payload[i]
        i += 1
        args = []
        for _ in range(argc):
            if i >= len(payload):
                raise TSCGBError("truncated arg")
            n = payload[i]
            i += 1
            if i + n > len(payload):
                raise TSCGBError("truncated arg data")
            args.append(payload[i : i + n].decode("utf-8"))
            i += n
        if args:
            parts.append(f"{symbol}({','.join(args)})")
        else:
            parts.append(symbol)
    return " ".join(parts)


def pack_text(text: str) -> bytes:
    expr = parse(text)
    validate(expr)
    normalized = canonical(expr)
    payload = encode_expr(expr)
    crc = binascii.crc32(payload) & 0xFFFFFFFF
    digest = hashlib.sha256(normalized.encode("utf-8")).digest()
    return (
        MAGIC
        + struct.pack(">BBH", VERSION, 0, len(payload))
        + payload
        + struct.pack(">I", crc)
        + digest
    )


class StreamDecoder:
    """
    Streaming TSCG-B decoder for multi-frame byte streams.

    Accepts arbitrary-size byte chunks via ``feed()`` and returns a list of
    fully-decoded frame dicts for every complete frame found in the buffered
    data.  Partial frames are retained in the internal buffer until the
    remaining bytes arrive.

    Frame wire format (all big-endian):
        4 bytes  magic       b"TSGB"
        1 byte   version
        1 byte   flags
        2 bytes  payload_len (uint16)
        N bytes  payload
        4 bytes  CRC32       of payload
       32 bytes  SHA-256     of canonical text

    Total frame size = 8 + payload_len + 36 bytes.

    Usage::

        dec = StreamDecoder()
        for chunk in socket_or_file:
            frames = dec.feed(chunk)
            for frame in frames:
                print(frame["text"])

        # After all data consumed, check for leftover partial bytes:
        remaining = dec.pending_bytes
        if remaining:
            raise ValueError(f"{remaining} bytes of incomplete trailing frame")

    Errors in individual frames raise :exc:`TSCGBError` at the point the
    complete frame becomes available, leaving the rest of the buffer intact.
    """

    _HEADER_LEN = 8    # magic(4) + version(1) + flags(1) + payload_len(2)
    _TRAILER_LEN = 36  # CRC32(4) + SHA-256(32)
    _MIN_FRAME = _HEADER_LEN + _TRAILER_LEN  # 44 bytes minimum (zero-length payload)

    def __init__(self) -> None:
        self._buf = bytearray()

    def feed(self, data: bytes) -> list[dict]:
        """
        Consume *data*, decode all complete frames, and return them.

        Returns an empty list if no complete frame is yet available.
        Raises :exc:`TSCGBError` if a frame's magic, version, CRC, or
        SHA-256 validation fails.
        """
        self._buf.extend(data)
        return self._drain()

    def _drain(self) -> list[dict]:
        frames: list[dict] = []
        while True:
            if len(self._buf) < self._MIN_FRAME:
                break  # not enough bytes even for the smallest frame

            # Peek at the magic before committing
            if self._buf[:4] != MAGIC:
                # Scan forward to resync (skip one byte at a time)
                idx = self._buf.find(MAGIC, 1)
                if idx == -1:
                    # No magic found — discard everything except the last 3 bytes
                    # (they could be the start of a split magic sequence)
                    self._buf = self._buf[-3:]
                    break
                self._buf = self._buf[idx:]
                continue

            if len(self._buf) < self._HEADER_LEN:
                break  # header not fully buffered yet

            # Read payload length from header
            _version, _flags, payload_len = struct.unpack_from(">BBH", self._buf, 4)
            frame_len = self._HEADER_LEN + payload_len + self._TRAILER_LEN

            if len(self._buf) < frame_len:
                break  # complete frame not yet buffered

            # Extract exactly one frame and advance buffer
            raw_frame = bytes(self._buf[:frame_len])
            self._buf = self._buf[frame_len:]

            # Unpack (validates CRC + SHA-256) — raises TSCGBError on corruption
            frames.append(unpack_frame(raw_frame))

        return frames

    @property
    def pending_bytes(self) -> int:
        """Number of buffered bytes that have not yet formed a complete frame."""
        return len(self._buf)

    def reset(self) -> None:
        """Discard all buffered data."""
        self._buf.clear()


def unpack_frame(frame: bytes) -> dict:
    if len(frame) < 4 + 1 + 1 + 2 + 4 + 32:
        raise TSCGBError("truncated frame")
    if frame[:4] != MAGIC:
        raise TSCGBError("invalid magic")
    version, flags, length = struct.unpack(">BBH", frame[4:8])
    if version != VERSION:
        raise TSCGBError(f"unsupported version {version}")
    payload_end = 8 + length
    if payload_end + 4 + 32 != len(frame):
        raise TSCGBError("invalid frame length")
    payload = frame[8:payload_end]
    crc_expected = struct.unpack(">I", frame[payload_end : payload_end + 4])[0]
    crc_actual = binascii.crc32(payload) & 0xFFFFFFFF
    if crc_expected != crc_actual:
        raise TSCGBError("CRC mismatch")
    text = decode_expr(payload)
    digest_expected = frame[payload_end + 4 :]
    digest_actual = hashlib.sha256(text.encode("utf-8")).digest()
    if digest_expected != digest_actual:
        raise TSCGBError("SHA mismatch")
    return {
        "version": version,
        "flags": flags,
        "payloadLen": length,
        "text": text,
        "crc32": f"{crc_actual:08x}",
        "sha256": digest_actual.hex(),
    }
