# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / sovereign_wrap.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / sovereign_wrap.py

import hashlib
import json
import os
import zlib
from datetime import datetime
from pathlib import Path



               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# DIALECT: TSCG-B / Sovereign-Wrapper                                         #




class SovereignWrap:
    """
    Sovereign TSCG-B Binary Wrapper.
    Encapsulates floors into symbolic binary blobs.
    """
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.output_file = self.root_dir / "sovereign_core.tscgb"
        self.registry = {}

    def _get_file_hash(self, file_path: Path) -> str:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def wrap_floor(self, floor_path: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ENCAPSULATING FLOOR: {floor_path}")
        target = self.root_dir / floor_path
        if not target.exists():
            print(f"  ERROR: Floor {floor_path} not found.")
            return

        for p in target.rglob("*"):
            if p.is_file() and p.suffix != ".tscgb":
                self._add_to_blob(p)

    def _add_to_blob(self, file_path: Path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            # Simulated TSCG-B Compression (High Level)
            compressed = zlib.compress(data, level=9)

            rel_path = file_path.relative_to(self.root_dir)
            self.registry[str(rel_path)] = {
                "size_raw": len(data),
                "size_compressed": len(compressed),
                "hash": self._get_file_hash(file_path)
            }

            # Write to binary blob
            with open(self.output_file, "ab") as f_out:
                # [4-byte NAME_LEN] + [NAME] + [4-byte DATA_LEN] + [DATA]
                name_bytes = str(rel_path).encode("utf-8")
                f_out.write(len(name_bytes).to_bytes(4, byteorder="big"))
                f_out.write(name_bytes)
                f_out.write(len(compressed).to_bytes(4, byteorder="big"))
                f_out.write(compressed)

        except Exception as e:
            print(f"  FAILED to wrap {file_path}: {e}")

    def finalize(self):
        # Write registry at the end
        reg_bytes = json.dumps(self.registry).encode("utf-8")
        with open(self.output_file, "ab") as f:
            f.write(len(reg_bytes).to_bytes(4, byteorder="big"))
            f.write(reg_bytes)
            f.write(b"TSCG-B-END")

        total_raw = sum(r["size_raw"] for r in self.registry.values())
        total_comp = sum(r["size_compressed"] for r in self.registry.values())
        ratio = (1 - (total_comp / total_raw)) * 100 if total_raw > 0 else 0
        
        print(f"\n--- ENCAPSULATION COMPLETE ---")
        print(f"  Files Wrapped: {len(self.registry)}")
        print(f"  Raw Size: {total_raw / 1024:.2f} KB")
        print(f"  TSCG-B Size: {total_comp / 1024:.2f} KB")
        print(f"  Reduction: {ratio:.2f}%")
        print(f"  Forensic Anchor: {self.output_file}")


if __name__ == "__main__":
    wrapper = SovereignWrap()
    # Clear existing blob
    if wrapper.output_file.exists():
        os.remove(wrapper.output_file)
    wrapper.wrap_floor("src")
    wrapper.wrap_floor("docs")
    # wrapper.wrap_floor("scripts") # Skip scripts to avoid recursion if running from scripts
    wrapper.finalize()
