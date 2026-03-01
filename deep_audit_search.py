import os
import hashlib

target_hash = "1e24d9c8bdc31e2dcac1e7aa6386447d9a63bc981ce154d14f594fc87177c727"
search_roots = [
    r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\data",
    r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\docs",
    r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Thirsty-Lang",
]

print(f"--- Starting deep search for hash: {target_hash} ---")

for root_dir in search_roots:
    if not os.path.exists(root_dir):
        continue
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            try:
                if file.endswith(
                    (".json", ".md", ".txt", ".db", ".yml", ".yaml", ".py")
                ):
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        if target_hash in f.read():
                            print(f"FOUND (text): {path}")
                else:
                    with open(path, "rb") as f:
                        if target_hash.encode() in f.read():
                            print(f"FOUND (binary): {path}")
            except Exception as e:
                pass

print("--- Search complete ---")

print("\n--- Searching for DOI/Zenodo/Copyright ---")
keywords = ["Zenodo", "10.5281/zenodo", "Copyright", "Jeremy Karrick", "©"]
for root_dir in search_roots:
    if not os.path.exists(root_dir):
        continue
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".md", ".txt", ".yml", ".yaml", ".py")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for kw in keywords:
                            if kw.lower() in content.lower():
                                print(f"MATCH ({kw}): {path}")
                except:
                    pass
