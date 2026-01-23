"""
Extract ZIP archive files while preserving UNIX file permissions.

This module provides a function to extract files from ZIP archives and apply
the original UNIX file permissions from the zip file entries to the extracted
files on the filesystem.

Usage:
    from pathlib import Path
    from extract_with_permissions import extract_with_permissions

    # Extract all files from archive.zip to /destination/path
    extracted_files = extract_with_permissions("archive.zip", "/destination/path")

    # With Path objects
    extracted_files = extract_with_permissions(
        Path("archive.zip"),
        Path("/destination/path")
    )

Returns:
    A list of Path objects representing all extracted file paths.
"""

import logging
import os
from pathlib import Path
from zipfile import BadZipFile, ZipFile  # noqa: F401

# Configure logging
logger = logging.getLogger(__name__)


def extract_with_permissions(zip_path, destination):
    """
    Extract all files from a ZIP archive and apply original UNIX permissions.

    This function extracts all files from a ZIP archive to a specified destination
    directory. If UNIX file permissions are stored in the ZIP file entries, they
    are applied to the extracted files. If chmod fails for any file, a warning is
    logged but extraction continues.

    Args:
        zip_path (str or Path): Path to the ZIP archive file
        destination (str or Path): Directory where files should be extracted

    Returns:
        list[Path]: List of Path objects for all extracted files

    Raises:
        FileNotFoundError: If the ZIP archive does not exist
        BadZipFile: If the file is not a valid ZIP archive
    """
    # Convert to Path objects for consistent handling
    zip_path = Path(zip_path)
    destination = Path(destination)

    # Validate that the ZIP file exists
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP archive not found: {zip_path}")

    # Create destination directory if it doesn't exist
    destination.mkdir(parents=True, exist_ok=True)

    extracted_files = []

    with ZipFile(zip_path, 'r') as zip_file:
        for zip_info in zip_file.infolist():
            # Extract the file
            extracted_path = zip_file.extract(zip_info, destination)
            extracted_file_path = Path(extracted_path)
            extracted_files.append(extracted_file_path)

            # Check if the entry has UNIX permission information
            # The external_attr field stores file attributes from the creating system
            # For UNIX systems, permissions are in the high 16 bits
            unix_permissions = zip_info.external_attr >> 16

            # Only apply permissions if they exist (non-zero) and the extracted
            # path is a file (not a directory)
            if unix_permissions and extracted_file_path.is_file():
                try:
                    os.chmod(extracted_file_path, unix_permissions)
                    logger.debug(
                        f"Applied permissions {oct(unix_permissions)} to {extracted_file_path}"
                    )
                except (OSError, PermissionError) as e:
                    # Log warning but continue with other files
                    logger.warning(
                        f"Failed to apply permissions to {extracted_file_path}: {e}"
                    )

    return extracted_files
