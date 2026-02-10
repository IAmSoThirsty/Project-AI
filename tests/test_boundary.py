import pytest

from cognition.boundary import enforce_boundary


def test_boundary_blocks_missing_tarl():
    with pytest.raises(RuntimeError):
        enforce_boundary(None)


def test_boundary_accepts_tarl():
    assert enforce_boundary("deadbeef") is True
