# ============================================================================ #
#                                           [2026-03-18 13:11]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 13:11             #
# COMPLIANCE: Sovereign Substrate / tscg_b_engine.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign-Native / TSCG-B v1.0 Framework                         #

"""
TSCG-B Engine
=============
Provides symbolic compression and binary framing for Project-AI workspace configurations.
Implements the TSCG-B v1.0 wire format for deterministic repository state.
"""

import binascii
import hashlib
import json
import logging
import os
import zlib
from typing import Any

# Setup Master-Tier Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("TSCG-B-Engine")

def get_existing_folders(workspace_path: str) -> list[dict[str, Any]]:
    """
    Filters out missing folders from the workspace configuration.

    Args:
        workspace_path: Path to the .code-workspace file.

    Returns:
        A list of existing folder entries.
    """
    try:
        with open(workspace_path) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load workspace file %s: %s", workspace_path, e)
        return []

    workspace_dir = os.path.dirname(workspace_path)
    filtered_folders = []

    for folder in data.get('folders', []):
        rel_path = folder.get('path', '')
        # Convert VS Code backslash escaped paths if necessary
        abs_path = os.path.abspath(os.path.join(workspace_dir, rel_path))
        if os.path.exists(abs_path):
            filtered_folders.append(folder)
        else:
            logger.warning("Skipping missing folder: %s (%s)", folder.get('name', 'Unknown'), abs_path)

    return filtered_folders

def create_tscg_b_frame(payload_bytes: bytes, sd_version: int = 0x01, const_version: int = 0x01) -> bytes:
    """
    Implements TSCG-B v1.0 Wire Format:
    MAGIC (4b) | PROTO (1b) | SD (1b) | CONST (1b) | FLAGS (1b) | LEN (2b) | PAYLOAD (Nb) | CRC32 (4b) | SHA256 (32b)

    Args:
        payload_bytes: The data to be framed.
        sd_version: Software Definition version.
        const_version: Constitutional version.

    Returns:
        The complete binary frame.
    """
    magic = b'TSGB'
    proto_ver = b'\x01'
    sd_ver = sd_version.to_bytes(1, 'big')
    const_ver = const_version.to_bytes(1, 'big')
    flags = b'\x00'

    if len(payload_bytes) > 0xFFFF:
        logger.warning("Payload size %d exceeds 2-byte length limit; truncation or protocol upgrade (v2) required.", len(payload_bytes))

    pay_len = len(payload_bytes).to_bytes(2, 'big')

    frame_body = magic + proto_ver + sd_ver + const_ver + flags + pay_len + payload_bytes

    crc = binascii.crc32(frame_body).to_bytes(4, 'big')
    sha = hashlib.sha256(frame_body).digest()

    return frame_body + crc + sha

def main() -> None:
    """
    Main entry point for workspace compression and remediation.
    """
    # Use relative pathing based on the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    workspace_file = os.path.join(project_root, "Project-AI.code-workspace")

    if not os.path.exists(workspace_file):
        logger.error("Workspace file not found at: %s", workspace_file)
        return

    # 1. Logical Compression (Filtering)
    logger.info("Reading workspace manifest: %s", workspace_file)
    try:
        with open(workspace_file) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Corrupt workspace file: %s", e)
        return

    original_count = len(config.get('folders', []))
    config['folders'] = get_existing_folders(workspace_file)
    new_count = len(config['folders'])

    logger.info("Logical Reduction: %d -> %d folders.", original_count, new_count)

    # Save the cleaned JSON version
    with open(workspace_file, 'w') as f:
        json.dump(config, f, indent=4)
    logger.info("Cleaned JSON workspace persistent.")

    # 2. TSCG-B Binary Encoding
    json_bytes = json.dumps(config).encode('utf-8')
    compressed_bytes = zlib.compress(json_bytes, level=9)

    tscg_b_data = create_tscg_b_frame(compressed_bytes)

    output_file = workspace_file + ".tscgb"
    try:
        with open(output_file, 'wb') as f:
            f.write(tscg_b_data)
        logger.info("TSCG-B Archive Synchronized: %s", output_file)
    except OSError as e:
        logger.error("Failed to write TSCG-B archive: %s", e)
        return

    logger.info("Source size: %d bytes", len(json_bytes))
    logger.info("Compressed frame size: %d bytes", len(tscg_b_data))

if __name__ == "__main__":
    main()
