
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from models.schemas import (
    ClinicalNoteRequest,
    PatientRequest,
    ScribeProcessRequest,
    TranscriptRequest,
)
from services.scribe_service import generate_sample_note

router = APIRouter(tags=["Clinical Scribe"])

patients = {}
transcripts = {}


@router.post("/api/transcript")
def submit_transcript(request: TranscriptRequest):
    cleaned = request.transcript.strip()

    if not cleaned:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    transcript_id = str(uuid4())
    transcripts[transcript_id] = cleaned

    return {
        "success": True,
        "transcript_id": transcript_id,
        "transcript": cleaned,
        "message": "Transcript received",
    }


@router.post("/api/patient")
def create_patient(request: PatientRequest):
    patient = request.model_dump(mode="json")
    patients[request.patient_id] = patient

    return {
        "success": True,
        "patient": patient,
        "message": "Demo patient information saved",
    }


@router.post("/api/clinical-note")
def create_clinical_note(request: ClinicalNoteRequest):
    try:
        note = generate_sample_note(request.transcript)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "success": True,
        "patient_id": request.patient_id,
        "note": note,
    }


@router.post("/api/scribe/process")
def process_scribe(request: ScribeProcessRequest):
    if not request.transcript or not request.transcript.strip():
        if request.file_id:
            raise HTTPException(
                status_code=501,
                detail="Audio transcription is not integrated yet. "
                "Connect the AI-core service first.",
            )

        raise HTTPException(
            status_code=400,
            detail="Provide a non-empty transcript",
        )

    try:
        note = generate_sample_note(request.transcript)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "success": True,
        "status": "demo",
        "note": note,
        "message": "Demo workflow completed; AI integration is pending",
    }