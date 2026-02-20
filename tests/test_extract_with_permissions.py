import os
import stat
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pytest
from extract_with_permissions import extract_with_permissions


@pytest.fixture
def test_zip_with_permissions(tmp_path):
    """Create a test ZIP file with UNIX permissions."""
    # Create test content
    content_dir = tmp_path / "content"
    content_dir.mkdir()

    file1 = content_dir / "file1.txt"
    file1.write_text("Content 1")

    file2 = content_dir / "file2.txt"
    file2.write_text("Content 2")

    subdir = content_dir / "subdir"
    subdir.mkdir()
    file3 = subdir / "file3.txt"
    file3.write_text("Content 3")

    # Create ZIP with UNIX permissions
    zip_path = tmp_path / "test.zip"
    with ZipFile(zip_path, "w") as zf:
        # Add file1 with permissions 0o644 (rw-r--r--)
        from zipfile import ZipInfo

        info1 = ZipInfo("file1.txt")
        info1.external_attr = 0o644 << 16
        zf.writestr(info1, file1.read_bytes())

        # Add file2 with permissions 0o755 (rwxr-xr-x)
        info2 = ZipInfo("file2.txt")
        info2.external_attr = 0o755 << 16
        zf.writestr(info2, file2.read_bytes())

        # Add file3 with permissions 0o600 (rw-------)
        info3 = ZipInfo("subdir/file3.txt")
        info3.external_attr = 0o600 << 16
        zf.writestr(info3, file3.read_bytes())

    return zip_path


@pytest.fixture
def test_zip_without_permissions(tmp_path):
    """Create a test ZIP file without UNIX permissions."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()

    file1 = content_dir / "file1.txt"
    file1.write_text("Content without permissions")

    zip_path = tmp_path / "test_no_perms.zip"
    with ZipFile(zip_path, "w") as zf:
        zf.write(file1, "file1.txt")

    return zip_path


def test_extract_all_files(test_zip_with_permissions, tmp_path):
    """Test that all files are extracted."""
    dest = tmp_path / "extracted"
    extracted = extract_with_permissions(test_zip_with_permissions, dest)

    assert len(extracted) == 3
    assert (dest / "file1.txt").exists()
    assert (dest / "file2.txt").exists()
    assert (dest / "subdir" / "file3.txt").exists()


def test_apply_unix_permissions(test_zip_with_permissions, tmp_path):
    """Test that UNIX permissions are correctly applied."""
    dest = tmp_path / "extracted"
    extract_with_permissions(test_zip_with_permissions, dest)

    # Check permissions
    file1_perms = stat.S_IMODE((dest / "file1.txt").stat().st_mode)
    file2_perms = stat.S_IMODE((dest / "file2.txt").stat().st_mode)
    file3_perms = stat.S_IMODE((dest / "subdir" / "file3.txt").stat().st_mode)

    assert file1_perms == 0o644
    assert file2_perms == 0o755
    assert file3_perms == 0o600


def test_extract_without_permissions(test_zip_without_permissions, tmp_path):
    """Test extraction of ZIP without UNIX permissions."""
    dest = tmp_path / "extracted"
    extracted = extract_with_permissions(test_zip_without_permissions, dest)

    # Should extract without errors
    assert len(extracted) == 1
    assert (dest / "file1.txt").exists()


def test_return_extracted_paths(test_zip_with_permissions, tmp_path):
    """Test that function returns list of Path objects."""
    dest = tmp_path / "extracted"
    extracted = extract_with_permissions(test_zip_with_permissions, dest)

    assert isinstance(extracted, list)
    assert all(isinstance(path, Path) for path in extracted)


def test_content_preservation(test_zip_with_permissions, tmp_path):
    """Test that file contents are preserved correctly."""
    dest = tmp_path / "extracted"
    extract_with_permissions(test_zip_with_permissions, dest)

    assert (dest / "file1.txt").read_text() == "Content 1"
    assert (dest / "file2.txt").read_text() == "Content 2"
    assert (dest / "subdir" / "file3.txt").read_text() == "Content 3"


def test_destination_created_if_not_exists(test_zip_with_permissions, tmp_path):
    """Test that destination directory is created if it doesn't exist."""
    dest = tmp_path / "new_dir" / "nested" / "extracted"
    assert not dest.exists()

    extract_with_permissions(test_zip_with_permissions, dest)

    assert dest.exists()
    assert (dest / "file1.txt").exists()


def test_nonexistent_zip_raises_error(tmp_path):
    """Test that FileNotFoundError is raised for non-existent ZIP."""
    with pytest.raises(FileNotFoundError, match="ZIP archive not found"):
        extract_with_permissions(tmp_path / "nonexistent.zip", tmp_path / "dest")


def test_invalid_zip_raises_error(tmp_path):
    """Test that BadZipFile is raised for invalid ZIP."""
    invalid_zip = tmp_path / "invalid.zip"
    invalid_zip.write_text("Not a ZIP file")

    with pytest.raises(BadZipFile):
        extract_with_permissions(invalid_zip, tmp_path / "dest")


def test_accepts_string_paths(test_zip_with_permissions, tmp_path):
    """Test that function accepts string paths as well as Path objects."""
    dest = tmp_path / "extracted"
    extracted = extract_with_permissions(str(test_zip_with_permissions), str(dest))

    assert len(extracted) == 3
    assert all(isinstance(path, Path) for path in extracted)


def test_chmod_failure_continues_extraction(test_zip_with_permissions, tmp_path, monkeypatch):
    """Test that extraction continues even if chmod fails."""
    dest = tmp_path / "extracted"
    chmod_calls = []

    original_chmod = os.chmod

    def mock_chmod(path, mode):
        chmod_calls.append((path, mode))
        # Fail only on the first file
        if len(chmod_calls) == 1:
            raise OSError("Simulated chmod failure")
        original_chmod(path, mode)

    monkeypatch.setattr(os, "chmod", mock_chmod)

    # Should complete extraction despite chmod failure
    extracted = extract_with_permissions(test_zip_with_permissions, dest)

    assert len(extracted) == 3
    assert all(path.exists() for path in extracted)
    # chmod should have been attempted for all files
    assert len(chmod_calls) == 3
