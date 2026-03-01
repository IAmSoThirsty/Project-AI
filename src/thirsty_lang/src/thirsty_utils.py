#!/usr/bin/env python3
"""
Thirsty-lang Python Utilities
Common utility functions for Thirsty-lang Python implementation
"""

import os
import sys


def read_file(filename: str) -> str:
    """
    Read a Thirsty-lang source file

    Args:
        filename: Path to the file

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    with open(filename, encoding="utf-8") as f:
        return f.read()


def get_file_extension(filename: str) -> str:
    """
    Get the file extension

    Args:
        filename: Path to the file

    Returns:
        File extension (e.g., '.thirsty')
    """
    return os.path.splitext(filename)[1]


def is_thirsty_file(filename: str) -> bool:
    """
    Check if a file is a Thirsty-lang file

    Args:
        filename: Path to the file

    Returns:
        True if file has Thirsty-lang extension
    """
    valid_extensions = [".thirsty", ".thirstyplus", ".thirstyplusplus", ".thirstofgods"]
    return get_file_extension(filename).lower() in valid_extensions


def find_thirsty_files(directory: str) -> list[str]:
    """
    Find all Thirsty-lang files in a directory

    Args:
        directory: Path to search

    Returns:
        List of Thirsty-lang file paths
    """
    thirsty_files = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if is_thirsty_file(filepath):
                thirsty_files.append(filepath)
    return thirsty_files


def format_error(message: str, line_num: int | None = None) -> str:
    """
    Format an error message

    Args:
        message: Error message
        line_num: Optional line number

    Returns:
        Formatted error string
    """
    if line_num:
        return f"Error on line {line_num}: {message}"
    return f"Error: {message}"


def print_banner(title: str):
    """
    Print a formatted banner

    Args:
        title: Banner title
    """
    width = 60
    border = "═" * (width - 2)
    print(f"╔{border}╗")
    padding = (width - len(title) - 2) // 2
    print(f"║{' ' * padding}{title}{' ' * (width - len(title) - padding - 2)}║")
    print(f"╚{border}╝")


def check_version() -> str:
    """
    Get Python and Thirsty-lang version info

    Returns:
        Version string
    """
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    return f"Python {python_version} | Thirsty-lang 1.0.0"


if __name__ == "__main__":
    # Test utilities
    print_banner("Thirsty-lang Python Utilities")
    print(f"\n{check_version()}\n")
