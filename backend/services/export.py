import json
from typing import Dict, Any
from backend.models import ClinicalNote


class ExportFormatError(Exception):
    pass


class FHIRNotImplementedError(Exception):
    pass


def export_note(note: ClinicalNote, format_type: str) -> Dict[str, Any]:
    """
    Exports a clinical note into requested format: txt, json, soap, or fhir.
    """
    fmt = format_type.lower().strip()

    patient_name = note.patient.name if note.patient else "Unassigned Patient"
    patient_mrn = note.patient.medical_record_number if note.patient else "N/A"
    patient_age = f"{note.patient.age}y" if note.patient else "Unknown age"
    patient_gender = note.patient.gender if note.patient else "Unknown"

    if fmt == "json":
        data = {
            "id": note.id,
            "patient": {
                "name": patient_name,
                "mrn": patient_mrn,
                "age": patient_age,
                "gender": patient_gender
            },
            "chief_complaint": note.chief_complaint,
            "history_of_present_illness": note.history_of_present_illness,
            "assessment": note.assessment,
            "plan": note.plan,
            "allergies": note.allergies,
            "medications": note.medications,
            "negated_findings": note.negated_findings,
            "status": note.status,
            "language": note.language,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "disclaimer": "ScribeCare generated draft documentation. Must be reviewed by a licensed clinician."
        }
        return {
            "content": json.dumps(data, indent=2),
            "media_type": "application/json",
            "filename": f"clinical_note_{note.id}.json"
        }

    elif fmt == "txt":
        plan_bullets = "\n".join(f"  - {p}" for p in note.plan) or "  - None specified"
        neg_line = f"Pertinent Negatives: {', '.join(note.negated_findings)}\n" if note.negated_findings else ""
        content = f"""SCRIBECARE CLINICAL NOTE
========================
Note ID: {note.id}
Status: {note.status.upper()}
Patient: {patient_name} ({patient_age}, {patient_gender}) | MRN: {patient_mrn}
Generated: {note.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if note.created_at else 'N/A'}

CHIEF COMPLAINT:
{note.chief_complaint}

HISTORY OF PRESENT ILLNESS:
{note.history_of_present_illness}
{neg_line}
ASSESSMENT:
{note.assessment}

PLAN:
{plan_bullets}

DISCLAIMER:
ScribeCare generates draft documentation that must be reviewed and signed by a licensed clinician.
"""
        return {
            "content": content.strip(),
            "media_type": "text/plain",
            "filename": f"clinical_note_{note.id}.txt"
        }

    elif fmt == "soap":
        plan_bullets = "\n".join(f"- {p}" for p in note.plan) or "- None specified"
        neg_section = f"Pertinent Negatives: {', '.join(note.negated_findings)}\n" if note.negated_findings else ""
        content = f"""# SOAP CLINICAL NOTE
**Patient:** {patient_name} | **MRN:** {patient_mrn} | **Demographics:** {patient_age}, {patient_gender}  
**Status:** {note.status.upper()} | **Date:** {note.created_at.strftime('%Y-%m-%d %H:%M') if note.created_at else 'N/A'}

---

### S — Subjective
- **Chief Complaint:** {note.chief_complaint}
- **History of Present Illness (HPI):** {note.history_of_present_illness}
{neg_section}

### O — Objective
- *Vital signs and physical examination to be documented by attending clinician.*

### A — Assessment
{note.assessment}

### P — Plan
{plan_bullets}

---
*Notice: ScribeCare generates draft clinical documentation that must be reviewed and authenticated by a licensed physician before entry into the official Medical Record.*
"""
        return {
            "content": content.strip(),
            "media_type": "text/markdown",
            "filename": f"clinical_note_{note.id}_soap.md"
        }

    elif fmt == "fhir":
        raise FHIRNotImplementedError(
            "FHIR R4 export is scheduled for Phase 4 roadmap and not yet implemented. "
            "Please use format=json, format=txt, or format=soap in the interim."
        )

    else:
        raise ExportFormatError(f"Unsupported export format '{format_type}'. Supported formats: txt, json, soap, fhir.")
