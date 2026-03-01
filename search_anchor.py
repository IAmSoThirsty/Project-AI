import os

target_hash = "1e24d9c8bdc31e2dcac1e7aa6386447d9a63bc981ce154d14f594fc87177c727"
search_dir = (
    r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\data"
)

for root, dirs, files in os.walk(search_dir):
    for file in files:
        path = os.path.join(root, file)
        try:
            with open(path, "rb") as f:
                content = f.read()
                if target_hash.encode() in content:
                    print(f"FOUND IN: {path}")
        except:
            pass
