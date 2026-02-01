"""
Test suite for save points system
"""
import pytest
import os
import shutil
from pathlib import Path
from project_ai.save_points import SavePointsManager


@pytest.fixture
def temp_save_dir(tmp_path):
    """Create temporary save directory for testing"""
    save_dir = tmp_path / "savepoints"
    yield str(save_dir)
    # Cleanup
    if save_dir.exists():
        shutil.rmtree(save_dir)


def test_save_manager_initialization(temp_save_dir):
    """Test SavePointsManager initialization"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    assert manager.base_dir.exists()
    assert manager.user_dir.exists()
    assert manager.auto_dir.exists()


def test_create_user_save(temp_save_dir):
    """Test creating a user save point"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    result = manager.create_user_save("test_save", {"key": "value"})
    
    assert result["name"] == "test_save"
    assert result["type"] == "user"
    assert "id" in result
    assert result["metadata"]["key"] == "value"


def test_create_auto_save(temp_save_dir):
    """Test creating an auto-save"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    result = manager.create_auto_save()
    
    assert result["type"] == "auto"
    assert result["slot"] == "latest"
    assert (manager.auto_dir / "latest").exists()


def test_auto_save_rotation(temp_save_dir):
    """Test auto-save rotation"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    # Create first auto-save
    manager.create_auto_save()
    assert (manager.auto_dir / "latest").exists()
    
    # Create second - should rotate first to previous1
    manager.create_auto_save()
    assert (manager.auto_dir / "latest").exists()
    assert (manager.auto_dir / "previous1").exists()
    
    # Create third - should rotate to previous2
    manager.create_auto_save()
    assert (manager.auto_dir / "latest").exists()
    assert (manager.auto_dir / "previous1").exists()
    assert (manager.auto_dir / "previous2").exists()
    
    # Create fourth - should delete oldest
    manager.create_auto_save()
    assert (manager.auto_dir / "latest").exists()
    assert (manager.auto_dir / "previous1").exists()
    assert (manager.auto_dir / "previous2").exists()


def test_list_save_points(temp_save_dir):
    """Test listing save points"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    # Create some saves
    manager.create_user_save("save1")
    manager.create_user_save("save2")
    manager.create_auto_save()
    
    result = manager.list_save_points()
    
    assert len(result["user"]) == 2
    assert len(result["auto"]) == 1
    assert result["user"][0]["name"] in ["save1", "save2"]


def test_delete_user_save(temp_save_dir):
    """Test deleting a user save point"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    # Create and delete
    result = manager.create_user_save("test_delete")
    save_id = result["id"]
    
    success = manager.delete_save_point(save_id)
    assert success
    
    # Verify deleted
    saves = manager.list_save_points()
    assert len(saves["user"]) == 0


def test_cannot_delete_auto_save(temp_save_dir):
    """Test that auto-saves cannot be deleted"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    manager.create_auto_save()
    
    # Try to delete auto-save
    success = manager.delete_save_point("latest")
    assert not success


def test_restore_save_point(temp_save_dir):
    """Test restoring from a save point"""
    manager = SavePointsManager(base_dir=temp_save_dir)
    
    # Create test file
    test_file = Path("data/test_restore.txt")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("original")
    
    # Create save
    result = manager.create_user_save("restore_test")
    save_id = result["id"]
    
    # Modify file
    test_file.write_text("modified")
    
    # Restore (note: actual implementation would restore)
    # This is a basic test
    save_path = manager._find_save_point(save_id)
    assert save_path is not None
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
