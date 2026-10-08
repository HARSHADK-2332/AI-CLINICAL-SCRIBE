
from datetime import date

from pydantic import BaseModel, Field


class TranscriptRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=50000)


class PatientRequest(BaseModel):
    patient_name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=120)
    gender: str = Field(min_length=1, max_length=30)
    patient_id: str = Field(min_length=1, max_length=100)
    consultation_date: date


class ClinicalNoteRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=50000)
    patient_id: str | None = None


class ScribeProcessRequest(BaseModel):
    transcript: str | None = Field(default=None, max_length=50000)
    file_id: str | None = None