from ai.clinical_extractor import extract_medical_information
from ai.note_generator import generate_clinical_note


transcript = """
Hi Doctor, I am 35 years old,
I am suffering from fever and cough
from past 3 days.
I don't have any allergies.
"""

info = extract_medical_information(transcript)

note = generate_clinical_note(info)

print("\n--- GENERATED CLINICAL NOTE ---")
print(note)