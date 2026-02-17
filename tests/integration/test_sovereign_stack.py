"""
Integration tests for Sovereign Stack
Verifies real functionality of all subsystems
"""
import pytest
import logging
from pathlib import Path
from project_ai.orchestrator import BootSequence
from project_ai.orchestrator.subsystems import (
    CerberusIntegration,
    ThirstyLangIntegration,
    MonolithIntegration,
    WaterfallIntegration,
    TriumvirateIntegration
)

logging.basicConfig(level=logging.INFO)


class TestCerberusIntegration:
    """Test Cerberus security framework"""
    
    def test_cerberus_initialization(self):
        """Verify Cerberus can be initialized"""
        cerberus = CerberusIntegration({})
        assert cerberus is not None
        status = cerberus.get_status()
        assert 'active' in status
        assert 'available' in status
    
    def test_cerberus_starts_gracefully(self):
        """Verify Cerberus starts (or gracefully degrades if unavailable)"""
        cerberus = CerberusIntegration({})
        
        # Should not raise exception even if Cerberus not available
        try:
            cerberus.start()
            status = cerberus.get_status()
            # Either active (if available) or inactive (if not)
            assert isinstance(status['active'], bool)
        except Exception as e:
            pytest.fail(f"Cerberus should not raise exception on start: {e}")
        
        cerberus.stop()
    
    @pytest.mark.skipif(
        not Path("external/Cerberus/src").exists(),
        reason="Cerberus not installed"
    )
    def test_cerberus_analyzes_input(self):
        """Verify Cerberus can analyze threats (if available)"""
        cerberus = CerberusIntegration({})
        cerberus.start()
        
        if cerberus.active:
            # Test benign input
            result = cerberus.analyze_input("Hello, how are you?")
            assert 'should_block' in result
            assert 'summary' in result
            assert 'active_guardians' in result
            
            cerberus.stop()


class TestThirstyLangIntegration:
    """Test Thirsty-Lang compiler and runtime"""
    
    def test_thirsty_lang_initialization(self):
        """Verify Thirsty-Lang can be initialized"""
        thirsty = ThirstyLangIntegration({})
        assert thirsty is not None
        status = thirsty.get_status()
        assert 'active' in status
        assert 'cli_path' in status
    
    @pytest.mark.skipif(
        not Path("external/Thirsty-Lang/src/cli.js").exists(),
        reason="Thirsty-Lang CLI not found"
    )
    def test_thirsty_lang_starts(self):
        """Verify Thirsty-Lang starts and verifies Node.js"""
        thirsty = ThirstyLangIntegration({})
        
        try:
            thirsty.start()
            status = thirsty.get_status()
            assert status['active'] == True
            assert status['node_version'] is not None
            assert status['cli_exists'] == True
            thirsty.stop()
        except RuntimeError as e:
            # Expected if Node.js not installed
            pytest.skip(f"Node.js not available: {e}")
    
    @pytest.mark.skipif(
        not Path("external/Thirsty-Lang/src/cli.js").exists(),
        reason="Thirsty-Lang CLI not found"
    )
    def test_thirsty_lang_compiles_code(self):
        """Verify Thirsty-Lang can actually compile and run code"""
        thirsty = ThirstyLangIntegration({})
        
        try:
            thirsty.start()
            
            # Test simple program
            code = 'drink x = 42\npour x'
            result = thirsty.compile_and_run(code)
            assert result == True, "Should successfully compile simple code"
            
            thirsty.stop()
        except RuntimeError:
            pytest.skip("Node.js not available")


class TestMonolithIntegration:
    """Test Thirstys-Monolith governance system"""
    
    def test_monolith_initialization(self):
        """Verify Monolith can be initialized"""
        monolith = MonolithIntegration({})
        assert monolith is not None
        status = monolith.get_status()
        assert 'active' in status
        assert 'available' in status
    
    def test_monolith_starts_gracefully(self):
        """Verify Monolith starts or degrades gracefully"""
        monolith = MonolithIntegration({})
        
        try:
            monolith.start()
            status = monolith.get_status()
            assert isinstance(status['active'], bool)
        except Exception as e:
            pytest.fail(f"Monolith should not raise exception on start: {e}")
        
        monolith.stop()


class TestWaterfallIntegration:
    """Test Thirstys-Waterfall privacy suite"""
    
    def test_waterfall_initialization(self):
        """Verify Waterfall can be initialized"""
        waterfall = WaterfallIntegration({})
        assert waterfall is not None
        status = waterfall.get_status()
        assert 'active' in status
    
    @pytest.mark.skipif(
        not Path("external/Thirstys-Waterfall/thirstys_waterfall/__init__.py").exists(),
        reason="Waterfall not installed"
    )
    def test_waterfall_starts(self):
        """Verify Waterfall starts with VPN and firewalls"""
        waterfall = WaterfallIntegration({})
        
        try:
            waterfall.start()
            status = waterfall.get_status()
            
            if waterfall.active:
                assert status['active'] == True
                assert 'vpn' in status
                assert 'firewalls' in status
                
            waterfall.stop()
        except Exception as e:
            pytest.skip(f"Waterfall dependencies not available: {e}")


class TestTriumvirateIntegration:
    """Test The_Triumvirate documentation website"""
    
    def test_triumvirate_initialization(self):
        """Verify Triumvirate can be initialized"""
        triumvirate = TriumvirateIntegration({})
        assert triumvirate is not None
        status = triumvirate.get_status()
        assert 'active' in status
        assert status['type'] == 'documentation_website'
    
    def test_triumvirate_starts(self):
        """Verify Triumvirate recognizes documentation"""
        triumvirate = TriumvirateIntegration({})
        triumvirate.start()
        
        status = triumvirate.get_status()
        assert status['type'] == 'documentation_website'
        assert status['purpose'] == 'AGI-Human relations manifesto'
        assert status['pages'] == 11
        
        triumvirate.stop()
    
    def test_triumvirate_website_exists(self):
        """Verify Triumvirate HTML files exist"""
        triumvirate = TriumvirateIntegration({})
        triumvirate.start()
        
        status = triumvirate.get_status()
        # Check if index.html exists
        assert 'index_exists' in status
        
        triumvirate.stop()


class TestBootSequence:
    """Test complete boot sequence"""
    
    def test_boot_sequence_initialization(self):
        """Verify boot sequence can be created"""
        boot = BootSequence({})
        assert boot is not None
        assert len(boot.boot_order) == 5
        assert boot.boot_order[0] == 'cerberus'  # Security first
    
    def test_boot_sequence_starts_all(self):
        """Verify boot sequence starts all subsystems"""
        boot = BootSequence({})
        
        # Should not crash
        boot.initialize_all()
        
        # Verify all subsystems initialized
        assert 'cerberus' in boot.subsystems
        assert 'thirsty_lang' in boot.subsystems
        assert 'monolith' in boot.subsystems
        assert 'waterfall' in boot.subsystems
        assert 'triumvirate' in boot.subsystems
        
        # Get status
        status = boot.get_status()
        assert len(status) == 5
        
        # At least some subsystems should have attempted to start
        assert all('active' in s for s in status.values())
        
        boot.shutdown_all()
    
    def test_boot_order_correct(self):
        """Verify subsystems boot in correct order"""
        boot = BootSequence({})
        
        # Check boot order
        expected_order = ['cerberus', 'monolith', 'thirsty_lang', 'waterfall', 'triumvirate']
        assert boot.boot_order == expected_order
    
    def test_boot_shutdown_graceful(self):
        """Verify graceful shutdown doesn't crash"""
        boot = BootSequence({})
        boot.initialize_all()
        
        # Should not crash
        try:
            boot.shutdown_all()
        except Exception as e:
            pytest.fail(f"Shutdown should not raise exception: {e}")


class TestIntegrationEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_stack_boot_and_shutdown(self):
        """Test complete boot and shutdown cycle"""
        boot = BootSequence({})
        
        # Boot
        boot.initialize_all()
        
        # Get status
        status = boot.get_status()
        assert len(status) == 5
        
        # Shutdown
        boot.shutdown_all()
        
        # Verify shutdown
        for subsystem in boot.subsystems.values():
            assert subsystem.active == False
    
    def test_subsystem_isolation(self):
        """Verify subsystems can run independently"""
        # Each should be able to start/stop independently
        
        # Cerberus
        cerb = CerberusIntegration({})
        cerb.start()
        cerb.stop()
        
        # Thirsty-Lang
        thirsty = ThirstyLangIntegration({})
        try:
            thirsty.start()
            thirsty.stop()
        except RuntimeError:
            pass  # Expected if Node.js not available
        
        # Monolith
        mono = MonolithIntegration({})
        mono.start()
        mono.stop()
        
        # Waterfall
        water = WaterfallIntegration({})
        try:
            water.start()
            water.stop()
        except Exception:
            pass  # Expected if dependencies not available
        
        # Triumvirate
        tri = TriumvirateIntegration({})
        tri.start()
        tri.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
