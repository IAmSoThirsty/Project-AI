#                                           [2026-03-04 21:15]
#                                          Productivity: Active

src_file = r"archive\src\app\core\ai_systems.py"
dest_file = r"src\app\core\ai_systems.py"

with open(src_file, encoding="utf-8") as f:
    lines = f.readlines()

atomic_start, atomic_end = -1, -1
for i, line in enumerate(lines):
    if line.startswith("def _atomic_write_json"):
        atomic_start = i
        break
for i in range(atomic_start + 1, len(lines)):
    line = lines[i]
    if line.startswith("def ") or line.startswith("# ==") and i > atomic_start:
        atomic_end = i - 1
        break

mem_start, mem_end = -1, -1
for i, line in enumerate(lines):
    if line.startswith("class MemoryExpansionSystem:"):
        mem_start = i
        break
for i in range(mem_start + 1, len(lines)):
    if lines[i].startswith("class ") or lines[i].startswith("# ===================="):
        mem_end = i - 1
        break
if mem_end == -1:
    mem_end = len(lines) - 1

atomic_code = "".join(lines[atomic_start : atomic_end + 1])

simple_atomic = """
import json
import tempfile
import hashlib

def _atomic_write_json(file_path: str, obj: Any) -> None:
    dirpath = os.path.dirname(file_path)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, file_path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
"""

mem_code = "".join(lines[mem_start : mem_end + 1])

with open(dest_file, "a", encoding="utf-8") as f:
    f.write("\n\n")
    f.write(simple_atomic)
    f.write("\n\n")
    f.write(mem_code)
print("Appended simple _atomic_write_json and MemoryExpansionSystem")
