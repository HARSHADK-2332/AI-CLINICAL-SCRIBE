def generate_clinical_note(info):
    age = info["age"]
    symptoms = info["symptoms"]
    duration = info["duration"]
    allergies = info["allergies"]

    if symptoms:
        symptom_text = "\n".join(f"- {symptom.title()}" for symptom in symptoms)
    else:
        symptom_text = "Not mentioned"

    note = f"""
CLINICAL NOTE
=============

Patient Age:
{age if age else "Not mentioned"}

Chief Complaints:
{symptom_text}

Duration:
{duration if duration else "Not mentioned"}

Allergies:
{allergies}

Medical History:
Not mentioned

Medications:
Not mentioned

Assessment:
Requires doctor review.

Plan:
To be decided by the doctor.
"""

    return note.strip()