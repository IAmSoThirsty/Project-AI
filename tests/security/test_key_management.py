"""
Tests for Key Management System
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from src.security.key_management import (
    KeyManagementSystem,
    KeyProvider,
    KeyType,
    KeyStatus,
    KeyMetadata
)


class TestKeyManagementSystem:
    """Test suite for Key Management System"""

    @pytest.fixture
    def kms(self):
        """Create KMS instance for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                'provider': 'local',
                'data_dir': tmpdir
            }
            yield KeyManagementSystem(config)

    def test_initialization(self, kms):
        """Test KMS initialization"""
        assert kms.provider == KeyProvider.LOCAL
        assert os.path.exists(kms.data_dir)
        assert os.path.exists(kms.audit_dir)

    def test_generate_key_local(self, kms):
        """Test local key generation"""
        metadata = kms.generate_key(
            key_id='test-signing-key',
            key_type=KeyType.SIGNING,
            rotation_policy={'enabled': True, 'rotation_days': 90}
        )
        
        assert metadata.key_id == 'test-signing-key'
        assert metadata.key_type == KeyType.SIGNING
        assert metadata.provider == KeyProvider.LOCAL
        assert metadata.status == KeyStatus.ACTIVE
        assert metadata.rotation_policy['enabled'] is True

    def test_generate_symmetric_key(self, kms):
        """Test symmetric key generation"""
        metadata = kms.generate_key(
            key_id='test-encryption-key',
            key_type=KeyType.SYMMETRIC
        )
        
        assert metadata.key_type == KeyType.SYMMETRIC
        assert metadata.status == KeyStatus.ACTIVE

    def test_key_persistence(self, kms):
        """Test that keys are persisted"""
        kms.generate_key(
            key_id='persistent-key',
            key_type=KeyType.SIGNING
        )
        
        # Create new instance with same data dir
        config = {
            'provider': 'local',
            'data_dir': kms.data_dir
        }
        kms2 = KeyManagementSystem(config)
        
        assert 'persistent-key' in kms2.keys
        metadata = kms2.get_key_metadata('persistent-key')
        assert metadata.key_id == 'persistent-key'

    def test_key_rotation(self, kms):
        """Test key rotation"""
        # Generate initial key
        metadata = kms.generate_key(
            key_id='rotate-test-key',
            key_type=KeyType.SIGNING,
            rotation_policy={'enabled': True, 'rotation_days': 1}
        )
        
        # Force rotation
        new_metadata = kms.rotate_key('rotate-test-key', force=True)
        
        assert new_metadata.key_id != 'rotate-test-key'
        assert new_metadata.status == KeyStatus.ACTIVE
        
        # Old key should be deprecated
        old_metadata = kms.get_key_metadata('rotate-test-key')
        assert old_metadata.status == KeyStatus.DEPRECATED

    def test_access_control(self, kms):
        """Test RBAC access control"""
        access_control = {
            'use': ['user1', 'user2'],
            'rotate': ['admin1'],
            'revoke': ['admin1', 'admin2']
        }
        
        kms.generate_key(
            key_id='access-controlled-key',
            key_type=KeyType.SIGNING,
            access_control=access_control
        )
        
        # Test access checks
        assert kms.check_access('access-controlled-key', 'user1', 'use') is True
        assert kms.check_access('access-controlled-key', 'user3', 'use') is False
        assert kms.check_access('access-controlled-key', 'admin1', 'rotate') is True
        assert kms.check_access('access-controlled-key', 'user1', 'rotate') is False

    def test_audit_log(self, kms):
        """Test audit logging"""
        kms.generate_key(
            key_id='audit-test-key',
            key_type=KeyType.SIGNING
        )
        
        # Check audit log
        assert len(kms.audit_log) > 0
        last_event = kms.audit_log[-1]
        assert last_event['event'] == 'key_generated'
        assert last_event['key_id'] == 'audit-test-key'

    def test_export_audit_log(self, kms):
        """Test audit log export"""
        kms.generate_key('export-test-key', KeyType.SIGNING)
        kms.check_access('export-test-key', 'user1', 'use')
        
        # Export to JSON
        output_path = kms.export_audit_log(format='json')
        assert os.path.exists(output_path)
        
        # Verify contents
        import json
        with open(output_path, 'r') as f:
            exported_log = json.load(f)
        
        assert len(exported_log) >= 1  # At least one event (generate or check_access)

    def test_list_keys(self, kms):
        """Test listing keys"""
        kms.generate_key('list-key-1', KeyType.SIGNING)
        kms.generate_key('list-key-2', KeyType.ENCRYPTION)
        kms.generate_key('list-key-3', KeyType.SYMMETRIC)
        
        # List all keys
        all_keys = kms.list_keys()
        assert len(all_keys) == 3
        
        # List active keys
        active_keys = kms.list_keys(status=KeyStatus.ACTIVE)
        assert len(active_keys) == 3

    def test_key_metadata_serialization(self):
        """Test KeyMetadata serialization"""
        metadata = KeyMetadata(
            key_id='serialize-test',
            key_type=KeyType.SIGNING,
            provider=KeyProvider.LOCAL,
            status=KeyStatus.ACTIVE,
            created_at=datetime.utcnow(),
            rotation_policy={'enabled': True, 'rotation_days': 90}
        )
        
        # Serialize
        data = metadata.to_dict()
        assert isinstance(data, dict)
        assert data['key_id'] == 'serialize-test'
        assert data['key_type'] == 'signing'
        
        # Deserialize
        restored = KeyMetadata.from_dict(data)
        assert restored.key_id == metadata.key_id
        assert restored.key_type == metadata.key_type
        assert restored.provider == metadata.provider

    def test_duplicate_key_rejection(self, kms):
        """Test that duplicate keys are rejected"""
        kms.generate_key('duplicate-key', KeyType.SIGNING)
        
        with pytest.raises(ValueError, match="already exists"):
            kms.generate_key('duplicate-key', KeyType.SIGNING)

    def test_rotation_not_due(self, kms):
        """Test that rotation is skipped when not due"""
        metadata = kms.generate_key(
            key_id='not-due-key',
            key_type=KeyType.SIGNING,
            rotation_policy={'enabled': True, 'rotation_days': 365}
        )
        
        # Try to rotate without force
        result = kms.rotate_key('not-due-key', force=False)
        
        # Should return same key metadata
        assert result.key_id == 'not-due-key'
        assert result.status == KeyStatus.ACTIVE
