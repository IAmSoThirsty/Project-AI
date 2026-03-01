import hashlib

file_path = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\docs\governance\AGI_CHARTER.md"
with open(file_path, "rb") as f:
    content = f.read()
    file_hash = hashlib.sha256(content).hexdigest()
    print(f"Hash: {file_hash}")
