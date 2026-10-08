
"""
AI Clinical Scribe - Speech to Text

Supports:
    English: en
    Hindi:   hi
    Telugu:  te

When language=None, Whisper automatically detects the spoken language.
"""

import os
import logging
import whisper

logger = logging.getLogger(__name__)

_model = None


def get_model():
    """Load Whisper once and reuse the model."""
    global _model

    if _model is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        logger.info("Loading Whisper model: %s", model_name)
        _model = whisper.load_model(model_name)

    return _model


def transcribe_audio(audio_file, language=None):
    """
    Transcribe an audio file.

    Args:
        audio_file: Path to the audio file.
        language: Optional spoken-language code: en, hi, or te.
                  None enables automatic language detection.

    Returns:
        Recognized transcript as a string.
    """

    if not audio_file:
        raise ValueError("Audio file path cannot be empty.")

    if not os.path.isfile(audio_file):
        raise FileNotFoundError(
            f"Audio file not found: {audio_file}"
        )

    language_aliases = {
        "english": "en",
        "en": "en",
        "hindi": "hi",
        "hi": "hi",
        "telugu": "te",
        "te": "te",
        "auto": None,
        "automatic": None,
    }

    if language is not None:
        language = str(language).strip().lower()

        if language not in language_aliases:
            raise ValueError(
                "Unsupported recording language. "
                "Use English, Hindi, Telugu, or None for automatic detection."
            )

        language = language_aliases[language]

    model = get_model()

    options = {
        "task": "transcribe",
        "fp16": False,
        "verbose": False,
    }

    if language is not None:
        options["language"] = language

    try:
        result = model.transcribe(audio_file, **options)
    except Exception as exc:
        logger.exception("Whisper transcription failed.")
        raise RuntimeError(
            "Could not transcribe the audio. "
            "Check the audio format, file and Whisper installation."
        ) from exc

    transcript = result.get("text", "").strip()

    if not transcript:
        raise ValueError(
            "Whisper returned an empty transcript. "
            "Try a clearer recording or check the spoken-language setting."
        )

    detected_language = result.get("language", "unknown")

    logger.info(
        "Transcription completed. Detected language: %s",
        detected_language,
    )

    return transcript