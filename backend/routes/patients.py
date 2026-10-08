from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Patient
from backend.schemas import PatientResponse

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.get("", response_model=List[PatientResponse])
def list_patients(db: Session = Depends(get_db)):
    """
    Returns list of registered patients.
    """
    patients = db.query(Patient).order_by(Patient.name.asc()).all()
    return [
        PatientResponse(
            id=p.id,
            name=p.name,
            age=p.age,
            gender=p.gender,
            medical_record_number=p.medical_record_number
        )
        for p in patients
    ]
