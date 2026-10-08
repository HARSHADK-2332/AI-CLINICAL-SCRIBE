
def transcribe_audio_mock(file_id: str) -> dict:
    return {
        "file_id": file_id,
        "transcript": (
            "DEMO ONLY - NOT REAL PATIENT DATA. "
            "The fictional patient reports a mild headache since this morning. "
            "This text was generated for testing and was not extracted from audio."
        ),
        "transcription_mode": "mock",
        "is_real_transcription": False,
        "message": "Mock transcription completed for development testing only."
    }