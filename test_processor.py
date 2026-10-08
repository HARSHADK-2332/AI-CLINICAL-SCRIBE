from ai.transcript_processor import (
    clean_transcript,
    detect_language,
    split_into_sentences,
    organize_conversation
)


transcript = """
Good morning doctor. Umm, I have fever and cough.
The fever is more at night. Do you know actually
if I have any allergies?
"""


print("\n--- ORIGINAL TRANSCRIPT ---")
print(transcript)


cleaned = clean_transcript(transcript)

print("\n--- CLEANED TRANSCRIPT ---")
print(cleaned)


language = detect_language(cleaned)

print("\n--- LANGUAGE ---")
print(language)


sentences = split_into_sentences(cleaned)

print("\n--- ORGANIZED SENTENCES ---")

for i, sentence in enumerate(sentences, 1):
    print(f"{i}. {sentence}")


organized = organize_conversation(cleaned)

print("\n--- CONVERSATION DATA ---")

for item in organized:
    print(item)