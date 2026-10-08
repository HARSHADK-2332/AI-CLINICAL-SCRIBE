from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.ai_service import run_audio_pipeline


router = APIRouter(
    prefix="/api/audio",
    tags=["Audio"]
)


# Folder where uploaded audio files are stored
UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Maximum file size: 25 MB
MAX_FILE_SIZE = 25 * 1024 * 1024


# Supported audio formats
ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".ogg",
    ".flac",
    ".mp4",
}


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...)
):
    # Check whether a file was selected
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    # Get file extension
    extension = Path(
        file.filename
    ).suffix.lower()

    # Validate file format
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format. "
                "Supported formats: "
                "wav, mp3, m4a, webm, ogg, flac, mp4."
            )
        )

    # Read uploaded file
    file_content = await file.read()

    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 25 MB."
        )

    # Generate unique file ID
    file_id = uuid4()

    # Create file path
    file_path = UPLOAD_DIR / f"{file_id}{extension}"

    try:
        # Save uploaded audio
        with open(
            file_path,
            "wb"
        ) as buffer:
            buffer.write(file_content)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save audio file: {str(exc)}"
        )

    return {
        "success": True,
        "file_id": str(file_id),
        "filename": file.filename,
        "file_type": extension,
        "file_size": len(file_content),
        "message": "Audio uploaded successfully."
    }


@router.post("/transcribe/{file_id}")
async def transcribe_audio(
    file_id: str
):
    # Validate UUID
    try:
        validated_id = str(
            UUID(file_id)
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid file_id."
        )

    # Find uploaded audio file
    matching_files = list(
        UPLOAD_DIR.glob(
            f"{validated_id}.*"
        )
    )

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail="Uploaded audio file not found."
        )

    # Get uploaded audio path
    audio_path = matching_files[0]

    try:
        # Run complete AI Clinical Scribe pipeline
        result = run_audio_pipeline(
            str(audio_path)
        )

        return {
            "success": True,
            "file_id": validated_id,
            "transcription_mode": "whisper",
            "is_real_transcription": True,
            "result": result
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(exc)}"
        )