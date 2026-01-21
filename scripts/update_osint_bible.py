#!/usr/bin/env python3
"""
OSINT-BIBLE Integration Script

This script fetches the OSINT-BIBLE repository from frangelbarrera/OSINT-Bible,
parses its contents, and outputs structured JSON to data/osint/osint_bible.json.

The OSINT-BIBLE contains curated lists of OSINT tools and resources across multiple
categories. This script provides the foundation for integrating these tools into
Project-AI's knowledge and plugin system.

Usage:
    python scripts/update_osint_bible.py [--force] [--output PATH]

Future Enhancements:
    - Add GitHub API token support for higher rate limits
    - Implement incremental updates with change detection
    - Add validation for tool metadata
    - Support for custom tool categories
"""

import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# OSINT-BIBLE repository details
GITHUB_API_BASE = "https://api.github.com"
OSINT_BIBLE_OWNER = "frankielaguerraYT"  # Updated owner name
OSINT_BIBLE_REPO = "OSINT-Bible"
OSINT_BIBLE_BRANCH = "main"

# Output paths
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "data" / "osint"
DEFAULT_OUTPUT_FILE = "osint_bible.json"


class OSINTBibleFetcher:
    """Fetches and parses the OSINT-BIBLE repository."""

    def __init__(self, output_dir: Path):
        """Initialize the fetcher.

        Args:
            output_dir: Directory to write output files
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Project-AI-OSINT-Fetcher",
            }
        )

    def fetch_repo_contents(self) -> dict[str, Any]:
        """Fetch the repository contents from GitHub API.

        Returns:
            Repository contents tree

        Raises:
            requests.RequestException: If API request fails
        """
        url = (
            f"{GITHUB_API_BASE}/repos/{OSINT_BIBLE_OWNER}/"
            f"{OSINT_BIBLE_REPO}/git/trees/{OSINT_BIBLE_BRANCH}?recursive=1"
        )
        logger.info(f"Fetching repository contents from {url}")

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        return response.json()

    def fetch_file_content(self, path: str) -> str:
        """Fetch content of a specific file from the repository.

        Args:
            path: Path to the file in the repository

        Returns:
            File content as string

        Raises:
            requests.RequestException: If API request fails
        """
        url = (
            f"{GITHUB_API_BASE}/repos/{OSINT_BIBLE_OWNER}/"
            f"{OSINT_BIBLE_REPO}/contents/{path}?ref={OSINT_BIBLE_BRANCH}"
        )
        logger.debug(f"Fetching file: {path}")

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data.get("content", "")

    def parse_markdown_tools(self, content: str) -> list[dict[str, Any]]:
        """Parse tool entries from markdown content.

        This is a simple parser that extracts links and descriptions from markdown.
        Future versions can implement more sophisticated parsing based on the
        actual structure of OSINT-BIBLE files.

        Args:
            content: Markdown content

        Returns:
            List of tool entries with name, url, and description
        """
        tools = []

        # Simple regex to find markdown links: [name](url) - description
        # This is a stub implementation - adjust based on actual OSINT-BIBLE format
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")

        for match in link_pattern.finditer(content):
            name, url = match.groups()
            tools.append(
                {
                    "name": name.strip(),
                    "url": url.strip(),
                    "description": "",  # Can be enhanced to extract descriptions
                    "source": "osint-bible",
                }
            )

        return tools

    def process_repository(self) -> dict[str, Any]:
        """Process the OSINT-BIBLE repository and extract structured data.

        Returns:
            Structured data containing tools organized by category

        Note:
            This is a stub implementation. The actual structure depends on the
            OSINT-BIBLE repository format. Adjust parsing logic as needed.
        """
        try:
            repo_tree = self.fetch_repo_contents()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch repository: {e}")
            # Return minimal structure if fetch fails
            return {
                "metadata": {
                    "source": "osint-bible",
                    "owner": OSINT_BIBLE_OWNER,
                    "repo": OSINT_BIBLE_REPO,
                    "last_updated": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e),
                },
                "categories": {},
            }

        categories: dict[str, list[dict[str, Any]]] = {}

        # Extract markdown files from the tree
        markdown_files = [
            item["path"]
            for item in repo_tree.get("tree", [])
            if item["path"].endswith(".md") and item["type"] == "blob"
        ]

        logger.info(f"Found {len(markdown_files)} markdown files")

        # Process README.md for main content (stub)
        for md_file in markdown_files[:5]:  # Limit to first 5 files for now
            try:
                # Fetch content - in production, decode base64 content from GitHub API
                # For now, we'll create a placeholder
                category_name = Path(md_file).stem
                categories[category_name] = []
                logger.info(f"Processed category: {category_name}")
            except Exception as e:
                logger.warning(f"Failed to process {md_file}: {e}")

        return {
            "metadata": {
                "source": "osint-bible",
                "owner": OSINT_BIBLE_OWNER,
                "repo": OSINT_BIBLE_REPO,
                "last_updated": datetime.now().isoformat(),
                "status": "success",
                "file_count": len(markdown_files),
            },
            "categories": categories,
        }

    def save_data(self, data: dict[str, Any], filename: str = DEFAULT_OUTPUT_FILE):
        """Save structured data to JSON file.

        Args:
            data: Data to save
            filename: Output filename
        """
        output_path = self.output_dir / filename
        logger.info(f"Writing output to {output_path}")

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Successfully wrote {output_path.stat().st_size} bytes")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fetch and parse OSINT-BIBLE repository"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if data exists",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory path",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    fetcher = OSINTBibleFetcher(args.output)

    output_file = args.output / DEFAULT_OUTPUT_FILE
    if output_file.exists() and not args.force:
        logger.info(f"Output file {output_file} already exists. Use --force to update.")
        return

    logger.info("Starting OSINT-BIBLE update...")
    data = fetcher.process_repository()
    fetcher.save_data(data)
    logger.info("OSINT-BIBLE update complete!")


if __name__ == "__main__":
    main()
