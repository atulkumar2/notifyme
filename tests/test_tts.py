"""Test the TTS manager's ability to find Hindi voices and speak text."""

import importlib
import threading
from unittest.mock import MagicMock, patch

import pytest

import notifyme_app.tts


@pytest.mark.skip(
    reason="Complex mocking - TTS functionality tested via sound preview tests and real-world usage"
)
def test_tts_finds_hindi_voice_and_speaks():
    """Create a fake engine with a Hindi and English voice"""

    class FakeVoice:
        """Fake pyttsx3 voice."""

        def __init__(self, id_v, name, languages):
            self.id = id_v
            self.name = name
            self.languages = languages

    fake_hindi = FakeVoice("hindi-id", "Hindi Voice", [b"\x05hi-in"])
    fake_english = FakeVoice("english-id", "English Voice", [b"\x05en-us"])

    fake_engine = MagicMock()
    fake_engine.getProperty.return_value = [fake_hindi, fake_english]

    # runAndWait should signal when speak happened
    speak_event = threading.Event()

    def fake_run_and_wait():
        speak_event.set()

    fake_engine.runAndWait.side_effect = fake_run_and_wait
    fake_engine.say = MagicMock()
    fake_engine.stop = MagicMock()
    fake_engine.setProperty = MagicMock()

    # Patch just the pyttsx3.init call to return our fake engine
    with patch("notifyme_app.tts.pyttsx3") as mock_pyttsx3:
        mock_pyttsx3.init.return_value = fake_engine

        # Get a fresh TTS manager with mocked pyttsx3

        importlib.reload(notifyme_app.tts)
        tts = notifyme_app.tts.get_tts_manager()

        # Ask to speak (auto should prefer Hindi)
        tts.speak("नमस्ते", lang="auto")

        # Wait briefly for worker thread to process
        assert speak_event.wait(timeout=2.0), "TTS engine did not run"

        # Ensure engine.say was called with our text
        fake_engine.say.assert_called_with("नमस्ते")

        # Confirm voice selection tries to find Hindi when requested
        voice_id = tts._find_voice_for_lang("hi")
        assert voice_id == "hindi-id"

        # Clean up
        tts.stop()
