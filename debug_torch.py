# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / debug_torch.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / debug_torch.py


import sys
try:
    import torch
    print(f"Torch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
