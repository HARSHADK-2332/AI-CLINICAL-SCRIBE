import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(30), nullable=False)
    medical_record_number = Column(String(50), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    notes = relationship("ClinicalNote", back_populates="patient", cascade="all, delete-orphan")


class ClinicalNote(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    chief_complaint = Column(Text, nullable=False, default="")
    history_of_present_illness = Column(Text, nullable=False, default="")
    assessment = Column(Text, nullable=False, default="")
    plan_json = Column(Text, nullable=False, default="[]")
    allergies_json = Column(Text, nullable=False, default="[]")
    medications_json = Column(Text, nullable=False, default="[]")
    negated_findings_json = Column(Text, nullable=False, default="[]")
    status = Column(String(30), nullable=False, default="draft")  # draft | reviewed
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="notes")

    @property
    def plan(self):
        try:
            return json.loads(self.plan_json or "[]")
        except Exception:
            return []

    @plan.setter
    def plan(self, value):
        self.plan_json = json.dumps(value or [])

    @property
    def allergies(self):
        try:
            return json.loads(self.allergies_json or "[]")
        except Exception:
            return []

    @allergies.setter
    def allergies(self, value):
        self.allergies_json = json.dumps(value or [])

    @property
    def medications(self):
        try:
            return json.loads(self.medications_json or "[]")
        except Exception:
            return []

    @medications.setter
    def medications(self, value):
        self.medications_json = json.dumps(value or [])

    @property
    def negated_findings(self):
        try:
            return json.loads(self.negated_findings_json or "[]")
        except Exception:
            return []

    @negated_findings.setter
    def negated_findings(self, value):
        self.negated_findings_json = json.dumps(value or [])


class DemoRequest(Base):
    __tablename__ = "demo_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    organization = Column(String(150), nullable=False)
    role = Column(String(80), nullable=False)
    message = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
