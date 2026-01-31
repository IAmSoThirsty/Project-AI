"""
Comprehensive tests for God Tier System
Tests all components: voice, visual, conversation, fusion, policy management.
"""
import os
import tempfile
import time
from unittest.mock import Mock, patch

import numpy as np
import pytest

from src.app.core.voice_models import (
    VoiceModelRegistry, BasicTTSVoiceModel, EmotionalTTSVoiceModel,
    VoiceModelMetadata, VoiceModelType, VoiceEmotionType
)
from src.app.core.voice_bonding_protocol import (
    EngagementProfiler, VoiceBondingProtocol, UserExpressionType
)
from src.app.core.visual_cue_models import (
    VisualCueModelRegistry, CameraManager, FacialEmotionModel,
    FocusAttentionModel
)
from src.app.core.visual_bonding_controller import (
    VisualBondingProtocol, VisualController
)
from src.app.core.conversation_context_engine import (
    ConversationContextEngine, PolicyManager, Intent
)
from src.app.core.multimodal_fusion import (
    MultiModalFusionEngine, MultiModalInput, FusionStrategy
)
from src.app.core.god_tier_config import (
    GodTierConfig, ConfigurationManager
)
from src.app.core.god_tier_integration import (
    GodTierIntegratedSystem
)


class TestVoiceSystem:
    """Tests for voice model system"""

    def test_voice_model_registry_creation(self):
        """Test voice model registry creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = VoiceModelRegistry(tmpdir)
            assert registry is not None
            assert len(registry.list_models()) == 0

    def test_voice_model_registration(self):
        """Test registering voice models"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = VoiceModelRegistry(tmpdir)
            
            model = BasicTTSVoiceModel(VoiceModelMetadata(
                model_id="test_model",
                model_type=VoiceModelType.TTS_BASIC,
                name="Test Model"
            ))
            
            assert registry.register(model) is True
            assert len(registry.list_models()) == 1
            
            # Test duplicate registration
            assert registry.register(model) is False

    def test_voice_model_synthesis(self):
        """Test voice synthesis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = VoiceModelRegistry(tmpdir)
            
            model = BasicTTSVoiceModel(VoiceModelMetadata(
                model_id="test_model",
                model_type=VoiceModelType.TTS_BASIC,
                name="Test Model"
            ))
            
            registry.register(model)
            model.initialize()
            
            response = model.synthesize("Hello world", VoiceEmotionType.HAPPY)
            assert response.success is True
            assert response.text == "Hello world"
            assert response.emotion == VoiceEmotionType.HAPPY

    def test_engagement_profiler(self):
        """Test engagement profiler"""
        with tempfile.TemporaryDirectory() as tmpdir:
            profiler = EngagementProfiler(tmpdir)
            
            user_id = "test_user"
            text = "This is damn good!"
            
            analysis = profiler.analyze_user_input(user_id, text)
            
            assert "expression_types" in analysis
            assert "detected_swearing" in analysis
            assert analysis["detected_swearing"] is True

    def test_voice_bonding_protocol(self):
        """Test voice bonding protocol"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = VoiceModelRegistry(os.path.join(tmpdir, "voice"))
            profiler = EngagementProfiler(os.path.join(tmpdir, "engagement"))
            bonding = VoiceBondingProtocol(registry, profiler, 
                                          os.path.join(tmpdir, "bonding"))
            
            # Register model
            model = BasicTTSVoiceModel(VoiceModelMetadata(
                model_id="test_model",
                model_type=VoiceModelType.TTS_BASIC,
                name="Test Model"
            ))
            registry.register(model)
            model.initialize()
            
            # Start bonding
            user_id = "test_user"
            assert bonding.start_bonding(user_id) is True
            
            # Experiment
            response = bonding.experiment_with_model(user_id, "test_model", "Hello")
            assert response is not None
            
            # Provide feedback
            assert bonding.provide_feedback(user_id, "test_model", "positive") is True


class TestVisualSystem:
    """Tests for visual cue recognition system"""

    def test_visual_registry_creation(self):
        """Test visual model registry creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = VisualCueModelRegistry(tmpdir)
            assert registry is not None
            assert len(registry.list_models()) == 0

    def test_facial_emotion_model(self):
        """Test facial emotion detection"""
        model = FacialEmotionModel()
        model.initialize()
        
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        cue_data = model.detect(frame)
        
        assert cue_data.is_present is True
        assert cue_data.emotion_confidence > 0

    def test_focus_attention_model(self):
        """Test focus and attention detection"""
        model = FocusAttentionModel()
        model.initialize()
        
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        cue_data = model.detect(frame)
        
        assert cue_data.is_present is True
        assert cue_data.focus_level is not None

    def test_camera_manager(self):
        """Test camera manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CameraManager(tmpdir)
            
            devices = manager.discover_devices()
            assert len(devices) >= 0  # May have simulated devices
            
            if devices:
                assert manager.activate_device(devices[0].device_id) is True

    def test_visual_bonding_protocol(self):
        """Test visual bonding protocol"""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = VisualCueModelRegistry(os.path.join(tmpdir, "visual"))
            camera = CameraManager(os.path.join(tmpdir, "camera"))
            bonding = VisualBondingProtocol(registry, camera,
                                           os.path.join(tmpdir, "bonding"))
            
            # Register model
            model = FacialEmotionModel()
            registry.register(model)
            model.initialize()
            
            # Start bonding
            user_id = "test_user"
            assert bonding.start_bonding(user_id) is True
            
            # Experiment
            frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            result = bonding.experiment_with_model(user_id, model.model_id, frame)
            assert result is not None


class TestConversationSystem:
    """Tests for conversation context engine"""

    def test_context_engine_creation(self):
        """Test conversation context engine creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ConversationContextEngine(tmpdir)
            assert engine is not None

    def test_session_management(self):
        """Test conversation session management"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ConversationContextEngine(tmpdir)
            
            user_id = "test_user"
            session_id = engine.start_session(user_id)
            assert session_id != ""
            
            # Add turns
            turn = engine.add_turn(session_id, "Hello", "Hi there!")
            assert turn is not None
            assert turn.user_input == "Hello"
            assert turn.system_response == "Hi there!"
            
            # Get context
            context = engine.get_context(session_id)
            assert context["turn_count"] == 1
            
            # End session
            assert engine.end_session(session_id) is True

    def test_intent_detection(self):
        """Test intent detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ConversationContextEngine(tmpdir)
            
            # Test query intent
            intent = engine._detect_intent("What is the weather today?")
            assert intent == Intent.QUERY
            
            # Test command intent
            intent = engine._detect_intent("Run the program")
            assert intent == Intent.COMMAND
            
            # Test greeting intent
            intent = engine._detect_intent("Hello there")
            assert intent == Intent.GREETING

    def test_policy_manager(self):
        """Test adaptive policy manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = ConversationContextEngine(os.path.join(tmpdir, "context"))
            policy_mgr = PolicyManager(engine, os.path.join(tmpdir, "policy"))
            
            user_id = "test_user"
            session_id = engine.start_session(user_id)
            
            # Get policies
            policies = policy_mgr.get_adaptive_policy(user_id, session_id)
            assert "response_length" in policies
            assert "empathy_level" in policies


class TestMultiModalFusion:
    """Tests for multi-modal fusion system"""

    def test_fusion_engine_creation(self):
        """Test fusion engine creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            profiler = EngagementProfiler(os.path.join(tmpdir, "engagement"))
            
            registry = VisualCueModelRegistry(os.path.join(tmpdir, "visual"))
            camera = CameraManager(os.path.join(tmpdir, "camera"))
            visual_bonding = VisualBondingProtocol(registry, camera,
                                                   os.path.join(tmpdir, "v_bonding"))
            visual_ctrl = VisualController(registry, camera, visual_bonding,
                                          os.path.join(tmpdir, "v_ctrl"))
            
            context_engine = ConversationContextEngine(os.path.join(tmpdir, "context"))
            policy_mgr = PolicyManager(context_engine, os.path.join(tmpdir, "policy"))
            
            fusion = MultiModalFusionEngine(
                profiler, visual_ctrl, context_engine, policy_mgr,
                FusionStrategy.HYBRID_FUSION,
                os.path.join(tmpdir, "fusion")
            )
            
            assert fusion is not None

    def test_multimodal_processing(self):
        """Test multi-modal input processing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup all components
            profiler = EngagementProfiler(os.path.join(tmpdir, "engagement"))
            
            visual_registry = VisualCueModelRegistry(os.path.join(tmpdir, "visual"))
            model = FacialEmotionModel()
            visual_registry.register(model)
            model.initialize()
            
            camera = CameraManager(os.path.join(tmpdir, "camera"))
            visual_bonding = VisualBondingProtocol(visual_registry, camera,
                                                   os.path.join(tmpdir, "v_bonding"))
            visual_ctrl = VisualController(visual_registry, camera, visual_bonding,
                                          os.path.join(tmpdir, "v_ctrl"))
            
            context_engine = ConversationContextEngine(os.path.join(tmpdir, "context"))
            policy_mgr = PolicyManager(context_engine, os.path.join(tmpdir, "policy"))
            
            fusion = MultiModalFusionEngine(
                profiler, visual_ctrl, context_engine, policy_mgr,
                FusionStrategy.HYBRID_FUSION,
                os.path.join(tmpdir, "fusion")
            )
            
            # Process input
            user_id = "test_user"
            session_id = context_engine.start_session(user_id)
            
            input_data = MultiModalInput(
                text_input="I'm happy today!",
                visual_frame=np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            )
            
            fused = fusion.process_multimodal_input(user_id, session_id, input_data)
            
            assert fused is not None
            assert fused.user_id == user_id
            assert fused.overall_emotional_state is not None


class TestConfiguration:
    """Tests for configuration system"""

    def test_config_creation(self):
        """Test configuration creation"""
        config = GodTierConfig()
        assert config.version == "1.0.0"
        assert config.voice_model.enabled is True

    def test_config_manager(self):
        """Test configuration manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.yaml")
            manager = ConfigurationManager(config_file)
            
            # Save config
            assert manager.save_config() is True
            assert os.path.exists(config_file)
            
            # Load config
            loaded_config = manager.load_config()
            assert loaded_config.version == manager.config.version

    def test_config_validation(self):
        """Test configuration validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test_config.yaml")
            manager = ConfigurationManager(config_file)
            
            is_valid, errors = manager.validate_config()
            assert is_valid is True
            assert len(errors) == 0


class TestIntegratedSystem:
    """Tests for fully integrated God Tier system"""

    def test_system_initialization(self):
        """Test system initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create custom config
            config = GodTierConfig()
            config.storage.base_dir = tmpdir
            
            system = GodTierIntegratedSystem(config)
            
            # Initialize
            success = system.initialize()
            assert success is True
            assert system.status.initialized is True

    def test_system_components(self):
        """Test all system components are initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = GodTierConfig()
            config.storage.base_dir = tmpdir
            
            system = GodTierIntegratedSystem(config)
            system.initialize()
            
            # Check components
            assert system.voice_registry is not None
            assert system.engagement_profiler is not None
            assert system.visual_registry is not None
            assert system.context_engine is not None
            assert system.policy_manager is not None
            assert system.fusion_engine is not None

    def test_user_interaction_processing(self):
        """Test end-to-end user interaction processing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = GodTierConfig()
            config.storage.base_dir = tmpdir
            
            system = GodTierIntegratedSystem(config)
            system.initialize()
            
            # Process interaction
            user_id = "test_user"
            text_input = "Hello, how are you?"
            frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
            
            result = system.process_user_interaction(user_id, text_input, frame)
            
            assert result.get("success") is True
            assert "response" in result
            assert "fused_context" in result

    def test_system_shutdown(self):
        """Test graceful system shutdown"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = GodTierConfig()
            config.storage.base_dir = tmpdir
            
            system = GodTierIntegratedSystem(config)
            system.initialize()
            
            # Shutdown should not raise exceptions
            system.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
