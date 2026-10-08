from uuid import UUID
from services.mock_transcription import transcribe_audio_mock
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/api/audio", tags=["Audio"])

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".webm", ".ogg", ".flac", ".mp4"
}

MAX_FILE_SIZE = 25 * 1024 * 1024


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format"
        )

    file_id = str(uuid4())
    saved_name = f"{file_id}{extension}"
    destination = UPLOAD_DIR / saved_name
    size = 0

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                size += len(chunk)

                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File exceeds the 25 MB limit"
                    )

                output.write(chunk)

        if size == 0:
            destination.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        return {
            "success": True,
            "file_id": file_id,
            "filename": saved_name,
            "original_filename": file.filename,
            "size_bytes": size,
            "message": "Audio uploaded successfully"
        }

    except HTTPException:
        destination.unlink(missing_ok=True)
        raise

    except OSError:
        destination.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Could not save uploaded file"
        )

    finally:
        await file.close()

@router.post("/transcribe/{file_id}")
async def transcribe_audio(file_id: str):
    try:
        validated_id = str(UUID(file_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid file_id"
        )

    matching_files = list(UPLOAD_DIR.glob(f"{validated_id}.*"))

    if not matching_files or not matching_files[0].is_file():
        raise HTTPException(
            status_code=404,
            detail="Uploaded audio file not found. Upload a file first."
        )
    return transcribe_audio_mock(validated_id)
