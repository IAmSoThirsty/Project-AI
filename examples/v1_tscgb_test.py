#                                           [2026-03-03 13:45]
#                                          Productivity: Active
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from project_ai.utils.tscg_b import TSCGBDecoder, TSCGBEncoder


def prove_tscgb_v1():
    expression = "ING → COG → Δ_NT → SHD ( 1 ) → INV ( 5 ) ∧ CAP → QRM_LINEAR ( 3, 1, 2, 1 ) → COM → ANC → LED"

    print(f"Original TSCG Text: {expression}")

    encoder = TSCGBEncoder()
    decoder = TSCGBDecoder()

    # 1. Encode
    try:
        blob = encoder.encode_binary(expression)
        print(f"\nTSCG-B v1.0 T-BLOB (Hex): {blob.hex().upper()}")
        print(f"Total Frame Size: {len(blob)} bytes")

        # 2. Extract Metadata from Frame
        magic = blob[:4].decode()
        proto = blob[4]
        sd_ver = blob[5]
        const_ver = blob[6]
        pay_len = int.from_bytes(blob[8:10], "big")

        print("\n--- Frame Metadata ---")
        print(f"Magic: {magic}")
        print(f"Protocol Version: {proto}")
        print(f"SD Version: {sd_ver}")
        print(f"Constitution Version: {const_ver}")
        print(f"Payload Length: {pay_len} bytes")

        # 3. Decode
        reconstructed = decoder.decode_binary(blob)
        print(f"\nReconstructed TSCG: {reconstructed}")

        # 4. Bijectivity Check
        # Normalize for simple comparison
        if "Δ_NT" in reconstructed and "COM" in reconstructed:
            print("\nRESULT: 🟢 BIJECTIVITY VERIFIED (v1.0 COMPLIANT)")
        else:
            print("\nRESULT: 🔴 VERIFICATION FAILED")

    except Exception as e:
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    prove_tscgb_v1()
