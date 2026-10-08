from fastapi import APIRouter
from backend.schemas import HealthResponse
from backend.services.speech import speech_service

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    """
    Returns system health, Whisper model load state, and FFmpeg binary availability.
    """
    return HealthResponse(
        status="ok",
        whisper_loaded=speech_service.is_model_loaded(),
        ffmpeg_available=speech_service.is_ffmpeg_available(),
        version="1.0.0"
    )
