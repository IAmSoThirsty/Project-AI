# (Substrate Tensor Debugger)             [2026-04-09 04:26]
#                                          Status: Active


import sys
try:
    import torch
    print(f"Torch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
