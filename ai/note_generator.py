# =========================================================
# AI CLINICAL SCRIBE
# Multilingual Clinical Note Generator
# Supports: English, Hindi, Telugu
# =========================================================

import re


# ---------------------------------------------------------
# COMMON TEXT
# ---------------------------------------------------------

NOT_MENTIONED = {
    "English": "Not mentioned",
    "Hindi": "उल्लेख नहीं किया गया",
    "Telugu": "పేర్కొనలేదు",
}


DISCLAIMER = {
    "English": (
        "This note is AI-generated and must be reviewed and "
        "verified by a qualified healthcare professional before "
        "clinical use."
    ),
    "Hindi": (
        "यह नोट AI द्वारा तैयार किया गया है। क्लिनिकल उपयोग से "
        "पहले योग्य स्वास्थ्य विशेषज्ञ द्वारा इसकी समीक्षा और "
        "पुष्टि आवश्यक है।"
    ),
    "Telugu": (
        "ఈ నోట్ AI ద్వారా రూపొందించబడింది. వైద్యపరంగా ఉపయోగించే "
        "ముందు అర్హత కలిగిన ఆరోగ్య నిపుణుడు దీనిని సమీక్షించి "
        "ధృవీకరించాలి."
    ),
}


# ---------------------------------------------------------
# SECTION LABELS
# ---------------------------------------------------------

SECTION_LABELS = {
    "English": {
        "duration": "Duration",
        "severity": "Severity",
        "medical_history": "Medical history",
    },
    "Hindi": {
        "duration": "अवधि",
        "severity": "गंभीरता",
        "medical_history": "चिकित्सा इतिहास",
    },
    "Telugu": {
        "duration": "వ్యవధి",
        "severity": "తీవ్రత",
        "medical_history": "వైద్య చరిత్ర",
    },
}


# ---------------------------------------------------------
# CLINICAL TERM TRANSLATIONS
# ---------------------------------------------------------

TERM_TRANSLATIONS = {

    # Symptoms
    "fever": {
        "English": "Fever",
        "Hindi": "बुखार",
        "Telugu": "జ్వరం",
    },

    "cough": {
        "English": "Cough",
        "Hindi": "खांसी",
        "Telugu": "దగ్గు",
    },

    "cold": {
        "English": "Cold",
        "Hindi": "सर्दी",
        "Telugu": "జలుబు",
    },

    "headache": {
        "English": "Headache",
        "Hindi": "सिरदर्द",
        "Telugu": "తలనొప్పి",
    },

    "vomiting": {
        "English": "Vomiting",
        "Hindi": "उल्टी",
        "Telugu": "వాంతులు",
    },

    "nausea": {
        "English": "Nausea",
        "Hindi": "मतली",
        "Telugu": "వికారంగా అనిపించడం",
    },

    "pain": {
        "English": "Pain",
        "Hindi": "दर्द",
        "Telugu": "నొప్పి",
    },

    "fatigue": {
        "English": "Fatigue",
        "Hindi": "थकान",
        "Telugu": "అలసట",
    },

    "dizziness": {
        "English": "Dizziness",
        "Hindi": "चक्कर आना",
        "Telugu": "తల తిరగడం",
    },

    "breathing difficulty": {
        "English": "Breathing difficulty",
        "Hindi": "सांस लेने में कठिनाई",
        "Telugu": "శ్వాస తీసుకోవడంలో ఇబ్బంది",
    },

    # Medical history
    "diabetes": {
        "English": "Diabetes",
        "Hindi": "मधुमेह",
        "Telugu": "మధుమేహం",
    },

    "hypertension": {
        "English": "Hypertension",
        "Hindi": "उच्च रक्तचाप",
        "Telugu": "అధిక రక్తపోటు",
    },

    "asthma": {
        "English": "Asthma",
        "Hindi": "अस्थमा",
        "Telugu": "ఆస్తమా",
    },

    "heart disease": {
        "English": "Heart disease",
        "Hindi": "हृदय रोग",
        "Telugu": "గుండె సంబంధిత వ్యాధి",
    },

    # Severity
    "mild": {
        "English": "Mild",
        "Hindi": "हल्का",
        "Telugu": "తేలికపాటి",
    },

    "moderate": {
        "English": "Moderate",
        "Hindi": "मध्यम",
        "Telugu": "మధ్యస్థ",
    },

    "severe": {
        "English": "Severe",
        "Hindi": "गंभीर",
        "Telugu": "తీవ్రమైన",
    },

    # Common clinical terms
    "normal": {
        "English": "Normal",
        "Hindi": "सामान्य",
        "Telugu": "సాధారణం",
    },

    "abnormal": {
        "English": "Abnormal",
        "Hindi": "असामान्य",
        "Telugu": "అసాధారణం",
    },

    "negative": {
        "English": "Negative",
        "Hindi": "नकारात्मक",
        "Telugu": "ప్రతికూలం",
    },

    "positive": {
        "English": "Positive",
        "Hindi": "सकारात्मक",
        "Telugu": "అనుకూలం",
    },

    "infection": {
        "English": "Infection",
        "Hindi": "संक्रमण",
        "Telugu": "ఇన్ఫెక్షన్",
    },

    "allergy": {
        "English": "Allergy",
        "Hindi": "एलर्जी",
        "Telugu": "అలెర్జీ",
    },
}


# ---------------------------------------------------------
# LANGUAGE HELPERS
# ---------------------------------------------------------

def normalize_language(language="English"):
    language = str(language or "English").strip().lower()

    if language in ["hindi", "hi"]:
        return "Hindi"

    if language in ["telugu", "te"]:
        return "Telugu"

    return "English"


# ---------------------------------------------------------
# TRANSLATION HELPERS
# ---------------------------------------------------------

def translate_term(value, language="English"):
    language = normalize_language(language)

    if value is None:
        return NOT_MENTIONED[language]

    text = str(value).strip()

    if not text:
        return NOT_MENTIONED[language]

    key = text.lower()

    if key in TERM_TRANSLATIONS:
        return TERM_TRANSLATIONS[key].get(
            language,
            text,
        )

    # -----------------------------------------------------
    # Duration translation
    # -----------------------------------------------------

    if language == "Hindi":
        text = re.sub(
            r"\b(\d+)\s*days?\b",
            r"\1 दिन",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*weeks?\b",
            r"\1 सप्ताह",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*months?\b",
            r"\1 महीने",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*hours?\b",
            r"\1 घंटे",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*years?\b",
            r"\1 वर्ष",
            text,
            flags=re.IGNORECASE,
        )

    elif language == "Telugu":
        text = re.sub(
            r"\b(\d+)\s*days?\b",
            r"\1 రోజులు",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*weeks?\b",
            r"\1 వారాలు",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*months?\b",
            r"\1 నెలలు",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*hours?\b",
            r"\1 గంటలు",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\b(\d+)\s*years?\b",
            r"\1 సంవత్సరాలు",
            text,
            flags=re.IGNORECASE,
        )

    return text


def translate_list(items, language="English"):
    language = normalize_language(language)

    if not items:
        return NOT_MENTIONED[language]

    # Accept a single value as well as a list.
    if isinstance(items, (str, int, float)):
        items = [items]

    translated = []

    for item in items:
        if item is None:
            continue

        text = str(item).strip()

        if not text:
            continue

        translated.append(
            translate_term(
                text,
                language,
            )
        )

    if not translated:
        return NOT_MENTIONED[language]

    return "\n".join(
        f"- {item}"
        for item in translated
    )


def format_value(value, language="English"):
    language = normalize_language(language)

    if value is None or value == "" or value == []:
        return NOT_MENTIONED[language]

    if isinstance(value, (list, tuple)):
        return translate_list(
            value,
            language,
        )

    return translate_term(
        value,
        language,
    )


# ---------------------------------------------------------
# PRECAUTIONS / CLINICAL CONSIDERATIONS
# ---------------------------------------------------------

def generate_precautions(info, language="English"):
    language = normalize_language(language)

    precautions = []

    symptoms = info.get("symptoms", [])

    if symptoms:
        if language == "Hindi":
            precautions.append(
                "लक्षणों में बदलाव या बढ़ोतरी होने पर डॉक्टर से संपर्क करें।"
            )

        elif language == "Telugu":
            precautions.append(
                "లక్షణాలు మారినా లేదా తీవ్రమైనా వైద్యుడిని సంప్రదించండి."
            )

        else:
            precautions.append(
                "Contact the doctor if symptoms change or worsen."
            )

    if info.get("medications"):
        if language == "Hindi":
            precautions.append(
                "दवाओं का उपयोग डॉक्टर की सलाह के अनुसार करें।"
            )

        elif language == "Telugu":
            precautions.append(
                "మందులను వైద్యుడి సూచన ప్రకారం మాత్రమే ఉపయోగించండి."
            )

        else:
            precautions.append(
                "Use medications only as advised by the doctor."
            )

    if not precautions:
        return NOT_MENTIONED[language]

    return "\n".join(
        f"- {item}"
        for item in precautions
    )


# ---------------------------------------------------------
# ENGLISH NOTE
# ---------------------------------------------------------

def generate_english_note(info):

    age = format_value(
        info.get("age"),
        "English",
    )

    symptoms = translate_list(
        info.get("symptoms", []),
        "English",
    )

    duration = format_value(
        info.get("duration"),
        "English",
    )

    severity = format_value(
        info.get("severity"),
        "English",
    )

    allergies = format_value(
        info.get("allergies"),
        "English",
    )

    history = translate_list(
        info.get("medical_history", []),
        "English",
    )

    medications = translate_list(
        info.get("medications", []),
        "English",
    )

    investigations = translate_list(
        info.get("investigations", []),
        "English",
    )

    diagnosis = translate_list(
        info.get("diagnosis", []),
        "English",
    )

    plan = translate_list(
        info.get("plan", []),
        "English",
    )

    precautions = generate_precautions(
        info,
        "English",
    )

    note = f"""
CLINICAL NOTE
=============

Patient Age:
{age}

Chief Complaints:
{symptoms}

Duration:
{duration}

Severity:
{severity}

Allergies:
{allergies}

Medical History:
{history}

Medications:
{medications}

Investigations:
{investigations}

Assessment / Diagnosis:
{diagnosis}

Plan:
{plan}

Precautions / Clinical Considerations:
{precautions}

Clinical Disclaimer:
{DISCLAIMER["English"]}
"""

    return note.strip()


# ---------------------------------------------------------
# HINDI NOTE
# ---------------------------------------------------------

def generate_hindi_note(info):

    age = format_value(
        info.get("age"),
        "Hindi",
    )

    symptoms = translate_list(
        info.get("symptoms", []),
        "Hindi",
    )

    duration = format_value(
        info.get("duration"),
        "Hindi",
    )

    severity = format_value(
        info.get("severity"),
        "Hindi",
    )

    allergies = format_value(
        info.get("allergies"),
        "Hindi",
    )

    history = translate_list(
        info.get("medical_history", []),
        "Hindi",
    )

    medications = translate_list(
        info.get("medications", []),
        "Hindi",
    )

    investigations = translate_list(
        info.get("investigations", []),
        "Hindi",
    )

    diagnosis = translate_list(
        info.get("diagnosis", []),
        "Hindi",
    )

    plan = translate_list(
        info.get("plan", []),
        "Hindi",
    )

    precautions = generate_precautions(
        info,
        "Hindi",
    )

    note = f"""
क्लिनिकल नोट
============

मरीज की आयु:
{age}

मुख्य शिकायतें:
{symptoms}

अवधि:
{duration}

गंभीरता:
{severity}

एलर्जी:
{allergies}

चिकित्सा इतिहास:
{history}

दवाएं:
{medications}

जांच:
{investigations}

मूल्यांकन / निदान:
{diagnosis}

योजना:
{plan}

सावधानियां / चिकित्सकीय विचार:
{precautions}

चिकित्सकीय अस्वीकरण:
{DISCLAIMER["Hindi"]}
"""

    return note.strip()


# ---------------------------------------------------------
# TELUGU NOTE
# ---------------------------------------------------------

def generate_telugu_note(info):

    age = format_value(
        info.get("age"),
        "Telugu",
    )

    symptoms = translate_list(
        info.get("symptoms", []),
        "Telugu",
    )

    duration = format_value(
        info.get("duration"),
        "Telugu",
    )

    severity = format_value(
        info.get("severity"),
        "Telugu",
    )

    allergies = format_value(
        info.get("allergies"),
        "Telugu",
    )

    history = translate_list(
        info.get("medical_history", []),
        "Telugu",
    )

    medications = translate_list(
        info.get("medications", []),
        "Telugu",
    )

    investigations = translate_list(
        info.get("investigations", []),
        "Telugu",
    )

    diagnosis = translate_list(
        info.get("diagnosis", []),
        "Telugu",
    )

    plan = translate_list(
        info.get("plan", []),
        "Telugu",
    )

    precautions = generate_precautions(
        info,
        "Telugu",
    )

    note = f"""
క్లినికల్ నోట్
=============

రోగి వయస్సు:
{age}

ప్రధాన ఫిర్యాదులు:
{symptoms}

వ్యవధి:
{duration}

తీవ్రత:
{severity}

అలర్జీలు:
{allergies}

వైద్య చరిత్ర:
{history}

మందులు:
{medications}

పరీక్షలు:
{investigations}

అంచనా / నిర్ధారణ:
{diagnosis}

చికిత్స ప్రణాళిక:
{plan}

జాగ్రత్తలు / వైద్యపరమైన సూచనలు:
{precautions}

వైద్య నిరాకరణ:
{DISCLAIMER["Telugu"]}
"""

    return note.strip()


# ---------------------------------------------------------
# MAIN NOTE GENERATOR
# ---------------------------------------------------------

def generate_clinical_note(
    info,
    language="English",
):

    language = normalize_language(language)

    if language == "Hindi":
        return generate_hindi_note(info)

    if language == "Telugu":
        return generate_telugu_note(info)

    return generate_english_note(info)
