
"""
AI Clinical Scribe - Multilingual AI Pipeline

Recording language:
    Language spoken in the audio.

Report language:
    Language selected by the doctor for the clinical note.

Supported languages:
    English, Hindi, Telugu.
"""

import logging

from ai.speech_to_text import transcribe_audio

from ai.transcript_processor import (
    clean_transcript,
    detect_language,
    split_into_sentences,
    organize_conversation,
)

from ai.clinical_extractor import extract_medical_information
from ai.note_generator import generate_clinical_note


logger = logging.getLogger(__name__)


SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
}


# =========================================================
# LANGUAGE HELPERS
# =========================================================

def normalize_language(language):
    """Normalize a doctor's report-language selection."""

    aliases = {
        "english": "English",
        "en": "English",
        "hindi": "Hindi",
        "hi": "Hindi",
        "telugu": "Telugu",
        "te": "Telugu",
    }

    if not language:
        return "English"

    return aliases.get(str(language).strip().lower(), "English")


def normalize_recording_language(language):
    """
    Return Whisper's language code.

    None means automatic language detection.
    """

    if language is None or not str(language).strip():
        return None

    value = str(language).strip().lower()

    aliases = {
        "english": "en",
        "en": "en",
        "hindi": "hi",
        "hi": "hi",
        "telugu": "te",
        "te": "te",
        "auto": None,
        "automatic": None,
    }

    if value not in aliases:
        raise ValueError(
            "Recording language must be English, Hindi, Telugu, "
            "or Auto."
        )

    return aliases[value]


# =========================================================
# EXTRACTOR OUTPUT VALIDATION
# =========================================================

def validate_medical_information(information):
    """
    Normalize extractor output without inventing clinical facts.
    """

    if not isinstance(information, dict):
        logger.warning(
            "Extractor returned an unexpected result type."
        )
        information = {}

    result = {
        "age": None,
        "symptoms": [],
        "duration": None,
        "severity": "Not mentioned",
        "allergies": "Not mentioned",
        "medications": [],
        "medical_history": [],
        "investigations": [],
        "diagnosis": [],
        "plan": [],
    }

    result.update(information)

    list_fields = [
        "symptoms",
        "medications",
        "medical_history",
        "investigations",
        "diagnosis",
        "plan",
    ]

    for field in list_fields:
        value = result.get(field)

        if value is None:
            result[field] = []
        elif isinstance(value, list):
            result[field] = value
        else:
            result[field] = [value]

    return result


# =========================================================
# AUDIO PIPELINE
# =========================================================

def process_audio(
    audio_file,
    report_language="English",
    recording_language=None,
):
    """
    Process an audio consultation.

    report_language:
        Doctor's preferred output language.

    recording_language:
        Spoken language: English, Hindi, Telugu, or None
        for automatic detection.

    The two language settings are independent.
    """

    if not audio_file:
        raise ValueError("Audio file path cannot be empty.")

    selected_report_language = normalize_language(
        report_language
    )

    selected_recording_language = normalize_recording_language(
        recording_language
    )

    logger.info("Starting audio transcription.")

    # 1. Transcribe audio using Whisper.
    transcript = transcribe_audio(
        audio_file,
        language=selected_recording_language,
    )

    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError(
            "Speech recognition did not return a transcript."
        )

    # 2. Process the recognized transcript.
    result = process_transcript(
        transcript=transcript,
        report_language=selected_report_language,
    )

    # Preserve the explicitly selected recording language in
    # the response when the doctor supplied one.
    if selected_recording_language:
        result["recording_language"] = {
            "en": "English",
            "hi": "Hindi",
            "te": "Telugu",
        }[selected_recording_language]

    return result


# =========================================================
# TRANSCRIPT PIPELINE
# =========================================================

def process_transcript(
    transcript,
    report_language="English",
):
    """
    Process an existing transcript without requiring audio.
    """

    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("Transcript cannot be empty.")

    selected_report_language = normalize_language(
        report_language
    )

    # 1. Clean the transcript.
    cleaned_transcript = clean_transcript(transcript)

    if (
        not isinstance(cleaned_transcript, str)
        or not cleaned_transcript.strip()
    ):
        raise ValueError(
            "Transcript cleaning returned empty text."
        )

    # 2. Detect the recording language.
    try:
        recording_language = detect_language(cleaned_transcript)
    except Exception:
        logger.exception("Language detection failed.")
        recording_language = "Unknown"

    if not recording_language:
        recording_language = "Unknown"

    # 3. Split into sentences.
    try:
        sentences = split_into_sentences(cleaned_transcript)
        if sentences is None:
            sentences = []
    except Exception:
        logger.exception("Sentence splitting failed.")
        sentences = [cleaned_transcript]

    # 4. Organize the conversation.
    try:
        conversation = organize_conversation(cleaned_transcript)
        if conversation is None:
            conversation = cleaned_transcript
    except Exception:
        logger.exception("Conversation organization failed.")
        conversation = cleaned_transcript

    # 5. Extract medical information.
    medical_information = extract_medical_information(
        cleaned_transcript
    )

    medical_information = validate_medical_information(
        medical_information
    )

    fields_with_information = [
        "age",
        "symptoms",
        "duration",
        "medications",
        "medical_history",
        "investigations",
        "diagnosis",
        "plan",
    ]

    extracted_count = sum(
        bool(medical_information.get(field))
        for field in fields_with_information
    )

    if extracted_count == 0:
        logger.warning(
            "No clinical details were extracted. "
            "Check transcript quality and clinical_extractor.py."
        )

    # 6. Generate the note in the doctor's selected language.
    clinical_note = generate_clinical_note(
        medical_information,
        selected_report_language,
    )

    # 7. Return the established response structure.
    return {
        "transcript": transcript,
        "cleaned_transcript": cleaned_transcript,
        "recording_language": recording_language,
        "report_language": selected_report_language,
        "language": selected_report_language,
        "sentences": sentences,
        "conversation": conversation,
        "medical_information": medical_information,
        "clinical_note": clinical_note,
    }