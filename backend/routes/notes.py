from typing import List, Optional
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    UploadFile,
    File,
    Form,
    status,
)

from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ClinicalNote, Patient
from backend.schemas import (
    NoteGenerateRequest,
    NoteResponse,
    NoteUpdateRequest,
    NoteCapabilities,
)

from backend.services.clinical import clinical_service
from backend.services.export import (
    export_note,
    FHIRNotImplementedError,
    ExportFormatError,
)

from backend.services.ai_service import run_audio_pipeline

from ai.note_generator import (
    format_value,
    translate_list,
    normalize_language,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/notes",
    tags=["Clinical Notes"],
)


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MAX_FILE_SIZE = 25 * 1024 * 1024

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".ogg",
    ".flac",
    ".mp4",
}


# ============================================================
# NOTE RESPONSE HELPER
# ============================================================

def _to_note_response(note: ClinicalNote) -> NoteResponse:
    """
    Convert database ClinicalNote object
    into API NoteResponse.
    """

    return NoteResponse(
        id=note.id,
        patient_id=note.patient_id,

        chief_complaint=note.chief_complaint,

        history_of_present_illness=(
            note.history_of_present_illness
        ),

        assessment=note.assessment,

        plan=note.plan,

        allergies=note.allergies,

        medications=note.medications,

        negated_findings=note.negated_findings,

        status=note.status,

        language=note.language,

        capabilities=NoteCapabilities(
            allergies=False,
            medications=False,
            negation=True,
            diarization=False,
        ),

        created_at=note.created_at,

        updated_at=note.updated_at,
    )


# ============================================================
# EXISTING: GENERATE NOTE FROM TRANSCRIPT
# ============================================================

@router.post(
    "/generate",
    response_model=NoteResponse,
)
def generate_note_endpoint(
    req: NoteGenerateRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a structured clinical note
    from transcript segments.

    The generated note is stored in SQLite.
    """

    segments_dict = [
        seg.model_dump()
        for seg in req.transcript
    ]

    generated = clinical_service.generate_note(
        segments_dict,
        language=req.language,
    )

    # --------------------------------------------------------
    # Create database note
    # --------------------------------------------------------

    db_note = ClinicalNote(
        patient_id=req.patient_id,

        chief_complaint=generated.get(
            "chief_complaint",
            "",
        ),

        history_of_present_illness=generated.get(
            "history_of_present_illness",
            "",
        ),

        assessment=generated.get(
            "assessment",
            "",
        ),

        status="draft",

        language=generated.get(
            "language",
            req.language or "en",
        ),
    )

    db_note.plan = generated.get(
        "plan",
        [],
    )

    db_note.allergies = generated.get(
        "allergies",
        [],
    )

    db_note.medications = generated.get(
        "medications",
        [],
    )

    db_note.negated_findings = generated.get(
        "negated_findings",
        [],
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    db.add(db_note)

    db.commit()

    db.refresh(db_note)

    return _to_note_response(
        db_note
    )


# ============================================================
# LOCALIZATION HELPERS
# ============================================================

def _normalize_list(value):
    """
    Convert None/string/list values into a list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _localized_history(
    medical_information,
    language,
):
    """
    Build a localized History of Present Illness
    for the doctor-facing response.
    """

    language = normalize_language(language)

    duration = medical_information.get(
        "duration"
    )

    severity = medical_information.get(
        "severity"
    )

    medical_history = medical_information.get(
        "medical_history"
    )

    parts = []

    labels = {
        "English": {
            "duration": "Duration",
            "severity": "Severity",
            "history": "Medical history",
        },
        "Hindi": {
            "duration": "अवधि",
            "severity": "गंभीरता",
            "history": "चिकित्सा इतिहास",
        },
        "Telugu": {
            "duration": "వ్యవధి",
            "severity": "తీవ్రత",
            "history": "వైద్య చరిత్ర",
        },
    }

    current_labels = labels[language]

    if duration:
        parts.append(
            f"{current_labels['duration']}: "
            f"{format_value(duration, language)}"
        )

    if severity:
        parts.append(
            f"{current_labels['severity']}: "
            f"{format_value(severity, language)}"
        )

    if medical_history:
        history_values = _normalize_list(
            medical_history
        )

        history_text = translate_list(
            history_values,
            language,
        )

        parts.append(
            f"{current_labels['history']}:\n"
            f"{history_text}"
        )

    if not parts:
        return format_value(
            None,
            language,
        )

    return "\n".join(parts)


def _localized_structured_note(
    medical_information,
    report_language,
):
    """
    Convert extracted canonical clinical information
    into doctor-selected report language.

    The original transcript remains unchanged.
    """

    language = normalize_language(
        report_language
    )

    symptoms = medical_information.get(
        "symptoms",
        [],
    )

    diagnosis = medical_information.get(
        "diagnosis",
        [],
    )

    plan = medical_information.get(
        "plan",
        [],
    )

    medications = medical_information.get(
        "medications",
        [],
    )

    investigations = medical_information.get(
        "investigations",
        [],
    )

    allergies = medical_information.get(
        "allergies"
    )

    return {
        "chief_complaint": translate_list(
            _normalize_list(symptoms),
            language,
        ),

        "history_of_present_illness": (
            _localized_history(
                medical_information,
                language,
            )
        ),

        "assessment": translate_list(
            _normalize_list(diagnosis),
            language,
        ),

        "plan": translate_list(
            _normalize_list(plan),
            language,
        ),

        "allergies": format_value(
            allergies,
            language,
        ),

        "medications": translate_list(
            _normalize_list(medications),
            language,
        ),

        "investigations": translate_list(
            _normalize_list(investigations),
            language,
        ),
    }


# ============================================================
# COMPLETE AI AUDIO → CLINICAL NOTE PIPELINE
# ============================================================

@router.post(
    "/process-audio",
)
async def process_audio_endpoint(
    file: UploadFile = File(...),

    patient_id: Optional[int] = Form(
        None
    ),

    language: Optional[str] = Form(
        None
    ),

    db: Session = Depends(get_db),
):
    """
    Complete AI Clinical Scribe pipeline.

    Audio
        ↓
    Whisper Speech-to-Text
        ↓
    Transcript Processing
        ↓
    Recording Language Detection
        ↓
    Clinical Information Extraction
        ↓
    Doctor-selected Report Language
        ↓
    Localized Clinical Note Generation
        ↓
    Database Storage

    Supported report languages:
        English
        Hindi
        Telugu

    Important:
        Recording language and report language
        are treated separately.
    """

    # ========================================================
    # VALIDATE FILE
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file selected.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_AUDIO_EXTENSIONS:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported audio format. "
                "Supported formats: "
                "wav, mp3, m4a, webm, ogg, flac, mp4."
            ),
        )

    # ========================================================
    # VALIDATE PATIENT
    # ========================================================

    if patient_id is not None:

        patient = (
            db.query(Patient)
            .filter(
                Patient.id == patient_id
            )
            .first()
        )

        if not patient:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Patient #{patient_id} "
                    "not found."
                ),
            )

    # ========================================================
    # READ AUDIO
    # ========================================================

    try:

        file_content = await file.read()

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Could not read audio file: "
                f"{str(exc)}"
            ),
        )

    # ========================================================
    # CHECK FILE SIZE
    # ========================================================

    if len(file_content) > MAX_FILE_SIZE:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Audio file must be "
                "less than 25 MB."
            ),
        )

    if len(file_content) == 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty.",
        )

    # ========================================================
    # SAVE TEMPORARY AUDIO
    # ========================================================

    file_id = uuid4()

    audio_path = (
        UPLOAD_DIR
        / f"{file_id}{extension}"
    )

    try:

        with open(
            audio_path,
            "wb",
        ) as buffer:

            buffer.write(
                file_content
            )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Could not save audio file: "
                f"{str(exc)}"
            ),
        )

    # ========================================================
    # DOCTOR REPORT LANGUAGE
    # ========================================================

    report_language = normalize_language(
        language or "English"
    )

    # ========================================================
    # RUN AI PIPELINE
    # ========================================================

    try:

        result = run_audio_pipeline(
            str(audio_path),
            report_language=report_language,
        )

    except Exception as exc:

        # Remove failed processing file
        if audio_path.exists():

            audio_path.unlink(
                missing_ok=True
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"AI processing failed: "
                f"{str(exc)}"
            ),
        )

    # ========================================================
    # GET AI RESULTS
    # ========================================================

    recording_language = result.get(
        "recording_language",
        "English",
    )

    report_language = normalize_language(
        result.get(
            "report_language",
            report_language,
        )
    )

    # Backward-compatible language value
    language = report_language

    medical_information = result.get(
        "medical_information",
        {},
    )

    clinical_note_text = result.get(
        "clinical_note",
        "",
    )

    transcript = result.get(
        "transcript",
        "",
    )

    cleaned_transcript = result.get(
        "cleaned_transcript",
        transcript,
    )

    # ========================================================
    # EXTRACT CLINICAL INFORMATION
    # ========================================================

    symptoms = medical_information.get(
        "symptoms",
        [],
    )

    duration = medical_information.get(
        "duration",
        None,
    )

    severity = medical_information.get(
        "severity",
        None,
    )

    allergies = medical_information.get(
        "allergies",
        None,
    )

    medications = medical_information.get(
        "medications",
        None,
    )

    medical_history = medical_information.get(
        "medical_history",
        None,
    )

    investigations = medical_information.get(
        "investigations",
        None,
    )

    diagnosis = medical_information.get(
        "diagnosis",
        None,
    )

    plan = medical_information.get(
        "plan",
        None,
    )

    # ========================================================
    # BUILD ORIGINAL CANONICAL DB FIELDS
    # ========================================================

    # Keep database values canonical/original.
    # The doctor-facing API response is localized separately.

    symptoms_list = _normalize_list(
        symptoms
    )

    if symptoms_list:

        chief_complaint = ", ".join(
            str(item)
            for item in symptoms_list
            if item
        )

    else:

        chief_complaint = (
            "Not mentioned"
        )

    if not chief_complaint:

        chief_complaint = (
            "Not mentioned"
        )

    # ========================================================
    # BUILD HISTORY OF PRESENT ILLNESS
    # ========================================================

    history_parts = []

    if duration:

        history_parts.append(
            f"Duration: {duration}"
        )

    if severity:

        history_parts.append(
            f"Severity: {severity}"
        )

    if medical_history:

        if isinstance(
            medical_history,
            list,
        ):

            history_parts.append(
                "Medical history: "
                + ", ".join(
                    str(item)
                    for item in medical_history
                )
            )

        else:

            history_parts.append(
                "Medical history: "
                + str(medical_history)
            )

    if history_parts:

        history_of_present_illness = (
            "; ".join(history_parts)
        )

    else:

        history_of_present_illness = (
            "Not mentioned"
        )

    # ========================================================
    # BUILD ASSESSMENT
    # ========================================================

    diagnosis_list = _normalize_list(
        diagnosis
    )

    if diagnosis_list:

        assessment = ", ".join(
            str(item)
            for item in diagnosis_list
            if item
        )

    else:

        assessment = (
            "Diagnosis not mentioned. "
            "Clinical review required."
        )

    # ========================================================
    # NORMALIZE LIST FIELDS
    # ========================================================

    allergies_list = _normalize_list(
        allergies
    )

    medications_list = _normalize_list(
        medications
    )

    plan_list = _normalize_list(
        plan
    )

    investigations_list = _normalize_list(
        investigations
    )

    # ========================================================
    # LOCALIZED STRUCTURED NOTE
    # ========================================================

    localized = _localized_structured_note(
        medical_information,
        report_language,
    )

    # ========================================================
    # CREATE DATABASE CLINICAL NOTE
    # ========================================================

    db_note = ClinicalNote(

        patient_id=patient_id,

        chief_complaint=chief_complaint,

        history_of_present_illness=(
            history_of_present_illness
        ),

        assessment=assessment,

        status="draft",

        # IMPORTANT:
        # Store the REPORT language,
        # not the recording language.
        language=report_language,
    )

    db_note.plan = plan_list

    db_note.allergies = allergies_list

    db_note.medications = medications_list

    db_note.negated_findings = []

    # ========================================================
    # SAVE NOTE
    # ========================================================

    db.add(
        db_note
    )

    db.commit()

    db.refresh(
        db_note
    )

    # ========================================================
    # RETURN COMPLETE AI RESULT
    # ========================================================

    return {

        "success": True,

        "message": (
            "Audio processed successfully "
            "using the AI Clinical Scribe pipeline."
        ),

        "file_id": str(
            file_id
        ),

        "filename": file.filename,

        "transcription_mode": "whisper",

        "is_real_transcription": True,

        # ----------------------------------------------------
        # LANGUAGE INFORMATION
        # ----------------------------------------------------

        "recording_language": recording_language,

        "report_language": report_language,

        # Backward compatibility
        "language": report_language,

        # ----------------------------------------------------
        # TRANSCRIPT
        # ----------------------------------------------------

        "transcript": transcript,

        "cleaned_transcript": cleaned_transcript,

        # ----------------------------------------------------
        # MEDICAL INFORMATION
        # ----------------------------------------------------

        "medical_information": medical_information,

        # ----------------------------------------------------
        # GENERATED CLINICAL NOTE
        # ----------------------------------------------------

        "clinical_note": clinical_note_text,

        # ----------------------------------------------------
        # STRUCTURED NOTE
        # ----------------------------------------------------

        "structured_note": {

            "id": db_note.id,

            "patient_id": db_note.patient_id,

            # Localized doctor-facing fields
            "chief_complaint": (
                localized["chief_complaint"]
            ),

            "history_of_present_illness": (
                localized[
                    "history_of_present_illness"
                ]
            ),

            "assessment": (
                localized["assessment"]
            ),

            "plan": localized["plan"],

            "allergies": localized["allergies"],

            "medications": localized["medications"],

            "investigations": (
                localized["investigations"]
            ),

            "status": db_note.status,

            "language": db_note.language,

            "recording_language": recording_language,

            "report_language": report_language,
        },

        # ----------------------------------------------------
        # CONVERSATION
        # ----------------------------------------------------

        "conversation": result.get(
            "conversation",
            [],
        ),

        "sentences": result.get(
            "sentences",
            [],
        ),
    }


# ============================================================
# LIST ALL NOTES
# ============================================================

@router.get(
    "",
    response_model=List[NoteResponse],
)
def list_notes(
    patient_id: Optional[int] = Query(
        None,
        description=(
            "Optional patient filter"
        ),
    ),

    db: Session = Depends(
        get_db
    ),
):
    """
    Lists clinical notes ordered
    by recent creation.
    """

    query = db.query(
        ClinicalNote
    )

    if patient_id is not None:

        query = query.filter(
            ClinicalNote.patient_id
            == patient_id
        )

    notes = (
        query
        .order_by(
            ClinicalNote.created_at.desc()
        )
        .all()
    )

    return [
        _to_note_response(note)
        for note in notes
    ]


# ============================================================
# GET SINGLE NOTE
# ============================================================

@router.get(
    "/{note_id}",
    response_model=NoteResponse,
)
def get_note(
    note_id: int,

    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieves a single clinical note.
    """

    note = (
        db.query(ClinicalNote)
        .filter(
            ClinicalNote.id == note_id
        )
        .first()
    )

    if not note:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Clinical note "
                f"#{note_id} not found."
            ),
        )

    return _to_note_response(
        note
    )


# ============================================================
# UPDATE NOTE
# ============================================================

@router.put(
    "/{note_id}",
    response_model=NoteResponse,
)
def update_note(
    note_id: int,

    req: NoteUpdateRequest,

    db: Session = Depends(
        get_db
    ),
):
    """
    Updates editable clinical note fields.

    Supports:
    - inline editing
    - draft → reviewed
    - allergies
    - medications
    - assessment
    - plan
    """

    note = (
        db.query(ClinicalNote)
        .filter(
            ClinicalNote.id == note_id
        )
        .first()
    )

    if not note:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Clinical note "
                f"#{note_id} not found."
            ),
        )

    if req.chief_complaint is not None:

        note.chief_complaint = (
            req.chief_complaint
        )

    if (
        req.history_of_present_illness
        is not None
    ):

        note.history_of_present_illness = (
            req.history_of_present_illness
        )

    if req.assessment is not None:

        note.assessment = (
            req.assessment
        )

    if req.plan is not None:

        note.plan = req.plan

    if req.allergies is not None:

        note.allergies = (
            req.allergies
        )

    if req.medications is not None:

        note.medications = (
            req.medications
        )

    if req.negated_findings is not None:

        note.negated_findings = (
            req.negated_findings
        )

    if req.status is not None:

        note.status = req.status

    db.commit()

    db.refresh(
        note
    )

    return _to_note_response(
        note
    )


# ============================================================
# EXPORT NOTE
# ============================================================

@router.post(
    "/{note_id}/export"
)
def export_note_endpoint(
    note_id: int,

    format: str = Query(
        "soap",
        description=(
            "Export format: "
            "txt | json | soap | fhir"
        ),
    ),

    db: Session = Depends(
        get_db
    ),
):
    """
    Export a clinical note.

    Supported:
        TXT
        JSON
        SOAP

    FHIR is currently a stub.
    """

    note = (
        db.query(ClinicalNote)
        .filter(
            ClinicalNote.id == note_id
        )
        .first()
    )

    if not note:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Clinical note "
                f"#{note_id} not found."
            ),
        )

    try:

        exported = export_note(
            note,
            format_type=format,
        )

        return Response(

            content=exported[
                "content"
            ],

            media_type=exported[
                "media_type"
            ],

            headers={
                "Content-Disposition":
                    (
                        "attachment; "
                        f"filename="
                        f"{exported['filename']}"
                    )
            },
        )

    except FHIRNotImplementedError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_501_NOT_IMPLEMENTED
            ),
            detail=str(exc),
        )

    except ExportFormatError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        )
