import re


def extract_age(transcript):
    match = re.search(
        r"(\d{1,3})\s*(?:years old|year old|yrs old|years)",
        transcript.lower()
    )

    if match:
        return int(match.group(1))

    return None


def extract_symptoms(transcript):
    symptoms = []

    common_symptoms = [
        "fever",
        "cough",
        "cold",
        "headache",
        "vomiting",
        "nausea",
        "pain",
        "fatigue",
        "dizziness",
        "shortness of breath"
    ]

    text = transcript.lower()

    for symptom in common_symptoms:
        if symptom in text:
            symptoms.append(symptom)

    return symptoms


def extract_duration(transcript):
    match = re.search(
        r"(?:past|for|from)\s+(\d+)\s+(day|days|week|weeks|month|months)",
        transcript.lower()
    )

    if match:
        return match.group(1) + " " + match.group(2)

    return None


def extract_allergies(transcript):
    text = transcript.lower()

    if "no allergies" in text or "don't have any allergies" in text:
        return "None reported"

    return "Not mentioned"


def extract_medical_information(transcript):
    return {
        "age": extract_age(transcript),
        "symptoms": extract_symptoms(transcript),
        "duration": extract_duration(transcript),
        "allergies": extract_allergies(transcript)
    }