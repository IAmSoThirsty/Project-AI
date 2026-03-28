# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / ingest_microservices.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign-Native / UTF-8                                         #


import argparse
import os
import re
import shutil
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
            if (
                os.path.isdir(item_path)
                and not (item == "Project-AI" or item.startswith("."))
                and (
                    item.startswith("thirsty-lang-")
                    or item
                    in [
                        "Cerberus",
                        "TTP",
                        "The_Triumvirate",
                        "Thirsty-Lang",
                        "Thirstys-Monolith",
                        "Thirstys-waterfall",
                    ]
                )
                and os.path.exists(os.path.join(item_path, ".git"))
            ):
                repos.append({"name": item, "path": item_path})

    # 2. Scan Desktop Integrationg Microservices
    integration_dir = SOURCE_DIRS[1]
    if os.path.exists(integration_dir):
        for item in os.listdir(integration_dir):
            item_path = os.path.join(integration_dir, item)
            if (
                os.path.isdir(item_path)
                and not item.startswith(".")
                and os.path.exists(os.path.join(item_path, ".git"))
            ):
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


def remove_submodule(name: str) -> bool:
    """Unlink and delete a microservice submodule from the repository.

    Performs the three-step git submodule removal:
      1. ``git submodule deinit -f`` — de-registers the submodule.
      2. ``git rm -f`` — removes the working-tree entry and .gitmodules record.
      3. Deletes the cached module data under ``.git/modules/``.

    Args:
        name: The microservice name as used in the ``microservices/<name>`` path.

    Returns:
        True on success, False if any step fails.
    """
    sanitized_name = re.sub(r"[^\w\-]", "_", name)
    target_rel_path = f"microservices/{sanitized_name}"
    target_abs_path = os.path.join(PROJECT_AI_PATH, target_rel_path)
    git_modules_cache = os.path.join(
        PROJECT_AI_PATH, ".git", "modules", target_rel_path
    )

    print(f"[*] Unlinking: {sanitized_name}")
    print(f"    Target: {target_rel_path}")

    if not os.path.exists(target_abs_path):
        print(f"    [SKIP] Submodule path does not exist: {target_rel_path}")
        return False

    try:
        subprocess.run(
            ["git", "submodule", "deinit", "-f", target_rel_path],
            cwd=PROJECT_AI_PATH,
            capture_output=True,
            text=True,
            check=True,
        )
        print("    [OK] Submodule deinitialized.")
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] Failed to deinit submodule: {e.stderr}")
        return False

    try:
        subprocess.run(
            ["git", "rm", "-f", target_rel_path],
            cwd=PROJECT_AI_PATH,
            capture_output=True,
            text=True,
            check=True,
        )
        print("    [OK] Submodule removed from index and .gitmodules.")
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] Failed to git rm submodule: {e.stderr}")
        return False

    if os.path.exists(git_modules_cache):
        try:
            shutil.rmtree(git_modules_cache)
            print("    [OK] Cached module data deleted.")
        except OSError as e:
            print(f"    [ERROR] Failed to delete cached module data: {e}")
            return False

    print("    [SUCCESS] Submodule unlinked and deleted.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Manage Project-AI microservice submodules."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "ingest", help="Discover and ingest all microservices (default)."
    )

    remove_parser = subparsers.add_parser(
        "remove", help="Unlink and delete a microservice submodule."
    )
    remove_parser.add_argument("name", help="Name of the microservice to remove.")

    args = parser.parse_args()

    if args.command == "remove":
        print("--- Omniversal Microservice Liberation: Unlink & Delete ---")
        success = remove_submodule(args.name)
        if success:
            print("Unlink complete.")
        else:
            print("Unlink failed.")
        return

    # Default: ingest (args.command is None or "ingest")
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
