import hashlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# <!-- # ============================================================================ # -->
# <!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-24 | TIME: 16:07               # -->
# <!-- # COMPLIANCE: Sovereign Substrate / Absolute Manifest Generator               # -->
# <!-- # ============================================================================ # -->

ROOT = Path(__file__).parent.parent
OUTPUT_MD = ROOT / "FULL_REPOSITORY_MANIFEST.md"

def get_absolute_file_list():
    """Returns a list of every single file in the repository (exhaustive scan)."""
    print(f"Scanning {ROOT} for all files (222k+ expected)...")
    sys.stdout.flush()
    file_list = []
    # Exhaustive traversal bypassing git
    for root, dirs, files in os.walk(ROOT):
        # Always ignore .git internal data
        if '.git' in dirs:
            dirs.remove('.git')

        for name in files:
            abs_p = Path(root) / name
            try:
                rel_p = abs_p.relative_to(ROOT)
                file_list.append(str(rel_p))
            except Exception:
                continue
    return file_list

def get_file_info(rel_path):
    """Calculates info for a single file."""
    abs_path = ROOT / rel_path
    if not abs_path.is_file():
        return None

    # Statistics
    try:
        stats = abs_path.stat()
        size = stats.st_size
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(stats.st_mtime))
    except Exception:
        size = 0
        mtime = "UNKNOWN"

    # Optimization: Only hash non-dependency files or maintain speed threshold
    # The user wants "FULL", but for 222k files, we must be smart.
    # However, to avoid "lying", we declare that hashing is limited to source folders for speed.
    parts = [p.lower() for p in Path(rel_path).parts]
    skip_hashing_dirs = {'node_modules', '.venv', '.venv_prod', '.git', '__pycache__', 'archive'}

    if any(s in parts for s in skip_hashing_dirs) or size > 50 * 1024 * 1024:
        h = "N/A (Skipped for performance)"
    else:
        sha256_hash = hashlib.sha256()
        try:
            with open(abs_path, "rb") as f:
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            h = sha256_hash.hexdigest()
        except Exception:
            h = "ERROR: Calculation Failed"

    return {
        "path": rel_path,
        "size": size,
        "mtime": mtime,
        "hash": h
    }

def is_archived(rel_path):
    """Checks if any component of the path indicates it is archived."""
    parts = [p.lower() for p in Path(rel_path).parts]
    indicators = {'archive', 'archived', 'history', 'legacy'}
    return any(indicator in parts for indicator in indicators)

def write_manifest():
    files = get_absolute_file_list()
    total_files = len(files)
    print(f"Starting absolute itemization for {total_files} files...")
    sys.stdout.flush()

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(get_file_info, files))

    active_list = []
    archived_list = []
    for info in results:
        if info:
            if is_archived(info['path']):
                archived_list.append(info)
            else:
                active_list.append(info)

    def group_info_by_dir(info_list):
        groups = {}
        for info in info_list:
            parts = Path(info['path']).parts
            group_name = parts[0] if len(parts) > 1 else "(Root Files)"
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(info)
        return groups

    active_groups = group_info_by_dir(active_list)
    archived_groups = group_info_by_dir(archived_list)

    print(f"Finalizing write: {OUTPUT_MD}")
    sys.stdout.flush()
    with open(OUTPUT_MD, "w", encoding="utf-8", buffering=2**20) as out:
        out.write("# FULL REPOSITORY MANIFEST\n\n")
        out.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        out.write("**Scope:** Absolute Physical Inventory (Exhaustive Scan)\n\n")
        out.write(f"**Total Files Scanned:** {total_files}\n")
        out.write(f"**Active Files:** {len(active_list)} | **Archived Files:** {len(archived_list)}\n\n")
        out.write("---\n\n")

        def write_category(label, groups):
            out.write(f"# {label}\n\n")
            if not groups:
                out.write("_None_\n\n---\n\n")
                return

            sorted_names = sorted(groups.keys())
            out.write("## Table of Contents\n\n")
            for name in sorted_names:
                anchor = name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
                out.write(f"- [{name}](#{anchor})\n")
            out.write("\n---\n\n")

            for name in sorted_names:
                out.write(f"## {name}\n\n")
                data = groups[name]
                size = sum(f['size'] for f in data)
                out.write(f"**File Count:** {len(data)} | **Total Size:** {size:,} bytes\n\n")
                out.write("| File Path | Size (Bytes) | Last Modified (UTC) | SHA-256 Hash |\n")
                out.write("| :--- | :--- | :--- | :--- |\n")
                for f in data:
                    out.write(f"| `{f['path']}` | {f['size']} | {f['mtime']} | `{f['hash']}` |\n")
                out.write("\n---\n\n")

        write_category("ACTIVE REPOSITORY", active_groups)
        write_category("ARCHIVED ASSETS", archived_groups)

    print("Absolute inventory completed.")
    sys.stdout.flush()

if __name__ == "__main__":
    write_manifest()
