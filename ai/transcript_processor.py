import re


def clean_transcript(transcript):
    if not transcript:
        return ""

    transcript = transcript.strip()

    # Remove filler words
    filler_words = [
        r"\bumm+\b",
        r"\buh+\b",
        r"\bah+\b",
        r"\byou know\b",
        r"\bactually\b"
    ]

    for word in filler_words:
        transcript = re.sub(
            word,
            "",
            transcript,
            flags=re.IGNORECASE
        )

    # Remove extra spaces
    transcript = re.sub(r"\s+", " ", transcript)

    # Remove spaces before punctuation
    transcript = re.sub(r"\s+([,.!?])", r"\1", transcript)

    # Remove punctuation left alone after filler-word removal
    transcript = re.sub(r"([.!?])\s*,", r"\1", transcript)
    transcript = re.sub(r",\s*([.!?])", r"\1", transcript)

    # Remove unnecessary commas after sentence starts
    transcript = re.sub(
        r"(^|[.!?])\s*,\s*",
        r"\1 ",
        transcript
    )

    # Clean spaces again
    transcript = re.sub(r"\s+", " ", transcript)

    return transcript.strip()


def detect_language(transcript):
    telugu_count = len(
        re.findall(r"[\u0C00-\u0C7F]", transcript)
    )

    hindi_count = len(
        re.findall(r"[\u0900-\u097F]", transcript)
    )

    if telugu_count > 0:
        return "Telugu"

    if hindi_count > 0:
        return "Hindi"

    return "English"


def split_into_sentences(transcript):
    if not transcript:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        transcript
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def organize_conversation(transcript):
    if not transcript:
        return []

    sentences = split_into_sentences(transcript)

    organized = []

    for sentence in sentences:
        organized.append({
            "text": sentence,
            "type": "conversation"
        })

    return organized