from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
import re


class HealthResponse(BaseModel):
    status: str = "ok"
    whisper_loaded: bool
    ffmpeg_available: bool
    version: str = "1.0.0"


class TranscriptSegment(BaseModel):
    speaker: Literal["Doctor", "Patient", "Unknown"] = "Unknown"
    start: float = 0.0
    end: float = 0.0
    text: str


class TranscribeResponse(BaseModel):
    segments: List[TranscriptSegment]
    language: str = "en"
    duration: Optional[float] = None


class NoteCapabilities(BaseModel):
    allergies: bool = False
    medications: bool = False
    negation: bool = True
    diarization: bool = False


class NoteGenerateRequest(BaseModel):
    transcript: List[TranscriptSegment]
    language: Optional[str] = "en"
    patient_id: Optional[int] = None


class NoteResponse(BaseModel):
    id: Optional[int] = None
    patient_id: Optional[int] = None
    chief_complaint: str
    history_of_present_illness: str
    assessment: str
    plan: List[str]
    allergies: List[str] = []
    medications: List[str] = []
    negated_findings: List[str] = []
    status: Literal["draft", "reviewed"] = "draft"
    language: str = "en"
    capabilities: NoteCapabilities = Field(default_factory=NoteCapabilities)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NoteUpdateRequest(BaseModel):
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    negated_findings: Optional[List[str]] = None
    status: Optional[Literal["draft", "reviewed"]] = None


class DemoRequestCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=120)
    organization: str = Field(..., min_length=2, max_length=150)
    role: str = Field(..., min_length=2, max_length=80)
    message: Optional[str] = Field(default="", max_length=1000)

    @field_validator("email")
    def validate_email_format(cls, v: str) -> str:
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email address format.")
        return v.strip().lower()


class DemoRequestResponse(BaseModel):
    id: int
    status: str = "received"
    message: str = "Demo request submitted successfully. A care specialist will follow up shortly."


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    medical_record_number: str
