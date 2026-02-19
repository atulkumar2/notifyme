"""
Offline Text-to-Speech manager using pyttsx3 (SAPI5 on Windows).

- Runs a background worker thread with a queue to keep TTS non-blocking.
- Attempts to use a Hindi voice when requested or when language='auto' and a Hindi
  voice is available; otherwise falls back to English/default voice.
- Gracefully degrades if pyttsx3 is not installed or fails: no exceptions escape
  public methods and the application won't crash.

This module is written to be PyInstaller-friendly: it imports pyttsx3 only when
needed and performs speech work in a single dedicated thread.
"""

from __future__ import annotations

import logging
import queue
import threading

from notifyme_app.constants import APP_NAME

try:
    import pyttsx3
except Exception:  # pragma: no cover - environment dependent
    pyttsx3 = None


class TTSManager:
    """Background Text-to-Speech manager."""

    def __init__(self) -> None:
        self._enabled = bool(pyttsx3)
        self._queue = queue.Queue()
        self._thread = threading.Thread(
            target=self._worker, daemon=True, name=f"{APP_NAME}-TTS"
        )
        self._stop_event = threading.Event()
        if self._enabled:
            self._thread.start()
            logging.info("TTS manager started (fresh engine per request)")
        else:
            logging.info("pyttsx3 not available; TTS disabled")

    def _find_voice_for_lang(self, lang: str, voices: list):
        """Return a voice.id matching the requested language if available.

        lang examples: 'hi' (Hindi), 'en' (English), 'auto' (prefer hi then en)
        """
        if not voices:
            return None

        if lang == "auto":
            # prefer Hindi if present
            candidate = self._find_voice_for_lang("hi", voices)
            if candidate:
                return candidate
            return self._find_voice_for_lang("en", voices)

        lang = lang.lower()
        for v in voices:
            try:
                # voice.languages may be a list of bytes like b'\x05en-us'
                langs = getattr(v, "languages", []) or []
                langs_str = " ".join(
                    [
                        (
                            l.decode("utf-8")
                            if isinstance(l, (bytes, bytearray))
                            else str(l)
                        ).lower()
                        for l in langs
                    ]
                )
                name = getattr(v, "name", "") or ""
                if (
                    lang in langs_str
                    or lang in name.lower()
                    or lang in getattr(v, "id", "").lower()
                ):
                    return getattr(v, "id", None)
            except Exception:
                continue
        return None

    def speak(self, text: str, lang: str = "auto") -> None:
        """Enqueue text to be spoken. Non-blocking.

        If TTS is disabled or not available, this is a no-op and will not raise.
        """
        if not text:
            return
        if not self._enabled:
            logging.debug("TTS speak requested but disabled")
            return
        self._queue.put((text, lang))

    # backward compatible name
    speak_async = speak

    def _worker(self) -> None:
        """Worker thread that performs speech synthesis."""
        while not self._stop_event.is_set():
            try:
                text, lang = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            # Create a fresh engine for each speak request
            engine = None
            try:
                logging.debug("Creating fresh TTS engine for speech request")
                engine = pyttsx3.init("sapi5")
                voices = engine.getProperty("voices") or []

                voice_id = self._find_voice_for_lang(lang or "auto", voices)
                if voice_id:
                    try:
                        engine.setProperty("voice", voice_id)
                        logging.debug("Set voice to %s", voice_id)
                    except Exception:
                        logging.debug("Failed to set voice %s, using default", voice_id)

                logging.debug("TTS speaking: %s (lang=%s)", text, lang)
                engine.say(text)
                engine.runAndWait()
                logging.debug("TTS speak completed successfully")
            except Exception as e:
                logging.error("Error during TTS speak: %s", e)
            finally:
                # Always clean up the engine
                if engine:
                    try:
                        engine.stop()
                    except Exception:
                        pass

    def stop(self) -> None:
        """Stop the TTS worker thread."""
        if not self._enabled:
            return
        logging.info("Stopping TTS manager")
        self._stop_event.set()
        self._thread.join(timeout=1.0)


# Module-level singleton
_tts_manager = None


def get_tts_manager() -> TTSManager:
    """Return a singleton TTSManager instance."""
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager
