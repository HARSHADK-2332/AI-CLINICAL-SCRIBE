import os
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.schemas import TranscribeResponse, TranscriptSegment
from backend.services.speech import speech_service, FFmpegNotFoundError

router = APIRouter(prefix="/api", tags=["Speech"])

# Max upload limit: 50MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".webm"}


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio_endpoint(
    audio: UploadFile = File(..., description="Audio file of consultation"),
    language: Optional[str] = Form(None, description="Optional target language: en | hi | te")
):
    """
    Transcribes audio into timestamped speaker turns using Whisper and SpeechToTextService.
    Returns clear, actionable errors if FFmpeg is not detected.
    """
    if not speech_service.is_ffmpeg_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "FFmpeg is missing on the host system. Whisper requires FFmpeg for audio transcoding. "
                "Instructions to fix: "
                "1. Windows: Run 'winget install Gyan.FFmpeg' or extract FFmpeg and add bin/ to system PATH. "
                "2. macOS: Run 'brew install ffmpeg'. "
                "3. Linux: Run 'sudo apt install ffmpeg'. "
                "To test the frontend without installing FFmpeg, enable mock mode by setting VITE_USE_MOCK=true."
            )
        )

    # Validate file extension
    ext = os.path.splitext(audio.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio extension '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Read and validate size
    content = await audio.read()
    if len(content) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file size exceeds maximum limit of {MAX_AUDIO_SIZE // (1024 * 1024)} MB."
        )

    # Write to temp file for Whisper processing
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = speech_service.transcribe(tmp_path, language=language)
        segments = [
            TranscriptSegment(
                speaker=seg["speaker"],
                start=seg["start"],
                end=seg["end"],
                text=seg["text"]
            )
            for seg in result["segments"]
        ]
        return TranscribeResponse(
            segments=segments,
            language=result["language"],
            duration=result.get("duration")
        )
    except FFmpegNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@router.get("/sample-audio/{filename}")
def get_sample_audio(filename: str):
    """Serve included sample audio files (test_audio.wav, multilingual_conversation.wav)."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    safe_files = {"test_audio.wav", "multilingual_conversation.wav"}
    if filename not in safe_files:
        raise HTTPException(status_code=404, detail="Sample audio file not found.")
    file_path = os.path.join(base_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server.")
    from fastapi.responses import FileResponse
    return FileResponse(file_path, media_type="audio/wav")


@router.post("/sample-audio/{filename}/transcribe", response_model=TranscribeResponse)
def transcribe_sample_audio(filename: str, language: Optional[str] = None):
    """Directly transcribes an included sample audio file using real Whisper."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    safe_files = {"test_audio.wav", "multilingual_conversation.wav"}
    if filename not in safe_files:
        raise HTTPException(status_code=404, detail="Sample audio file not found.")
    file_path = os.path.join(base_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server.")

    result = speech_service.transcribe(file_path, language=language)
    segments = [
        TranscriptSegment(
            speaker=seg["speaker"],
            start=seg["start"],
            end=seg["end"],
            text=seg["text"]
        )
        for seg in result["segments"]
    ]
    return TranscribeResponse(
        segments=segments,
        language=result["language"],
        duration=result.get("duration")
    )
