# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / organize_yggdrasil.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / organize_yggdrasil.py

#
# COMPLIANCE: Sovereign Substrate / organize_yggdrasil.py


import os
import shutil

root = "trunk/leaf"
groups = [f"leaf_group_{i:02d}" for i in range(1, 16)]

# Create groups
for g in groups:
    path = os.path.join(root, g)
    if not os.path.exists(path):
        os.makedirs(path)

# List all current child directories that are NOT groups
children = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and d not in groups]

# Move them into groups (distribute roughly 4-5 per group if there are ~60 submodules)
for i, child in enumerate(children):
    group_idx = i % 15
    src = os.path.join(root, child)
    dst = os.path.join(root, groups[group_idx], child)
    
    # Handle move
    if os.path.exists(src):
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"Error moving {src}: {e}")

print(f"Substrate fractalization complete. Organized {len(children)} kernels into 15 groups.")
