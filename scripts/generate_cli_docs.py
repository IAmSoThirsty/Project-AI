#!/usr/bin/env python3
"""Generate CLI documentation from Typer CLI commands.

This script auto-generates documentation for all CLI commands by capturing
the output of --help for each command and subcommand.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_cli_help(args: List[str]) -> Tuple[str, int]:
    """Run CLI command with --help and capture output.

    Args:
        args: Command arguments to pass to CLI.

    Returns:
        Tuple of (output, exit_code).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "app.cli"] + args + ["--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        return result.stdout, result.returncode
    except Exception as e:
        return f"Error: {e}", 1


def generate_command_doc(command: str, subcommands: List[str]) -> str:
    """Generate documentation for a command and its subcommands.

    Args:
        command: Main command name (or empty string for root).
        subcommands: List of subcommand names.

    Returns:
        Markdown documentation string.
    """
    doc = []

    # Root help
    if command:
        args = [command]
        output, code = run_cli_help(args)
        if code == 0:
            doc.append(f"### `{command}`\n")
            doc.append("```")
            doc.append(output)
            doc.append("```\n")
    else:
        args = []
        output, code = run_cli_help(args)
        if code == 0:
            doc.append("## Main CLI Help\n")
            doc.append("```")
            doc.append(output)
            doc.append("```\n")

    # Subcommands
    for subcmd in subcommands:
        if command:
            args = [command, subcmd]
            title = f"`{command} {subcmd}`"
        else:
            args = [subcmd]
            title = f"`{subcmd}`"

        output, code = run_cli_help(args)
        if code == 0:
            doc.append(f"### {title}\n")
            doc.append("```")
            doc.append(output)
            doc.append("```\n")

    return "\n".join(doc)


def main():
    """Generate CLI documentation."""
    print("Generating CLI documentation...")

    # Define command structure
    commands = {
        "": [],  # Root commands (shown in main help)
        "user": ["example"],
        "memory": ["example"],
        "learning": ["example"],
        "plugin": ["example"],
        "system": ["example"],
        "ai": ["example"],
    }

    # Generate documentation
    docs = [
        "# CLI Command Reference\n",
        "This documentation is auto-generated from CLI help output.\n",
        "**Last updated:** Run `python scripts/generate_cli_docs.py` to regenerate.\n",
        "---\n",
    ]

    # Root help first
    docs.append(generate_command_doc("", []))

    # Then each command group
    for cmd, subcmds in commands.items():
        if cmd:  # Skip root (already done)
            docs.append(generate_command_doc(cmd, subcmds))

    # Write to file
    output_path = Path(__file__).parent.parent / "docs" / "cli" / "commands.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("\n".join(docs))

    print(f"✓ Documentation generated: {output_path}")


if __name__ == "__main__":
    main()
