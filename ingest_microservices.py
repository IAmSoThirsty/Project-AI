# (Microservice Ingestion Gateway)           [2026-04-09 04:12]
#                                          Status: Active



import os
import subprocess

# The root directory of the Project-AI repository
PROJECT_AI_PATH = (
    r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI"
)
MICROSERVICES_DIR = os.path.join(PROJECT_AI_PATH, "microservices")

# Source directories containing the microservices
SOURCE_DIRS = [
    r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos",
    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\Integrationg Microservices",
]


def get_git_remote(repo_path):
    """Attempt to get the remote origin url of a git repository."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        if url:
            return url
    except subprocess.CalledProcessError:
        pass

    # If no remote, use local path as submodule source
    # Convert windows path to generic format for Git
    return repo_path.replace("\\", "/")


def discover_microservices():
    """Scan source directories for potential microservices."""
    repos = []

    # 1. Scan sovereign-repos for thirsty-lang-* and other specific standalone repos
    sovereign_dir = SOURCE_DIRS[0]
    if os.path.exists(sovereign_dir):
        for item in os.listdir(sovereign_dir):
            item_path = os.path.join(sovereign_dir, item)
            if (os.path.isdir(item_path) and not (item == "Project-AI" or item.startswith(".")) and 
                (item.startswith("thirsty-lang-") or item in [
                    "Cerberus",
                    "TTP",
                    "The_Triumvirate",
                    "Thirsty-Lang",
                    "Thirstys-Monolith",
                    "Thirstys-waterfall",
                ]) and os.path.exists(os.path.join(item_path, ".git"))):
                repos.append({"name": item, "path": item_path})

    # 2. Scan Desktop Integrationg Microservices
    integration_dir = SOURCE_DIRS[1]
    if os.path.exists(integration_dir):
        for item in os.listdir(integration_dir):
            item_path = os.path.join(integration_dir, item)
            if os.path.isdir(item_path) and not item.startswith(".") and os.path.exists(os.path.join(item_path, ".git")):
                repos.append({"name": item, "path": item_path})

    return repos


def add_submodule(repo_info):
    """Add a microservice as a git submodule."""
    name = repo_info["name"].replace(" ", "_")  # Sanitize name for target path
    source_path = repo_info["path"]
    target_rel_path = f"microservices/{name}"

    remote_url = get_git_remote(source_path)

    print(f"[*] Ingesting: {name}")
    print(f"    Source: {source_path}")
    print(f"    Remote: {remote_url}")
    print(f"    Target: {target_rel_path}")

    try:
        # Check if already added
        if os.path.exists(os.path.join(PROJECT_AI_PATH, target_rel_path)):
            print(f"    [SKIP] Already exists at {target_rel_path}")
            return True

        subprocess.run(
            [
                "git",
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                "--force",
                remote_url,
                target_rel_path,
            ],
            cwd=PROJECT_AI_PATH,
            capture_output=True,
            text=True,
            check=True,
        )
        print("    [SUCCESS] Submodule bonded.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] Failed to add submodule: {e.stderr}")
        return False


def main():
    print("--- Omniversal Microservice Subjugation: Phase 1 ---")

    # Ensure microservices directory exists
    if not os.path.exists(MICROSERVICES_DIR):
        os.makedirs(MICROSERVICES_DIR)
        print(f"Created unified ecosystem directory: {MICROSERVICES_DIR}")

    repos = discover_microservices()
    print(f"Identified {len(repos)} standalone repositories for ingestion.\n")

    success_count = 0
    for repo in repos:
        if add_submodule(repo):
            success_count += 1

    print("Phase 1 Execution Complete.")
    print(
        f"Successfully subjugated {success_count}/{len(repos)} microservices into Project-AI."
    )


if __name__ == "__main__":
    main()
