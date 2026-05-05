from __future__ import annotations

import binascii
import hashlib
import struct
from dataclasses import dataclass

from tscg.core import Symbol, Pipeline, Combine, Expr, canonical, parse, validate

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
        return encode_expr(expr.left) + encode_expr(Symbol(expr.op)) + encode_expr(expr.right)
    raise TypeError(expr)


def decode_expr(payload: bytes) -> str:
    parts: list[str] = []
    i = 0
    while i < len(payload):
        opcode = payload[i]; i += 1
        if opcode not in REVERSE:
            raise TSCGBError(f"invalid opcode 0x{opcode:02x}")
        symbol = REVERSE[opcode]
        argc = payload[i]; i += 1
        args = []
        for _ in range(argc):
            if i >= len(payload):
                raise TSCGBError("truncated arg")
            n = payload[i]; i += 1
            if i + n > len(payload):
                raise TSCGBError("truncated arg data")
            args.append(payload[i:i+n].decode("utf-8"))
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
    crc = binascii.crc32(payload) & 0xffffffff
    digest = hashlib.sha256(normalized.encode("utf-8")).digest()
    return MAGIC + struct.pack(">BBH", VERSION, 0, len(payload)) + payload + struct.pack(">I", crc) + digest


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
    crc_expected = struct.unpack(">I", frame[payload_end:payload_end+4])[0]
    crc_actual = binascii.crc32(payload) & 0xffffffff
    if crc_expected != crc_actual:
        raise TSCGBError("CRC mismatch")
    text = decode_expr(payload)
    digest_expected = frame[payload_end+4:]
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
