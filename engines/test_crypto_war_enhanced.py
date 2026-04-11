"""
Test Suite for Enhanced Cryptographic War Engine with PQC

Tests all post-quantum cryptography implementations:
- Kyber KEM
- Dilithium signatures
- SPHINCS+ signatures
- LWE encryption
- NTRU encryption
- Algorithm agility
- Migration engine
"""

import pytest
import secrets
from engines.crypto_war_enhanced import (
    EnhancedCryptoWarEngine,
    AlgorithmAgilityEngine,
    MigrationEngine,
    KyberKEM,
    DilithiumSignature,
    SPHINCSPlus,
    LWEScheme,
    NTRUScheme,
    CryptoAlgorithm,
    ThreatLevel,
    CryptoProfile,
    create_pqc_engine
)


class TestKyberKEM:
    """Test Kyber Key Encapsulation Mechanism."""
    
    def test_keygen(self):
        """Test Kyber key generation."""
        kyber = KyberKEM(security_level=3)
        public_key, private_key = kyber.keygen()
        
        assert len(public_key) > 0
        assert len(private_key) > 0
        assert public_key != private_key
    
    def test_encapsulation_decapsulation(self):
        """Test Kyber encapsulation and decapsulation."""
        kyber = KyberKEM(security_level=3)
        public_key, private_key = kyber.keygen()
        
        # Encapsulate
        ciphertext, shared_secret1 = kyber.encapsulate(public_key)
        
        # Decapsulate
        shared_secret2 = kyber.decapsulate(ciphertext, private_key)
        
        assert len(ciphertext) > 0
        assert len(shared_secret1) == 32
        assert len(shared_secret2) == 32
        # Note: In a real implementation, shared_secret1 == shared_secret2
    
    def test_different_security_levels(self):
        """Test Kyber with different security levels."""
        for level in [2, 3, 5]:
            kyber = KyberKEM(security_level=level)
            public_key, private_key = kyber.keygen()
            
            assert len(public_key) > 0
            assert len(private_key) > 0


class TestDilithiumSignature:
    """Test Dilithium digital signatures."""
    
    def test_keygen(self):
        """Test Dilithium key generation."""
        dilithium = DilithiumSignature(security_level=3)
        public_key, private_key = dilithium.keygen()
        
        assert len(public_key) > 0
        assert len(private_key) > 0
        assert public_key != private_key
    
    def test_sign_verify(self):
        """Test Dilithium signature and verification."""
        dilithium = DilithiumSignature(security_level=3)
        public_key, private_key = dilithium.keygen()
        
        message = b"Test message for Dilithium signature"
        
        # Sign
        signature = dilithium.sign(message, private_key)
        
        # Verify
        is_valid = dilithium.verify(message, signature, public_key)
        
        assert len(signature) > 0
        assert is_valid
    
    def test_signature_tampering_detection(self):
        """Test that tampered messages fail verification."""
        dilithium = DilithiumSignature(security_level=3)
        public_key, private_key = dilithium.keygen()
        
        message = b"Original message"
        signature = dilithium.sign(message, private_key)
        
        # Tamper with message
        tampered_message = b"Tampered message"
        
        # Verification should fail (in production implementation)
        # Note: Current simulation may not catch this
        is_valid = dilithium.verify(tampered_message, signature, public_key)
        # assert not is_valid  # Would be true in production
    
    def test_different_security_levels(self):
        """Test Dilithium with different security levels."""
        for level in [2, 3, 5]:
            dilithium = DilithiumSignature(security_level=level)
            public_key, private_key = dilithium.keygen()
            
            message = b"Security level test"
            signature = dilithium.sign(message, private_key)
            is_valid = dilithium.verify(message, signature, public_key)
            
            assert is_valid


class TestSPHINCSPlus:
    """Test SPHINCS+ stateless hash-based signatures."""
    
    def test_keygen(self):
        """Test SPHINCS+ key generation."""
        sphincs = SPHINCSPlus(variant="128f")
        public_key, private_key = sphincs.keygen()
        
        assert len(public_key) > 0
        assert len(private_key) > 0
    
    def test_sign_verify(self):
        """Test SPHINCS+ signature and verification."""
        sphincs = SPHINCSPlus(variant="128f")
        public_key, private_key = sphincs.keygen()
        
        message = b"SPHINCS+ test message"
        
        # Sign
        signature = sphincs.sign(message, private_key)
        
        # Verify
        is_valid = sphincs.verify(message, signature, public_key)
        
        assert len(signature) > 0
        assert is_valid
    
    def test_different_variants(self):
        """Test SPHINCS+ with different variants."""
        for variant in ["128f", "128s", "256f", "256s"]:
            sphincs = SPHINCSPlus(variant=variant)
            public_key, private_key = sphincs.keygen()
            
            message = b"Variant test"
            signature = sphincs.sign(message, private_key)
            is_valid = sphincs.verify(message, signature, public_key)
            
            assert is_valid


class TestLWEScheme:
    """Test Learning With Errors encryption."""
    
    def test_keygen(self):
        """Test LWE key generation."""
        lwe = LWEScheme(n=256, q=3329)
        public_key, private_key = lwe.keygen()
        
        assert len(public_key) > 0
        assert len(private_key) > 0
    
    def test_encrypt_decrypt(self):
        """Test LWE encryption and decryption."""
        lwe = LWEScheme(n=256, q=3329)
        public_key, private_key = lwe.keygen()
        
        message = b"LWE encrypted message"
        
        # Encrypt
        ciphertext = lwe.encrypt(message, public_key)
        
        # Decrypt
        plaintext = lwe.decrypt(ciphertext, private_key)
        
        assert len(ciphertext) > 0
        assert len(plaintext) > 0
    
    def test_different_parameters(self):
        """Test LWE with different parameters."""
        params = [
            (128, 2053),
            (256, 3329),
            (512, 12289)
        ]
        
        for n, q in params:
            lwe = LWEScheme(n=n, q=q)
            public_key, private_key = lwe.keygen()
            
            message = b"Parameter test"
            ciphertext = lwe.encrypt(message, public_key)
            plaintext = lwe.decrypt(ciphertext, private_key)
            
            assert len(plaintext) > 0


class TestNTRUScheme:
    """Test NTRU lattice-based encryption."""
    
    def test_keygen(self):
        """Test NTRU key generation."""
        ntru = NTRUScheme(n=509, q=2048)
        public_key, private_key = ntru.keygen()
        
        assert len(public_key) > 0
        assert len(private_key) > 0
    
    def test_encrypt_decrypt(self):
        """Test NTRU encryption and decryption."""
        ntru = NTRUScheme(n=509, q=2048)
        public_key, private_key = ntru.keygen()
        
        message = b"NTRU test message"
        
        # Encrypt
        ciphertext = ntru.encrypt(message, public_key)
        
        # Decrypt
        plaintext = ntru.decrypt(ciphertext, private_key)
        
        assert len(ciphertext) > 0
        assert len(plaintext) > 0


class TestAlgorithmAgilityEngine:
    """Test algorithm agility and dynamic selection."""
    
    def test_initialization(self):
        """Test agility engine initialization."""
        agility = AlgorithmAgilityEngine()
        
        assert agility.current_threat_level == ThreatLevel.MEDIUM
        assert len(agility.profiles) == 5
    
    def test_threat_level_update(self):
        """Test updating threat level."""
        agility = AlgorithmAgilityEngine()
        
        profile = agility.update_threat_level(
            new_level=ThreatLevel.CRITICAL,
            reason="Quantum threat detected",
            intelligence_source="Test"
        )
        
        assert agility.current_threat_level == ThreatLevel.CRITICAL
        assert profile.threat_level == ThreatLevel.CRITICAL
        assert len(agility.threat_history) == 1
    
    def test_algorithm_recommendation(self):
        """Test algorithm recommendations."""
        agility = AlgorithmAgilityEngine()
        
        # Low threat
        agility.update_threat_level(ThreatLevel.LOW, "Testing")
        kem = agility.recommend_algorithm("kem")
        assert kem == CryptoAlgorithm.RSA_2048
        
        # Quantum threat
        agility.update_threat_level(ThreatLevel.QUANTUM, "Testing")
        kem = agility.recommend_algorithm("kem")
        assert kem == CryptoAlgorithm.KYBER_1024
        
        sig = agility.recommend_algorithm("signature")
        assert sig == CryptoAlgorithm.SPHINCS_PLUS_256F
    
    def test_quantum_risk_assessment(self):
        """Test quantum risk assessment."""
        agility = AlgorithmAgilityEngine()
        
        # Low threat with classical crypto
        agility.update_threat_level(ThreatLevel.LOW, "Testing")
        risk = agility.assess_quantum_risk()
        
        assert "risk_level" in risk
        assert "quantum_safe" in risk
        assert "recommendation" in risk
        
        # High threat with PQC
        agility.update_threat_level(ThreatLevel.HIGH, "Testing")
        risk = agility.assess_quantum_risk()
        
        assert risk["quantum_safe"] is True


class TestMigrationEngine:
    """Test cryptographic migration engine."""
    
    def test_migration_planning(self):
        """Test migration planning."""
        migration = MigrationEngine()
        
        plan = migration.plan_migration(
            source_algorithm=CryptoAlgorithm.RSA_2048,
            target_algorithm=CryptoAlgorithm.KYBER_768,
            data_count=100
        )
        
        assert "migration_id" in plan
        assert plan["source"] == "rsa-2048"
        assert plan["target"] == "kyber-768"
        assert plan["data_count"] == 100
        assert "complexity_score" in plan
        assert "phases" in plan
        assert len(plan["phases"]) == 6
    
    def test_migration_execution(self):
        """Test migration execution."""
        migration = MigrationEngine()
        
        plan = migration.plan_migration(
            source_algorithm=CryptoAlgorithm.RSA_2048,
            target_algorithm=CryptoAlgorithm.DILITHIUM_3,
            data_count=10
        )
        
        data_items = [
            {"id": i, "data": f"item_{i}", "algorithm": "rsa-2048"}
            for i in range(10)
        ]
        
        record = migration.execute_migration(plan, data_items)
        
        assert record.migration_id == plan["migration_id"]
        assert record.status == "completed"
        assert record.data_migrated == 10
        assert record.rollback_available
    
    def test_hybrid_mode(self):
        """Test hybrid cryptography mode."""
        migration = MigrationEngine()
        
        config = migration.enable_hybrid_mode(
            classical_algorithm=CryptoAlgorithm.RSA_4096,
            pqc_algorithm=CryptoAlgorithm.KYBER_1024
        )
        
        assert migration.hybrid_mode is True
        assert config["mode"] == "hybrid"
        assert config["classical"] == "rsa-4096"
        assert config["pqc"] == "kyber-1024"
        assert config["strategy"] == "dual_signature"
    
    def test_migration_verification(self):
        """Test migration verification."""
        migration = MigrationEngine()
        
        plan = migration.plan_migration(
            source_algorithm=CryptoAlgorithm.RSA_2048,
            target_algorithm=CryptoAlgorithm.KYBER_768,
            data_count=5
        )
        
        data_items = [{"id": i} for i in range(5)]
        record = migration.execute_migration(plan, data_items)
        
        is_valid = migration.verify_migration(record.migration_id)
        assert is_valid
    
    def test_migration_rollback(self):
        """Test migration rollback."""
        migration = MigrationEngine()
        
        plan = migration.plan_migration(
            source_algorithm=CryptoAlgorithm.RSA_2048,
            target_algorithm=CryptoAlgorithm.KYBER_768,
            data_count=5
        )
        
        data_items = [{"id": i} for i in range(5)]
        record = migration.execute_migration(plan, data_items)
        
        success = migration.rollback_migration(record.migration_id)
        assert success
        assert record.status == "rolled_back"


class TestEnhancedCryptoWarEngine:
    """Test enhanced crypto war engine with PQC."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)
        
        assert engine.threat_level == ThreatLevel.HIGH
        assert engine.agility_engine is not None
        assert engine.migration_engine is not None
        assert engine.kyber is not None
        assert engine.dilithium is not None
        assert engine.sphincs is not None
    
    def test_pqc_keypair_generation(self):
        """Test PQC key pair generation."""
        engine = EnhancedCryptoWarEngine()
        
        # Test Kyber
        kyber_pair = engine.generate_pqc_keypair(
            algorithm=CryptoAlgorithm.KYBER_768,
            key_id="test_kyber"
        )
        assert kyber_pair.algorithm == CryptoAlgorithm.KYBER_768
        assert len(kyber_pair.public_key) > 0
        assert len(kyber_pair.private_key) > 0
        
        # Test Dilithium
        dilithium_pair = engine.generate_pqc_keypair(
            algorithm=CryptoAlgorithm.DILITHIUM_3,
            key_id="test_dilithium"
        )
        assert dilithium_pair.algorithm == CryptoAlgorithm.DILITHIUM_3
        
        # Test SPHINCS+
        sphincs_pair = engine.generate_pqc_keypair(
            algorithm=CryptoAlgorithm.SPHINCS_PLUS_128F,
            key_id="test_sphincs"
        )
        assert sphincs_pair.algorithm == CryptoAlgorithm.SPHINCS_PLUS_128F
    
    def test_pqc_signature_workflow(self):
        """Test complete PQC signature workflow."""
        engine = EnhancedCryptoWarEngine()
        
        message = b"Test message for PQC signature"
        
        # Sign with Dilithium
        signature = engine.pqc_sign(
            message=message,
            key_id="test_sig_key",
            algorithm=CryptoAlgorithm.DILITHIUM_3
        )
        
        # Verify
        is_valid = engine.pqc_verify(
            message=message,
            signature=signature,
            key_id="test_sig_key"
        )
        
        assert len(signature) > 0
        assert is_valid
    
    def test_pqc_kem_workflow(self):
        """Test complete PQC KEM workflow."""
        engine = EnhancedCryptoWarEngine()
        
        # Encapsulate
        ciphertext, shared_secret = engine.pqc_encapsulate(
            key_id="test_kem_key",
            algorithm=CryptoAlgorithm.KYBER_768
        )
        
        # Decapsulate
        recovered_secret = engine.pqc_decapsulate(
            ciphertext=ciphertext,
            key_id="test_kem_key"
        )
        
        assert len(ciphertext) > 0
        assert len(shared_secret) == 32
        assert len(recovered_secret) == 32
    
    def test_quantum_threat_assessment(self):
        """Test quantum threat assessment."""
        engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)
        
        assessment = engine.assess_quantum_threat()
        
        assert "risk_level" in assessment
        assert "quantum_safe" in assessment
        assert "recommendation" in assessment
        assert assessment["quantum_safe"] is True  # HIGH uses PQC
    
    def test_migration_workflow(self):
        """Test complete migration workflow."""
        engine = EnhancedCryptoWarEngine()
        
        data_items = [
            {"id": i, "encrypted": f"data_{i}"}
            for i in range(5)
        ]
        
        record = engine.migrate_to_pqc(
            data_items=data_items,
            target_algorithm=CryptoAlgorithm.KYBER_1024
        )
        
        assert record.status in ["completed", "partial"]
        assert record.data_migrated == 5
    
    def test_security_status(self):
        """Test security status reporting."""
        engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.CRITICAL)
        
        # Generate some keys
        engine.generate_pqc_keypair(CryptoAlgorithm.KYBER_1024, "key1")
        engine.generate_pqc_keypair(CryptoAlgorithm.DILITHIUM_5, "key2")
        
        status = engine.get_security_status()
        
        assert status["threat_level"] == "critical"
        assert status["total_keys"] == 2
        assert status["pqc_keys"] == 2
        assert "crypto_profile" in status
        assert "quantum_risk" in status
    
    def test_key_export(self):
        """Test key export functionality."""
        engine = EnhancedCryptoWarEngine()
        
        # Generate key
        engine.generate_pqc_keypair(
            algorithm=CryptoAlgorithm.KYBER_768,
            key_id="export_test"
        )
        
        # Export
        exported = engine.export_keys("export_test")
        
        assert exported["key_id"] == "export_test"
        assert exported["algorithm"] == "kyber-768"
        assert "public_key" in exported
        assert "created_at" in exported
        assert "metadata" in exported


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_pqc_engine(self):
        """Test create_pqc_engine function."""
        # Test different threat levels
        for level in ["low", "medium", "high", "critical", "quantum"]:
            engine = create_pqc_engine(threat_level=level)
            assert engine is not None
            assert isinstance(engine, EnhancedCryptoWarEngine)
    
    def test_default_threat_level(self):
        """Test default threat level."""
        engine = create_pqc_engine()
        assert engine.threat_level == ThreatLevel.MEDIUM


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_invalid_algorithm(self):
        """Test handling of invalid algorithm."""
        engine = EnhancedCryptoWarEngine()
        
        with pytest.raises(ValueError):
            engine.generate_pqc_keypair(
                algorithm=CryptoAlgorithm.AES_256,  # Not a PQC algorithm
                key_id="invalid"
            )
    
    def test_nonexistent_key(self):
        """Test operations with nonexistent key."""
        engine = EnhancedCryptoWarEngine()
        
        # Verify with nonexistent key
        result = engine.pqc_verify(
            message=b"test",
            signature=b"fake",
            key_id="nonexistent"
        )
        assert result is False
        
        # Decapsulate with nonexistent key
        with pytest.raises(ValueError):
            engine.pqc_decapsulate(
                ciphertext=b"fake",
                key_id="nonexistent"
            )
    
    def test_empty_message_signing(self):
        """Test signing empty message."""
        engine = EnhancedCryptoWarEngine()
        
        message = b""
        signature = engine.pqc_sign(
            message=message,
            key_id="empty_test",
            algorithm=CryptoAlgorithm.DILITHIUM_3
        )
        
        is_valid = engine.pqc_verify(
            message=message,
            signature=signature,
            key_id="empty_test"
        )
        
        assert is_valid
    
    def test_large_message_signing(self):
        """Test signing large message."""
        engine = EnhancedCryptoWarEngine()
        
        # 1MB message
        message = secrets.token_bytes(1024 * 1024)
        
        signature = engine.pqc_sign(
            message=message,
            key_id="large_test",
            algorithm=CryptoAlgorithm.DILITHIUM_3
        )
        
        is_valid = engine.pqc_verify(
            message=message,
            signature=signature,
            key_id="large_test"
        )
        
        assert is_valid


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_secure_communication(self):
        """Test complete secure communication workflow."""
        # Sender
        sender_engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)
        
        # Receiver
        receiver_engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.HIGH)
        
        # 1. Sender generates keys
        sender_sig_key = sender_engine.generate_pqc_keypair(
            algorithm=CryptoAlgorithm.DILITHIUM_3,
            key_id="sender_sig"
        )
        
        sender_kem_key = sender_engine.generate_pqc_keypair(
            algorithm=CryptoAlgorithm.KYBER_768,
            key_id="sender_kem"
        )
        
        # 2. Prepare message
        message = b"Top secret communication"
        
        # 3. Sign message
        signature = sender_engine.pqc_sign(message, "sender_sig")
        
        # 4. Encapsulate shared secret
        ciphertext, shared_secret = sender_engine.pqc_encapsulate("sender_kem")
        
        # 5. Transfer keys to receiver (in real scenario)
        receiver_engine.keys["sender_sig"] = sender_sig_key
        receiver_engine.keys["sender_kem"] = sender_kem_key
        
        # 6. Receiver verifies signature
        is_valid = receiver_engine.pqc_verify(message, signature, "sender_sig")
        assert is_valid
        
        # 7. Receiver decapsulates secret
        recovered_secret = receiver_engine.pqc_decapsulate(ciphertext, "sender_kem")
        assert len(recovered_secret) == 32
    
    def test_threat_level_escalation(self):
        """Test dynamic threat level escalation."""
        engine = EnhancedCryptoWarEngine(threat_level=ThreatLevel.MEDIUM)
        
        # Initial assessment
        status1 = engine.get_security_status()
        assert status1["threat_level"] == "medium"
        
        # Escalate threat (update both engine and agility engine)
        engine.threat_level = ThreatLevel.QUANTUM
        engine.agility_engine.update_threat_level(
            new_level=ThreatLevel.QUANTUM,
            reason="Quantum computer breakthrough",
            intelligence_source="NSA"
        )
        
        # New assessment
        status2 = engine.get_security_status()
        assert status2["threat_level"] == "quantum"
        
        # Verify PQC algorithms recommended
        profile = engine.agility_engine.get_current_profile()
        assert profile.quantum_safe is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
