# ============================================================================ #
#                                           [2026-03-18 12:15]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 12:15             #
# COMPLIANCE: Sovereign Substrate / sovereign_indexer.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign-Native / TSCG-B Indexer v1.0                           #

"""
Sovereign Indexer (TSCG-B)
Generates a cryptographically sealed, high-performance binary manifest of the repository.
Optimized for Agentic autonomy and resource minimization.
"""

import os
import json
import zlib
import hashlib
import binascii
import logging
from datetime import datetime, timezone

# Setup Master-Tier Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("SovereignIndexer")

class SovereignIndexer:
    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.output_file = os.path.join(self.root_dir, "SOVEREIGN_MANIFEST.tscgb")
        self.exclusions = {
            '.git', '.venv', 'node_modules', '__pycache__', 
            '.pytest_cache', '.mypy_cache', '.antigravity',
            'bin', 'obj', 'dist', 'build'
        }
        logger.info("Indexer initialized for: %s", self.root_dir)

    def should_skip(self, path):
        """Determines if a path should be excluded from the index."""
        parts = path.split(os.sep)
        return any(ex in parts for ex in self.exclusions)

    def generate_index(self):
        """Crawls the repo and generates the symbolic state dictionary."""
        repo_state = {
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "root": self.root_dir,
            "files": []
        }

        logger.info("Crawling repository for file manifest...")
        for root, _, files in os.walk(self.root_dir):
            if self.should_skip(root):
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.root_dir)
                
                try:
                    stats = os.stat(file_path)
                    repo_state["files"].append({
                        "p": rel_path,      # Path
                        "s": stats.st_size, # Size
                        "m": int(stats.st_mtime) # Modified Time
                    })
                except OSError as e:
                    logger.warning("Could not index %s: %s", rel_path, e)

        return repo_state

    def seal_manifest(self, repo_state):
        """
        Applies TSCG-B v1.0 Binary Seal:
        MAGIC | PROTO_VER | SD_VER | CONST_VER | FLAGS | PAY_LEN | PAYLOAD | CRC32 | SHA256
        """
        logger.info("Sealing manifest with TSCG-B v1.0 protocol...")
        
        # 1. Symbolic Contextual Compression (zlib-9)
        json_data = json.dumps(repo_state, separators=(',', ':'))
        payload = zlib.compress(json_data.encode('utf-8'), level=9)

        # 2. Build Header (TSCG-B2 Expansion: 4-byte payload length)
        magic = b'TSGB'
        proto_ver = b'\x02'  # Proto v2 for 4-byte len support
        sd_ver = b'\x01'
        const_ver = b'\x01'
        flags = b'\x00'
        pay_len = len(payload).to_bytes(4, 'big') # Extended to 4 bytes

        frame_body = magic + proto_ver + sd_ver + const_ver + flags + pay_len + payload

        # 3. Integrity Seals
        crc = binascii.crc32(frame_body).to_bytes(4, 'big')
        sha = hashlib.sha256(frame_body).digest()

        full_binary = frame_body + crc + sha
        
        with open(self.output_file, 'wb') as f:
            f.write(full_binary)
            
        logger.info("Sovereign Manifest Sealed: %s", self.output_file)
        logger.info("Final Size: %d bytes (vs %d bytes JSON)", len(full_binary), len(json_data))
        return self.output_file

if __name__ == "__main__":
    indexer = SovereignIndexer(".")
    state = indexer.generate_index()
    indexer.seal_manifest(state)
