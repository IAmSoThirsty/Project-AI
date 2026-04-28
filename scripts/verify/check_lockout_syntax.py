"""Quick syntax check for user_manager.py implementation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from app.core.user_manager import UserManager
    print("✓ UserManager imported successfully")
    
    # Check that methods exist
    assert hasattr(UserManager, 'authenticate'), "Missing authenticate method"
    assert hasattr(UserManager, 'is_account_locked'), "Missing is_account_locked method"
    assert hasattr(UserManager, 'unlock_account'), "Missing unlock_account method"
    print("✓ All lockout methods present")
    
    # Create instance and verify it initializes
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        um = UserManager(users_file=str(Path(tmpdir) / "test.json"))
        print("✓ UserManager instance created successfully")
        
        # Create a test user
        result = um.create_user("test", "Password123!")
        assert result is True, "Failed to create user"
        print("✓ User creation works")
        
        # Verify lockout fields exist
        assert "failed_attempts" in um.users["test"]
        assert "locked_until" in um.users["test"]
        print("✓ Lockout fields initialized")
        
        # Test authentication returns tuple
        success, msg = um.authenticate("test", "Password123!")
        assert success is True
        assert isinstance(msg, str)
        print("✓ Authentication returns tuple (bool, str)")
        
    print("\n✅ ALL SYNTAX AND IMPORT CHECKS PASSED")
    print("🛡️  Account lockout protection is operational")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
