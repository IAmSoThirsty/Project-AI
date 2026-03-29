# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / tscg_b.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / tscg_b.py


import hashlib
import logging
import struct
import zlib

from project_ai.utils.tscg import TSCG, TSCGDecoder, TSCGEncoder

logger = logging.getLogger(__name__)


class TSCGB(TSCG):
    """
    TSCG-B (Binary) Formal Specification v1.0
    Authoritative constitutional wire protocol implementation.
    """

    MAGIC = b"TSGB"
    PROTO_VER = 0x01

    # 3.1 & 3.2 Opcode Table
    OP_CODES = {
        "ING": 0x01,
        "COG": 0x02,
        "Δ_NT": 0x03,
        "SHD": 0x04,
        "INV": 0x05,
        "CAP": 0x06,
        "QRM_LINEAR": 0x07,
        "COM": 0x08,
        "ANC": 0x09,
        "LED": 0x0A,
        "RFX": 0x0B,
        "ESC": 0x0C,
        "SAFE": 0x0D,
        "MUT": 0x0E,
        "SEL": 0x0F,
        "QRM_STATIC": 0x15,
        "→": 0x10,
        "∧": 0x11,
        "∨": 0x12,
        "¬": 0x13,
        "||": 0x14,
        ":=": 0x16,
        "=": 0x17,
        "∈": 0x18,
        "≥": 0x19,
        "<": 0x1A,
    }

    # 4.2 Parameter Schemas
    SCHEMAS = {
        "SHD": ">B",  # U8 Version
        "INV": ">B",  # U8 Identifier
        "QRM_LINEAR": ">BBBB",  # U8, U8, U8, U8
        "QRM_STATIC": ">HH",  # U16, U16
        "RFX": ">B",  # U8 Flag
        "ESC": ">B",  # U8 Level
    }


class TSCGBEncoder(TSCGEncoder):
    def encode_binary(
        self, expression: str, sd_ver: int = 1, const_ver: int = 1
    ) -> bytes:
        """
        Encodes TSCG text into formal v1.0 Wire Frame.
        """
        # Canonical Tokenization: ensure symbols are distinct
        expr = expression.replace("(", " ( ").replace(")", " ) ").replace(",", " ")
        for sym in TSCGB.OP_CODES:
            if len(sym) == 1 and not sym.isalnum():
                expr = expr.replace(sym, f" {sym} ")

        tokens = expr.split()
        payload = bytearray()

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in TSCGB.OP_CODES:
                payload.append(TSCGB.OP_CODES[token])

                if token in TSCGB.SCHEMAS:
                    schema = TSCGB.SCHEMAS[token]
                    params = []
                    if i + 1 < len(tokens) and tokens[i + 1] == "(":
                        i += 2
                        while i < len(tokens) and tokens[i] != ")":
                            try:
                                params.append(int(tokens[i]))
                            except ValueError:
                                logger.warning("Encountered non-terminal exception in %s", __name__)
                            i += 1
                    if params:
                        payload.extend(struct.pack(schema, *params))
            i += 1

        header = bytearray(TSCGB.MAGIC)
        header.append(TSCGB.PROTO_VER)
        header.append(sd_ver)
        header.append(const_ver)
        header.append(0x00)
        header.extend(struct.pack(">H", len(payload)))

        frame_no_integrity = header + payload
        crc = struct.pack(">I", zlib.crc32(frame_no_integrity))
        sha = hashlib.sha256(frame_no_integrity).digest()

        return frame_no_integrity + crc + sha


class TSCGBDecoder(TSCGDecoder):
    def decode_binary(self, blob: bytes) -> str:
        """
        Decodes formal v1.0 Binary Frame into canonical string.
        """
        if blob[:4] != TSCGB.MAGIC:
            raise ValueError("E01: Magic Mismatch")

        pay_len = struct.unpack(">H", blob[8:10])[0]
        payload = blob[10 : 10 + pay_len]

        REV_OPS = {v: k for k, v in TSCGB.OP_CODES.items()}
        decoded = []
        i = 0
        while i < len(payload):
            op = payload[i]
            symbol = REV_OPS.get(op, "???")
            decoded.append(symbol)
            i += 1

            if symbol in TSCGB.SCHEMAS:
                schema = TSCGB.SCHEMAS[symbol]
                width = struct.calcsize(schema)
                params = struct.unpack(schema, payload[i : i + width])
                decoded.append(f"({','.join(map(str, params))})")
                i += width

        return " ".join(decoded)
