
import re


# =========================================================
# CLEAN TRANSCRIPT
# =========================================================

def clean_transcript(text):
    """
    Clean speech-to-text output while preserving
    English, Hindi, and Telugu content.
    """

    if not text:
        return ""

    cleaned = text.strip()

    # Common English speech fillers
    english_fillers = [
        r"\bumm+\b",
        r"\buh+\b",
        r"\bah+\b",
        r"\byou know\b",
        r"\bactually\b",
    ]

    for pattern in english_fillers:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE
        )

    # Remove spaces before punctuation
    cleaned = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        cleaned
    )

    # Remove punctuation left at the beginning of a sentence
    cleaned = re.sub(
        r"([.!?])\s*[,;:]+\s*",
        r"\1 ",
        cleaned
    )

    # Remove repeated punctuation
    cleaned = re.sub(
        r"([,.!?])\1+",
        r"\1",
        cleaned
    )

    # Remove unnecessary spaces
    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    )

    return cleaned.strip()


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text):
    """
    Detect English, Hindi, or Telugu.
    """

    if not text:
        return "English"

    telugu_chars = re.findall(
        r"[\u0C00-\u0C7F]",
        text
    )

    hindi_chars = re.findall(
        r"[\u0900-\u097F]",
        text
    )

    english_chars = re.findall(
        r"[A-Za-z]",
        text
    )

    if (
        len(telugu_chars) > len(hindi_chars)
        and len(telugu_chars) > 0
    ):
        return "Telugu"

    if len(hindi_chars) > 0:
        return "Hindi"

    if len(english_chars) > 0:
        return "English"

    return "English"


# =========================================================
# SENTENCE SPLITTING
# =========================================================

def split_into_sentences(text):
    """
    Split transcript into individual sentences.
    Supports English, Hindi, and Telugu punctuation.
    """

    if not text or not text.strip():
        return []

    sentences = re.split(
        r"(?<=[.!?।])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# =========================================================
# ORGANIZE CONVERSATION
# =========================================================

def organize_conversation(text):
    """
    Organize transcript into conversation entries.
    """

    sentences = split_into_sentences(text)

    conversation = []

    for sentence in sentences:

        conversation.append({
            "text": sentence,
            "type": "conversation"
        })

    return conversation
