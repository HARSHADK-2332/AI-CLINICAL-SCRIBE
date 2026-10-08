from ai.clinical_extractor import extract_medical_information


transcript = """
Hi Doctor, I am 35 years old,
I am suffering from fever and cough
from past 3 days.
I don't have any allergies.
"""

result = extract_medical_information(transcript)

print("\n--- CLINICAL INFORMATION ---")
print("Age:", result["age"])
print("Symptoms:", result["symptoms"])
print("Duration:", result["duration"])
print("Allergies:", result["allergies"])