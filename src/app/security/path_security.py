"""Path traversal security utilities.

This module provides secure path validation and joining to prevent
directory traversal attacks across all file operations.

Security Features:
- Validates paths stay within allowed base directories
- Blocks .. sequences and absolute path attacks
- Normalizes paths to prevent bypasses
- Provides secure file opening with automatic validation
- Logs all path validation failures

Usage:
    from app.security.path_security import safe_path_join, safe_open
    
    # Safe path joining
    safe_path = safe_path_join(data_dir, user_input)
    
    # Safe file opening
    with safe_open(data_dir, user_filename, 'r') as f:
        content = f.read()
"""

import logging
import os
from pathlib import Path
from typing import Optional, Literal

logger = logging.getLogger(__name__)


class PathTraversalError(ValueError):
    """Raised when path traversal attack is detected."""
    pass


def safe_path_join(base_dir: str, *user_paths: str) -> str:
    """Securely join paths and validate they stay within base directory.
    
    Args:
        base_dir: Trusted base directory path
        *user_paths: User-controlled path components to join
        
    Returns:
        Normalized absolute path within base_dir
        
    Raises:
        PathTraversalError: If path traversal is detected
        
    Example:
        >>> safe_path_join("/data", "user", "profile.json")
        '/data/user/profile.json'
        >>> safe_path_join("/data", "../../../etc/passwd")
        PathTraversalError: Path traversal detected
    """
    # Normalize base directory
    base_abs = os.path.abspath(base_dir)
    
    # Join and normalize the full path
    full_path = os.path.normpath(os.path.join(base_abs, *user_paths))
    
    # Convert to absolute path
    full_abs = os.path.abspath(full_path)
    
    # Ensure result is still under base directory
    # Use os.path.commonpath to handle edge cases on Windows
    try:
        common = os.path.commonpath([base_abs, full_abs])
        if common != base_abs:
            logger.warning(
                "Path traversal blocked: %s escapes base %s",
                user_paths, base_dir
            )
            raise PathTraversalError(
                f"Path traversal detected: {user_paths} escapes {base_dir}"
            )
    except ValueError:
        # Different drives on Windows
        logger.warning(
            "Path traversal blocked: %s on different drive from %s",
            user_paths, base_dir
        )
        raise PathTraversalError(
            f"Path traversal detected: different drive"
        )
    
    # Additional check: block any .. sequences in user input
    for user_path in user_paths:
        if ".." in str(user_path):
            logger.warning(
                "Path traversal blocked: '..' sequence in %s",
                user_path
            )
            raise PathTraversalError(
                f"Invalid path: '..' sequences not allowed"
            )
    
    # Block absolute paths in user input (Unix and Windows)
    for user_path in user_paths:
        user_str = str(user_path)
        if user_str.startswith('/') or user_str.startswith('\\'):
            logger.warning(
                "Path traversal blocked: absolute path %s",
                user_path
            )
            raise PathTraversalError(
                f"Invalid path: absolute paths not allowed"
            )
        # Block Windows drive letters (C:, D:, etc.)
        if len(user_str) >= 2 and user_str[1] == ':':
            logger.warning(
                "Path traversal blocked: drive letter in %s",
                user_path
            )
            raise PathTraversalError(
                f"Invalid path: drive letters not allowed"
            )
    
    return full_abs


def safe_open(
    base_dir: str,
    user_path: str,
    mode: Literal['r', 'w', 'a', 'rb', 'wb', 'ab'] = 'r',
    encoding: Optional[str] = 'utf-8',
    **kwargs
):
    """Safely open a file with path traversal protection.
    
    Args:
        base_dir: Trusted base directory
        user_path: User-controlled file path (relative to base_dir)
        mode: File open mode
        encoding: File encoding (None for binary modes)
        **kwargs: Additional arguments passed to open()
        
    Returns:
        File object
        
    Raises:
        PathTraversalError: If path traversal is detected
        
    Example:
        >>> with safe_open("/data", "user/config.json", "r") as f:
        ...     data = json.load(f)
    """
    safe_path = safe_path_join(base_dir, user_path)
    
    # For binary modes, don't use encoding
    if 'b' in mode:
        return open(safe_path, mode, **kwargs)
    else:
        return open(safe_path, mode, encoding=encoding, **kwargs)


def validate_filename(filename: str, max_length: int = 255) -> bool:
    """Validate that filename is safe.
    
    Args:
        filename: Filename to validate (not path)
        max_length: Maximum allowed filename length
        
    Returns:
        True if filename is safe
        
    Raises:
        PathTraversalError: If filename is invalid
    """
    # Block path separators
    if '/' in filename or '\\' in filename:
        raise PathTraversalError(
            "Filename cannot contain path separators"
        )
    
    # Block .. sequences
    if '..' in filename:
        raise PathTraversalError(
            "Filename cannot contain '..' sequences"
        )
    
    # Block hidden files on Unix
    if filename.startswith('.'):
        raise PathTraversalError(
            "Hidden filenames not allowed"
        )
    
    # Block null bytes
    if '\x00' in filename:
        raise PathTraversalError(
            "Filename cannot contain null bytes"
        )
    
    # Check length
    if len(filename) > max_length:
        raise PathTraversalError(
            f"Filename too long (max {max_length} characters)"
        )
    
    # Block reserved Windows filenames
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                'COM4', 'LPT1', 'LPT2', 'LPT3'}
    name_upper = filename.upper().split('.')[0]
    if name_upper in reserved:
        raise PathTraversalError(
            f"Reserved filename: {filename}"
        )
    
    return True


def sanitize_filename(filename: str, replacement: str = '_') -> str:
    """Sanitize a filename by replacing dangerous characters.
    
    Args:
        filename: Filename to sanitize
        replacement: Character to replace dangerous chars with
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    sanitized = filename.replace('/', replacement).replace('\\', replacement)
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Remove .. sequences
    while '..' in sanitized:
        sanitized = sanitized.replace('..', '.')
    
    # Remove leading dots
    sanitized = sanitized.lstrip('.')
    
    # Ensure not empty
    if not sanitized:
        sanitized = 'file'
    
    # Truncate to reasonable length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized


def is_safe_symlink(link_path: str, base_dir: str) -> bool:
    """Check if a symlink target is within the allowed base directory.
    
    Args:
        link_path: Path to the symlink
        base_dir: Allowed base directory
        
    Returns:
        True if symlink target is safe, False otherwise
    """
    if not os.path.islink(link_path):
        return True
    
    try:
        target = os.readlink(link_path)
        # Resolve relative to link's directory
        link_dir = os.path.dirname(link_path)
        target_abs = os.path.abspath(os.path.join(link_dir, target))
        
        # Check if target is within base_dir
        base_abs = os.path.abspath(base_dir)
        common = os.path.commonpath([base_abs, target_abs])
        return common == base_abs
    except (OSError, ValueError):
        return False
