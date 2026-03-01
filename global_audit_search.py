import os

target_hash = "1e24d9c8bdc31e2dcac1e7aa6386447d9a63bc981ce154d14f594fc87177c727"
base_dir = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos"

print("--- Starting Global Sovereign Search ---")
for repo in os.listdir(base_dir):
    repo_path = os.path.join(base_dir, repo)
    if not os.path.isdir(repo_path):
        continue
    # print(f"Searching repo: {repo}")
    for root, dirs, files in os.walk(repo_path):
        if ".git" in root:
            continue

        # Search for thirrtc
        if "thirrtc" in root.lower():
            print(f"MATCH (path thirrtc): {root}")

        for file in files:
            if "thirrtc" in file.lower():
                print(f"MATCH (file thirrtc): {os.path.join(root, file)}")

            path = os.path.join(root, file)
            try:
                # Search for target hash
                if os.path.getsize(path) < 5 * 1024 * 1024:  # 5MB limit for speed
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if target_hash in content:
                            print(f"FOUND HASH ({target_hash}) in: {path}")
                        if "10.5281/zenodo" in content:
                            print(f"FOUND DOI in: {path}")
            except:
                pass
print("--- Global Search Complete ---")
