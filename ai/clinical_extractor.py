
import re


# =========================================================
# TEXT UTILITIES
# =========================================================

def _clean_text(text):
    """Normalize whitespace without changing the original script."""
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _contains_phrase(text, phrase):
    """Match whole words for English and literal phrases for other scripts."""
    phrase = phrase.strip()
    if not phrase:
        return False

    if re.fullmatch(r"[a-zA-Z0-9 -]+", phrase):
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        return re.search(pattern, text, re.IGNORECASE) is not None

    return phrase.casefold() in text.casefold()


def _find_keyword_occurrence(text, keyword):
    """Return the first occurrence of a keyword, or -1."""
    if re.fullmatch(r"[a-zA-Z0-9 -]+", keyword):
        match = re.search(
            r"(?<!\w)" + re.escape(keyword) + r"(?!\w)",
            text,
            re.IGNORECASE,
        )
        return match.start() if match else -1

    return text.casefold().find(keyword.casefold())


def _is_negated(text, keyword, position):
    """
    Conservative check for common denial phrases immediately
    before a keyword. This is not a full clinical NLP system.
    """
    if position < 0:
        return False

    preceding = text[max(0, position - 75):position].casefold()

    denial_patterns = [
        r"\bno\s+(?:fever|cough|cold|headache|vomiting|nausea|pain|"
        r"fatigue|dizziness|allerg(?:y|ies)|breathing difficulty)\s*$",
        r"\b(?:denies|denied|without|negative for|not experiencing)\s*$",
        r"\b(?:does not have|do not have|did not have|has no|have no)\s*$",
        r"\b(?:no history of)\s*$",
        r"(?:नहीं है|नहीं|नकारते हैं|नकारती हैं)\s*$",
        r"(?:లేవు|లేదు|కాదు)\s*$",
    ]

    for pattern in denial_patterns:
        if re.search(pattern, preceding, re.IGNORECASE):
            return True

    return False


def _unique(values):
    """Return unique, non-empty values while preserving order."""
    result = []
    seen = set()

    for value in values:
        value = str(value).strip()
        key = value.casefold()

        if value and key not in seen:
            result.append(value)
            seen.add(key)

    return result


def _extract_first(patterns, text, flags=re.IGNORECASE):
    """Return the first successful regular-expression match."""
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match

    return None


# =========================================================
# AGE EXTRACTION
# =========================================================

def extract_age(text):
    """
    Extract an explicitly stated age in English, Hindi or Telugu.
    Returns an integer or None.
    """
    text = _clean_text(text)

    patterns = [
        # English
        r"\b(?:i am|i'm|my age is|patient is|age is|aged)"
        r"\s*[:,-]?\s*(\d{1,3})"
        r"(?:\s*(?:years?\s*old|years?|yrs?|y/o))?\b",

        r"\b(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|years?\s*of age)\b",

        # Hindi
        r"(?:मेरी उम्र|मेरी आयु|उम्र|आयु)"
        r"\s*(?:है|हैं|लगभग)?\s*(\d{1,3})\s*(?:साल|वर्ष)?",

        r"(\d{1,3})\s*(?:साल|वर्ष)\s*(?:की|का|के)?\s*(?:उम्र|आयु)",

        # Telugu
        r"(?:నా వయస్సు|నా వయసు|వయస్సు|వయసు)"
        r"\s*(?:సుమారు)?\s*(\d{1,3})",

        r"(\d{1,3})\s*(?:సంవత్సరాలు|సంవత్సరం|ఏళ్లు|ఏళ్ళు)"
        r"(?:\s*(?:వయస్సు|వయసు))?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            age = int(match.group(1))

            if 0 <= age <= 120:
                return age

    return None


# =========================================================
# SYMPTOM EXTRACTION
# =========================================================

SYMPTOM_KEYWORDS = {
    "fever": ["fever", "బుఖార్", "बुखार", "జ్వరం"],
    "cough": ["cough", "खांसी", "खाँसी", "దగ్గు"],
    "cold": ["cold", "जुकाम", "सर्दी", "జలుబు"],
    "headache": ["headache", "सिरदर्द", "सिर दर्द", "తలనొప్పి"],
    "vomiting": ["vomiting", "vomit", "उल्टी", "వాంతులు"],
    "nausea": ["nausea", "मतली", "వికారం"],
    "pain": ["pain", "दर्द", "నొప్పి"],
    "fatigue": ["fatigue", "tiredness", "थकान", "అలసట"],
    "dizziness": ["dizziness", "చक्कर", "चक्कर", "తల తిరగడం"],
    "breathing difficulty": [
        "breathing difficulty",
        "difficulty breathing",
        "shortness of breath",
        "breathlessness",
        "सांस लेने में कठिनाई",
        "सांस लेने में दिक्कत",
        "శ్వాస తీసుకోవడంలో ఇబ్బంది",
        "శ్వాస తీసుకోవడం కష్టం",
    ],
}


def extract_symptoms(text):
    """
    Return recognized symptoms in normalized English labels.
    Common explicit denials are excluded conservatively.
    """
    text = _clean_text(text)
    found = []

    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        for keyword in keywords:
            position = _find_keyword_occurrence(text, keyword)

            if position >= 0 and not _is_negated(text, keyword, position):
                found.append(symptom)
                break

    return _unique(found)


# =========================================================
# DURATION EXTRACTION
# =========================================================

def extract_duration(text):
    """
    Extract a stated duration. Returns the matched number and unit.
    """
    text = _clean_text(text)

    patterns = [
        # English: for three days, for 3 days, since 2 weeks
        r"\b(?:for|past|last|since|about|around|approximately)"
        r"\s+(\d+)\s*(days?|weeks?|months?|years?|hours?)\b",

        r"\b(\d+)\s*(days?|weeks?|months?|years?|hours?)"
        r"\s*(?:now|ago)?\b",

        # Hindi
        r"(?:पिछले|पिछली|लगभग|करीब|से)"
        r"\s*(\d+)\s*(दिन|हफ्ते|हफ्तों|सप्ताह|महीने|महीनों|साल|वर्ष)",

        r"(\d+)\s*(दिन|हफ्ते|हफ्तों|सप्ताह|महीने|महीनों|साल|वर्ष)",

        # Telugu
        r"(?:గత|సుమారు|దాదాపు|నుండి|గా)"
        r"\s*(\d+)\s*(రోజులు|రోజుల|రోజు|వారాలు|వారాల|నెలలు|నెలల|"
        r"సంవత్సరాలు|సంవత్సరాల|గంటలు)",

        r"(\d+)\s*(రోజులు|రోజుల|రోజు|వారాలు|వారాల|నెలలు|నెలల|"
        r"సంవత్సరాలు|సంవత్సరాల|గంటలు)",
    ]

    match = _extract_first(patterns, text)

    if match:
        return f"{match.group(1)} {match.group(2)}"

    return None


# =========================================================
# ALLERGY EXTRACTION
# =========================================================

def extract_allergies(text):
    """
    Extract explicit allergy information.

    'None reported' means the transcript explicitly reports
    no allergies. 'Not mentioned' means no clear information
    was identified.
    """
    text = _clean_text(text)
    lower = text.casefold()

    no_allergy_phrases = [
        "no allergies",
        "no allergy",
        "no known allergies",
        "not allergic",
        "does not have any allergies",
        "do not have any allergies",
        "doesn't have any allergies",
        "कोई एलर्जी नहीं",
        "एलर्जी नहीं है",
        "एलर्जी नहीं",
        "எந்த ஒவ்வாமையும் இல்லை",
        "ఎలాంటి అలర్జీలు లేవు",
        "అలర్జీ లేదు",
        "అలర్జీలు లేవు",
        "ఎలాంటి అలర్జీ లేదు",
    ]

    for phrase in no_allergy_phrases:
        if phrase.casefold() in lower:
            return "None reported"

    patterns = [
        r"\b(?:allergic to|allergy to|allergies to)\s+"
        r"([^,.;\n!?]+)",

        r"(?:एलर्जी|एलर्जिक)\s*(?:है|हैं|से)?\s*"
        r"([^,.;\n!?।]+)",

        r"(?:అలర్జీ|అలర్జీలు)\s*(?:ఉంది|ఉన్నాయి|వల్ల)?\s*"
        r"([^,.;\n!?।]+)",
    ]

    match = _extract_first(patterns, text)

    if match:
        value = match.group(1).strip(" :-,")
        if value:
            return value

    return "Not mentioned"


# =========================================================
# MEDICATION EXTRACTION
# =========================================================

def extract_medications(text):
    """
    Extract medication phrases explicitly mentioned in the transcript.

    These are text matches, not validated drug names or dosage advice.
    """
    text = _clean_text(text)
    medications = []

    patterns = [
        # English: taking paracetamol; takes metformin
        r"\b(?:taking|takes|currently on|prescribed)\s+"
        r"([A-Za-z][A-Za-z0-9-]*(?:\s+[A-Za-z][A-Za-z0-9-]*){0,3})",

        # Hindi
        r"(?:दवा का नाम|दवाई का नाम|दवा ले रहे हैं|दवा ले रही हैं|"
        r"दवा लेते हैं|दवा लेती हैं)\s*[:,-]?\s*([^,.;\n!?।]+)",

        # Telugu
        r"(?:మందు పేరు|మందులు వాడుతున్నారు|మందు తీసుకుంటున్నారు|"
        r"మందులు తీసుకుంటున్నారు)\s*[:,-]?\s*([^,.;\n!?।]+)",
    ]

    stop_words = {
        "for", "because", "since", "and", "but", "with",
        "today", "yesterday", "daily", "regularly",
        "fever", "cough", "pain", "headache",
    }

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(1).strip(" :-,")
            words = value.split()

            # Trim at common sentence connectors to reduce over-capture.
            trimmed = []

            for word in words:
                if word.casefold() in stop_words:
                    break
                trimmed.append(word)

            value = " ".join(trimmed).strip()

            if value:
                medications.append(value)

    return _unique(medications)


# =========================================================
# MEDICAL HISTORY
# =========================================================

MEDICAL_HISTORY_KEYWORDS = {
    "diabetes": [
        "diabetes",
        "मधुमेह",
        "डायबिटीज",
        "డయాబెటిస్",
        "చక్కెర వ్యాధి",
    ],
    "hypertension": [
        "hypertension",
        "high blood pressure",
        "उच्च रक्तचाप",
        "బీపీ",
        "బి.పి.",
        "అధిక రక్తపోటు",
    ],
    "asthma": [
        "asthma",
        "अस्थमा",
        "दमा",
        "ఆస్తమా",
    ],
    "heart disease": [
        "heart disease",
        "हृदय रोग",
        "दिल की बीमारी",
        "గుండె జబ్బు",
    ],
}


def extract_medical_history(text):
    """Extract recognized medical history terms."""
    text = _clean_text(text)
    history = []

    for condition, keywords in MEDICAL_HISTORY_KEYWORDS.items():
        for keyword in keywords:
            position = _find_keyword_occurrence(text, keyword)

            if position >= 0 and not _is_negated(text, keyword, position):
                history.append(condition)
                break

    return _unique(history)


# =========================================================
# SEVERITY
# =========================================================

def extract_severity(text):
    """Extract explicitly stated severity."""
    text = _clean_text(text)

    severity_keywords = {
        "Mild": [
            "mild",
            "हल्का",
            "हल्की",
            "हल्के",
            "తేలికపాటి",
        ],
        "Moderate": [
            "moderate",
            "मध्यम",
            "మధ్యస్థ",
        ],
        "Severe": [
            "severe",
            "serious",
            "गंभीर",
            "बहुत ज्यादा",
            "తీవ్ర",
            "తీవ్రమైన",
        ],
    }

    for severity, keywords in severity_keywords.items():
        for keyword in keywords:
            if _contains_phrase(text, keyword):
                return severity

    return "Not mentioned"


# =========================================================
# INVESTIGATIONS
# =========================================================

INVESTIGATION_KEYWORDS = {
    "blood test": [
        "blood test",
        "blood tests",
        "ब्लड टेस्ट",
        "रक्त जांच",
        "रक्त जाँच",
        "రక్త పరీక్ష",
    ],
    "x-ray": [
        "x-ray",
        "xray",
        "एक्स रे",
        "एक्स-रे",
        "ఎక్స్ రే",
    ],
    "ct scan": [
        "ct scan",
        "सीटी स्कैन",
        "సిటి స్కాన్",
    ],
    "mri": [
        "mri",
        "एमआरआई",
        "ఎంఆర్ఐ",
    ],
}


def extract_investigations(text):
    """Extract investigation names mentioned in the transcript."""
    text = _clean_text(text)
    investigations = []

    for investigation, keywords in INVESTIGATION_KEYWORDS.items():
        for keyword in keywords:
            if _contains_phrase(text, keyword):
                investigations.append(investigation)
                break

    return _unique(investigations)


# =========================================================
# DIAGNOSIS
# =========================================================

def extract_diagnosis(text):
    """
    Extract diagnosis phrases when introduced explicitly.
    This does not infer a diagnosis from symptoms.
    """
    text = _clean_text(text)
    diagnosis = []

    patterns = [
        r"\b(?:diagnosed with|diagnosis is|assessment is)"
        r"\s+([^,.;\n!?]+)",

        r"(?:निदान|डायग्नोसिस)\s*(?:है|हैं|:)?\s*"
        r"([^,.;\n!?।]+)",

        r"(?:నిర్ధారణ|డయాగ్నోసిస్)\s*(?:అని|ఉంది|:)?\s*"
        r"([^,.;\n!?।]+)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = match.group(1).strip(" :-,")

            if value:
                diagnosis.append(value)

    return _unique(diagnosis)


# =========================================================
# PLAN
# =========================================================

PLAN_KEYWORDS = [
    # English
    "take rest",
    "drink plenty of water",
    "follow up",
    "follow-up",
    "take medication",
    "blood test",
    "x-ray",
    "ct scan",
    "mri",

    # Hindi
    "दवा लें",
    "आराम करें",
    "पानी पिएं",
    "पानी पिएँ",
    "फॉलो अप",

    # Telugu
    "విశ్రాంతి తీసుకోండి",
    "నీరు ఎక్కువగా తాగండి",
    "మందులు తీసుకోండి",
    "ఫాలో అప్",
]


def extract_plan(text):
    """
    Extract recognized plan phrases that were actually mentioned.
    The function does not generate treatment recommendations.
    """
    text = _clean_text(text)
    found = []

    for keyword in PLAN_KEYWORDS:
        if _contains_phrase(text, keyword):
            found.append(keyword)

    return _unique(found)


# =========================================================
# MAIN MEDICAL INFORMATION EXTRACTION
# =========================================================

def extract_medical_information(text):
    """
    Return the structured information expected by the
    existing AI Clinical Scribe pipeline and frontend.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Transcript cannot be empty.")

    text = _clean_text(text)

    return {
        "age": extract_age(text),
        "symptoms": extract_symptoms(text),
        "duration": extract_duration(text),
        "severity": extract_severity(text),
        "allergies": extract_allergies(text),
        "medications": extract_medications(text),
        "medical_history": extract_medical_history(text),
        "investigations": extract_investigations(text),
        "diagnosis": extract_diagnosis(text),
        "plan": extract_plan(text),
    }