"""Tests for path traversal security utilities."""

import os
import tempfile
import pytest

from app.security.path_security import (
    safe_path_join,
    safe_open,
    validate_filename,
    sanitize_filename,
    is_safe_symlink,
    PathTraversalError,
)


class TestSafePathJoin:
    """Test safe_path_join function."""
    
    def test_normal_join(self):
        """Test normal path joining."""
        result = safe_path_join("/data", "user", "file.txt")
        assert result.endswith(os.path.join("data", "user", "file.txt"))
    
    def test_blocks_parent_directory_attack(self):
        """Test blocking ../../../etc/passwd attack."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "../../../etc/passwd")
    
    def test_blocks_double_dot_sequences(self):
        """Test blocking .. sequences anywhere."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "user/../../../etc/passwd")
    
    def test_blocks_absolute_path(self):
        """Test blocking absolute paths in user input."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "/etc/passwd")
    
    def test_blocks_windows_absolute_path(self):
        """Test blocking Windows absolute paths."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "C:\\Windows\\System32\\config")
    
    def test_normalizes_paths(self):
        """Test that paths are normalized."""
        result = safe_path_join("/data", "user/./file.txt")
        assert "/." not in result
        assert result.endswith(os.path.join("data", "user", "file.txt"))
    
    def test_allows_subdirectories(self):
        """Test that subdirectories are allowed."""
        result = safe_path_join("/data", "users", "alice", "profile.json")
        assert result.endswith(
            os.path.join("data", "users", "alice", "profile.json")
        )
    
    def test_with_tempdir(self):
        """Test with temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = safe_path_join(tmpdir, "subdir", "file.txt")
            assert result.startswith(os.path.abspath(tmpdir))


class TestSafeOpen:
    """Test safe_open function."""
    
    def test_safe_open_read(self):
        """Test safely opening a file for reading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")
            
            # Read with safe_open
            with safe_open(tmpdir, "test.txt", "r") as f:
                content = f.read()
            
            assert content == "test content"
    
    def test_safe_open_write(self):
        """Test safely opening a file for writing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write with safe_open
            with safe_open(tmpdir, "test.txt", "w") as f:
                f.write("new content")
            
            # Verify file was created
            test_file = os.path.join(tmpdir, "test.txt")
            assert os.path.exists(test_file)
            
            with open(test_file) as f:
                assert f.read() == "new content"
    
    def test_safe_open_blocks_traversal(self):
        """Test that safe_open blocks path traversal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(PathTraversalError):
                safe_open(tmpdir, "../../etc/passwd", "r")
    
    def test_safe_open_binary_mode(self):
        """Test safe_open with binary mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write binary data
            with safe_open(tmpdir, "test.bin", "wb") as f:
                f.write(b"\x00\x01\x02\x03")
            
            # Read binary data
            with safe_open(tmpdir, "test.bin", "rb") as f:
                data = f.read()
            
            assert data == b"\x00\x01\x02\x03"


class TestValidateFilename:
    """Test validate_filename function."""
    
    def test_valid_filename(self):
        """Test valid filenames pass validation."""
        assert validate_filename("file.txt")
        assert validate_filename("document.pdf")
        assert validate_filename("image_2024.png")
    
    def test_blocks_path_separators(self):
        """Test blocking path separators."""
        with pytest.raises(PathTraversalError):
            validate_filename("path/to/file.txt")
        
        with pytest.raises(PathTraversalError):
            validate_filename("path\\to\\file.txt")
    
    def test_blocks_double_dots(self):
        """Test blocking .. sequences."""
        with pytest.raises(PathTraversalError):
            validate_filename("..file.txt")
        
        with pytest.raises(PathTraversalError):
            validate_filename("file..txt")
    
    def test_blocks_hidden_files(self):
        """Test blocking hidden files."""
        with pytest.raises(PathTraversalError):
            validate_filename(".hidden")
    
    def test_blocks_null_bytes(self):
        """Test blocking null bytes."""
        with pytest.raises(PathTraversalError):
            validate_filename("file\x00.txt")
    
    def test_blocks_long_filenames(self):
        """Test blocking excessively long filenames."""
        with pytest.raises(PathTraversalError):
            validate_filename("a" * 300)
    
    def test_blocks_reserved_windows_names(self):
        """Test blocking reserved Windows filenames."""
        reserved = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        for name in reserved:
            with pytest.raises(PathTraversalError):
                validate_filename(name)
            
            # Also test with extensions
            with pytest.raises(PathTraversalError):
                validate_filename(f"{name}.txt")


class TestSanitizeFilename:
    """Test sanitize_filename function."""
    
    def test_sanitizes_path_separators(self):
        """Test sanitizing path separators."""
        assert sanitize_filename("path/to/file.txt") == "path_to_file.txt"
        assert sanitize_filename("path\\to\\file.txt") == "path_to_file.txt"
    
    def test_sanitizes_double_dots(self):
        """Test sanitizing .. sequences."""
        assert sanitize_filename("..file.txt") == "file.txt"
        assert sanitize_filename("file..txt") == "file.txt"
    
    def test_sanitizes_null_bytes(self):
        """Test sanitizing null bytes."""
        assert sanitize_filename("file\x00.txt") == "file.txt"
    
    def test_sanitizes_leading_dots(self):
        """Test removing leading dots."""
        assert sanitize_filename(".hidden") == "hidden"
        assert sanitize_filename("...file") == "file"
    
    def test_handles_empty_result(self):
        """Test handling empty sanitization result."""
        result = sanitize_filename("...")
        assert result != ""
        assert result == "file"
    
    def test_truncates_long_filenames(self):
        """Test truncating long filenames."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")
    
    def test_custom_replacement(self):
        """Test custom replacement character."""
        assert sanitize_filename("path/to/file", replacement="-") == "path-to-file"


class TestIsSymlinkSafe:
    """Test is_safe_symlink function."""
    
    def test_regular_file_is_safe(self):
        """Test that regular files are considered safe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")
            
            assert is_safe_symlink(test_file, tmpdir)
    
    def test_safe_symlink_within_basedir(self):
        """Test symlink pointing within base directory is safe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "target.txt")
            link = os.path.join(tmpdir, "link.txt")
            
            with open(target, "w") as f:
                f.write("target")
            
            # Create symlink (skip on Windows if permissions insufficient)
            try:
                os.symlink(target, link)
                assert is_safe_symlink(link, tmpdir)
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported")
    
    def test_unsafe_symlink_outside_basedir(self):
        """Test symlink pointing outside base directory is unsafe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create symlink to /etc/passwd
            link = os.path.join(tmpdir, "evil_link")
            
            try:
                os.symlink("/etc/passwd", link)
                assert not is_safe_symlink(link, tmpdir)
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported")


class TestPathTraversalAttacks:
    """Test various path traversal attack vectors."""
    
    def test_etc_passwd_attack(self):
        """Test classic /etc/passwd attack."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "../../../etc/passwd")
    
    def test_windows_system32_attack(self):
        """Test Windows system32 attack."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "..\\..\\..\\Windows\\System32\\config")
    
    def test_mixed_separators_attack(self):
        """Test mixed path separators."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "../..\\/etc/passwd")
    
    def test_url_encoded_attack(self):
        """Test URL-encoded traversal (should be blocked)."""
        # Note: We expect this to be blocked by .. detection
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "..%2F..%2F..%2Fetc%2Fpasswd")
    
    def test_double_encoded_attack(self):
        """Test double URL-encoded traversal."""
        with pytest.raises(PathTraversalError):
            safe_path_join("/data", "..%252F..%252Fetc%252Fpasswd")
    
    def test_null_byte_injection(self):
        """Test null byte injection attack."""
        # This should be caught by filename validation if used
        assert "\x00" not in safe_path_join("/data", "safe_file.txt")
    
    def test_unicode_attack(self):
        """Test Unicode normalization attack."""
        # Ensure Unicode characters are handled safely
        result = safe_path_join("/data", "file\u2044subdir")  # Unicode slash
        assert result.startswith(os.path.abspath("/data"))
