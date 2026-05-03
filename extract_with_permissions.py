"""extract_with_permissions — ZIP extraction that preserves UNIX file permissions.

Standard :mod:`zipfile` ignores the UNIX permission bits stored in
``ZipInfo.external_attr``.  This module provides a single convenience function
that restores those bits after extraction, making it safe for use on POSIX
systems where permission fidelity matters (e.g. executable scripts, SSH keys).

Windows note: ``os.chmod`` is a no-op for most permission bits on Windows;
failures are silently swallowed so extraction always completes.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from zipfile import BadZipFile, ZipFile  # noqa: F401 – re-exported for callers

__all__ = ["extract_with_permissions"]

logger = logging.getLogger(__name__)


def extract_with_permissions(
    zip_path: str | os.PathLike,
    dest: str | os.PathLike,
) -> list[Path]:
    """Extract *zip_path* into *dest*, restoring UNIX permission bits.

    Parameters
    ----------
    zip_path:
        Path to the ZIP archive.  Accepts both :class:`str` and
        :class:`~pathlib.Path`.
    dest:
        Destination directory.  Created (including parents) if it does not
        exist.  Accepts both :class:`str` and :class:`~pathlib.Path`.

    Returns
    -------
    list[Path]
        Absolute paths of every file extracted (directories are excluded).

    Raises
    ------
    FileNotFoundError
        If *zip_path* does not exist, with the message
        ``"ZIP archive not found: <path>"``.
    zipfile.BadZipFile
        If *zip_path* is not a valid ZIP archive.
    """
    zip_path = Path(zip_path)
    dest = Path(dest)

    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP archive not found: {zip_path}")

    # Let BadZipFile propagate naturally — callers expect it.
    with ZipFile(zip_path, "r") as zf:
        dest.mkdir(parents=True, exist_ok=True)

        extracted: list[Path] = []

        for info in zf.infolist():
            # Skip directory entries — they are created implicitly below.
            if info.filename.endswith("/"):
                continue

            # Extract the member.
            out_path = dest / info.filename
            out_path.parent.mkdir(parents=True, exist_ok=True)

            with zf.open(info) as src, open(out_path, "wb") as dst:
                dst.write(src.read())

            # Restore UNIX permissions from the high 16 bits of external_attr.
            unix_perms = (info.external_attr >> 16) & 0xFFFF
            if unix_perms:
                try:
                    os.chmod(out_path, unix_perms)
                except OSError as exc:
                    # Non-fatal — log and continue so every file is extracted.
                    logger.warning(
                        "chmod failed for %s (mode=%o): %s", out_path, unix_perms, exc
                    )

            extracted.append(out_path)

    return extracted
