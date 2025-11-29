"""Tests for the voice assistant module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os


def test_voice_assistant_import():
    """Test that VoiceAssistant can be imported."""
    from app.core.voice_assistant import VoiceAssistant
    assert VoiceAssistant is not None


def test_voice_assistant_init():
    """Test VoiceAssistant initialization."""
    from app.core.voice_assistant import VoiceAssistant

    # Test with explicit API key
    va = VoiceAssistant(api_key="test-key")
    assert va.api_key == "test-key"
    assert va._tts_engine is None  # Lazy initialization
    assert va._recognizer is None  # Lazy initialization
    assert va.is_listening is False


def test_voice_assistant_init_from_env():
    """Test VoiceAssistant uses environment variable for API key."""
    from app.core.voice_assistant import VoiceAssistant

    with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-test-key'}):
        va = VoiceAssistant()
        assert va.api_key == 'env-test-key'


def test_get_ai_response_no_api_key():
    """Test get_ai_response returns error message when no API key."""
    from app.core.voice_assistant import VoiceAssistant

    va = VoiceAssistant(api_key=None)
    # Ensure environment variable is not set for this test
    with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=True):
        va_no_key = VoiceAssistant()
        va_no_key.api_key = None
        response = va_no_key.get_ai_response("Hello")
        assert "API key not configured" in response


def test_speak_empty_text():
    """Test speak returns False for empty text."""
    from app.core.voice_assistant import VoiceAssistant

    va = VoiceAssistant()
    result = va.speak("")
    assert result is False
    result = va.speak(None)
    assert result is False


@patch('pyttsx3.init')
def test_speak_success(mock_pyttsx3_init):
    """Test successful text-to-speech."""
    from app.core.voice_assistant import VoiceAssistant

    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    va = VoiceAssistant()
    result = va.speak("Hello, world!")

    assert result is True
    mock_engine.say.assert_called_once_with("Hello, world!")
    mock_engine.runAndWait.assert_called_once()


@patch('pyttsx3.init')
def test_set_voice_rate(mock_pyttsx3_init):
    """Test setting voice rate."""
    from app.core.voice_assistant import VoiceAssistant

    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    va = VoiceAssistant()
    va.set_voice_rate(200)

    mock_engine.setProperty.assert_called_with('rate', 200)


@patch('pyttsx3.init')
def test_set_voice_volume(mock_pyttsx3_init):
    """Test setting voice volume."""
    from app.core.voice_assistant import VoiceAssistant

    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    va = VoiceAssistant()
    va.set_voice_volume(0.5)

    mock_engine.setProperty.assert_called_with('volume', 0.5)


@patch('pyttsx3.init')
def test_set_voice_volume_clamped(mock_pyttsx3_init):
    """Test volume is clamped to valid range."""
    from app.core.voice_assistant import VoiceAssistant

    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    va = VoiceAssistant()

    # Test upper bound
    va.set_voice_volume(1.5)
    mock_engine.setProperty.assert_called_with('volume', 1.0)

    # Test lower bound
    va.set_voice_volume(-0.5)
    mock_engine.setProperty.assert_called_with('volume', 0.0)


@patch('pyttsx3.init')
def test_get_available_voices(mock_pyttsx3_init):
    """Test getting available voices."""
    from app.core.voice_assistant import VoiceAssistant

    mock_voice = MagicMock()
    mock_voice.id = "voice1"
    mock_voice.name = "Voice One"

    mock_engine = MagicMock()
    mock_engine.getProperty.return_value = [mock_voice]
    mock_pyttsx3_init.return_value = mock_engine

    va = VoiceAssistant()
    voices = va.get_available_voices()

    assert len(voices) == 1
    assert voices[0]['id'] == "voice1"
    assert voices[0]['name'] == "Voice One"


@patch('pyttsx3.init')
def test_set_voice(mock_pyttsx3_init):
    """Test setting a specific voice."""
    from app.core.voice_assistant import VoiceAssistant

    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    va = VoiceAssistant()
    result = va.set_voice("voice1")

    assert result is True
    mock_engine.setProperty.assert_called_with('voice', 'voice1')


def test_is_listening_property():
    """Test is_listening property."""
    from app.core.voice_assistant import VoiceAssistant

    va = VoiceAssistant()
    assert va.is_listening is False

    va._is_listening = True
    assert va.is_listening is True


def test_stop_listening():
    """Test stop_listening method."""
    from app.core.voice_assistant import VoiceAssistant

    va = VoiceAssistant()
    va._is_listening = True

    va.stop_listening()

    assert va._is_listening is False


@patch('openai.OpenAI')
def test_get_ai_response_success(mock_openai_class):
    """Test successful AI response."""
    from app.core.voice_assistant import VoiceAssistant

    # Setup mock
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello! How can I help you?"
    mock_client.chat.completions.create.return_value = mock_response

    va = VoiceAssistant(api_key="test-key")
    response = va.get_ai_response("Hi there")

    assert response == "Hello! How can I help you?"
    mock_client.chat.completions.create.assert_called_once()


@patch('openai.OpenAI')
def test_get_ai_response_with_context(mock_openai_class):
    """Test AI response with conversation context."""
    from app.core.voice_assistant import VoiceAssistant

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Your name is Alice."
    mock_client.chat.completions.create.return_value = mock_response

    va = VoiceAssistant(api_key="test-key")
    context = [
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Nice to meet you, Alice!"}
    ]
    response = va.get_ai_response("What's my name?", context=context)

    # Verify context was included in the call
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs['messages']
    assert len(messages) == 4  # system + 2 context + user message


@patch('openai.OpenAI')
def test_get_ai_response_error_handling(mock_openai_class):
    """Test AI response error handling."""
    from app.core.voice_assistant import VoiceAssistant

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    va = VoiceAssistant(api_key="test-key")
    response = va.get_ai_response("Hello")

    assert "Error getting AI response" in response


@patch('pyttsx3.init')
@patch('openai.OpenAI')
def test_converse_with_speech(mock_openai_class, mock_pyttsx3_init):
    """Test converse method with speech output."""
    from app.core.voice_assistant import VoiceAssistant

    # Setup TTS mock
    mock_engine = MagicMock()
    mock_pyttsx3_init.return_value = mock_engine

    # Setup OpenAI mock
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello!"
    mock_client.chat.completions.create.return_value = mock_response

    va = VoiceAssistant(api_key="test-key")
    response = va.converse("Hi", speak_response=True)

    assert response == "Hello!"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
