"""
Voice assistant module providing text-to-speech and speech-to-text capabilities
for real-time conversational AI interaction.
"""

import os
import threading
import queue
from typing import Optional, Callable

# Lazy imports for optional dependencies - set to None if not available
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class VoiceAssistant:
    """Voice assistant with text-to-speech and speech recognition capabilities."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the voice assistant.

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self._tts_engine = None
        self._recognizer = None
        self._microphone = None
        self._is_listening = False
        self._listen_thread = None
        self._speech_queue = queue.Queue()
        self._on_speech_recognized: Optional[Callable[[str], None]] = None
        self._tts_lock = threading.Lock()

    def _init_tts(self):
        """Initialize text-to-speech engine lazily."""
        if self._tts_engine is None:
            if pyttsx3 is None:
                raise RuntimeError("pyttsx3 is not installed. Install with: pip install pyttsx3")
            try:
                self._tts_engine = pyttsx3.init()
                # Configure voice properties
                self._tts_engine.setProperty('rate', 175)  # Words per minute
                self._tts_engine.setProperty('volume', 0.9)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize TTS engine: {e}")

    def _init_recognizer(self):
        """Initialize speech recognizer lazily."""
        if self._recognizer is None:
            if sr is None:
                raise RuntimeError(
                    "SpeechRecognition is not installed. Install with: pip install SpeechRecognition"
                )
            try:
                self._recognizer = sr.Recognizer()
                self._microphone = sr.Microphone()
                # Adjust for ambient noise initially
                with self._microphone as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize speech recognizer: {e}")

    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it.

        Args:
            text: The text to speak.

        Returns:
            True if successful, False otherwise.
        """
        if not text:
            return False

        try:
            self._init_tts()
            with self._tts_lock:
                self._tts_engine.say(text)
                self._tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"TTS error: {e}")
            return False

    def speak_async(self, text: str) -> None:
        """
        Convert text to speech asynchronously.

        Args:
            text: The text to speak.
        """
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()

    def listen_once(self, timeout: int = 5, phrase_limit: int = 15) -> Optional[str]:
        """
        Listen for a single speech input and convert to text.

        Args:
            timeout: Maximum seconds to wait for speech to start.
            phrase_limit: Maximum seconds for a phrase.

        Returns:
            Recognized text or None if recognition failed.
        """
        try:
            self._init_recognizer()

            with self._microphone as source:
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

            # Try Google Speech Recognition (free, no API key needed)
            text = self._recognizer.recognize_google(audio)
            return text

        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None

    def start_continuous_listening(
        self,
        callback: Callable[[str], None],
        timeout: int = 5,
        phrase_limit: int = 15
    ) -> bool:
        """
        Start continuous speech recognition in background.

        Args:
            callback: Function to call with recognized text.
            timeout: Maximum seconds to wait for speech to start.
            phrase_limit: Maximum seconds for a phrase.

        Returns:
            True if listening started successfully.
        """
        if self._is_listening:
            return False

        self._on_speech_recognized = callback
        self._is_listening = True

        def listen_loop():
            while self._is_listening:
                text = self.listen_once(timeout=timeout, phrase_limit=phrase_limit)
                if text and self._on_speech_recognized:
                    self._on_speech_recognized(text)

        self._listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self._listen_thread.start()
        return True

    def stop_listening(self) -> None:
        """Stop continuous speech recognition."""
        self._is_listening = False
        if self._listen_thread:
            self._listen_thread.join(timeout=2)
            self._listen_thread = None

    def get_ai_response(self, user_message: str, context: list = None) -> str:
        """
        Get conversational AI response using OpenAI.

        Args:
            user_message: The user's message.
            context: Previous conversation messages.

        Returns:
            AI response text.
        """
        if not self.api_key:
            return "OpenAI API key not configured. Please set OPENAI_API_KEY."

        if OpenAI is None:
            return "OpenAI library is not installed. Install with: pip install openai"

        try:
            client = OpenAI(api_key=self.api_key)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI voice assistant. Keep responses "
                        "concise and conversational since they will be spoken aloud. "
                        "Avoid long lists or technical jargon unless asked."
                    )
                }
            ]

            if context:
                messages.extend(context)

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error getting AI response: {str(e)}"

    def converse(
        self,
        user_message: str,
        context: list = None,
        speak_response: bool = True
    ) -> str:
        """
        Have a conversational exchange with the AI.

        Args:
            user_message: The user's message (text or from speech).
            context: Previous conversation messages.
            speak_response: Whether to speak the response aloud.

        Returns:
            AI response text.
        """
        response = self.get_ai_response(user_message, context)

        if speak_response:
            self.speak_async(response)

        return response

    def set_voice_rate(self, rate: int) -> None:
        """
        Set the speech rate.

        Args:
            rate: Words per minute (default is 175).
        """
        self._init_tts()
        self._tts_engine.setProperty('rate', rate)

    def set_voice_volume(self, volume: float) -> None:
        """
        Set the speech volume.

        Args:
            volume: Volume level from 0.0 to 1.0.
        """
        self._init_tts()
        self._tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))

    def get_available_voices(self) -> list:
        """
        Get list of available voices.

        Returns:
            List of voice dictionaries with 'id' and 'name'.
        """
        try:
            self._init_tts()
            voices = self._tts_engine.getProperty('voices')
            return [{'id': v.id, 'name': v.name} for v in voices]
        except Exception:
            return []

    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use.

        Args:
            voice_id: Voice ID from get_available_voices().

        Returns:
            True if successful.
        """
        try:
            self._init_tts()
            self._tts_engine.setProperty('voice', voice_id)
            return True
        except Exception:
            return False

    @property
    def is_listening(self) -> bool:
        """Check if currently listening for speech."""
        return self._is_listening
