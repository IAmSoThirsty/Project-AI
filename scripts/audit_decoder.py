# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / audit_decoder.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / audit_decoder.py

#
# COMPLIANCE: Regulator-Ready / UTF-8                                          #


import json
import zlib
import sys
import os

# Sovereign Metadata
# Date: 2026-03-10 | Time: 19:45 | Status: Active | Tier: Master

def decode_tscgb(file_path):
    """
    Decodes a Thirsty's Symbolic Compression Grammar — Binary (.tscgb) file.
    """
    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found.")
        return []

    records = []
    with open(file_path, 'rb') as f:
        while True:
            # Read 4-byte length prefix
            len_bytes = f.read(4)
            if not len_bytes:
                break
            
            length = int.from_bytes(len_bytes, byteorder='big')
            blob = f.read(length)
            
            try:
                # TSCG-B Simplified Decompression
                raw_json = zlib.decompress(blob)
                record = json.loads(raw_json)
                records.append(record)
            except Exception as e:
                print(f"FAILED TO DECODE RECORD: {e}")
    
    return records

if __name__ == "__main__":
    target = "audit_trail.tscgb" if len(sys.argv) < 2 else sys.argv[1]
    print(f"=== DECODING SOVEREIGN AUDIT TRAIL: {target} ===")
    
    audit_data = decode_tscgb(target)
    if audit_data:
        print(json.dumps(audit_data, indent=2))
        print(f"\n[SUCCESS] Decoded {len(audit_data)} records.")
    else:
        print("[INFO] No records found or decoding failed.")
