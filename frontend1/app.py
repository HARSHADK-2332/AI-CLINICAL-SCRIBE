
import json
import os
from datetime import date
from typing import Any

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Clinical Scribe",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_API_URL = "https://ai-clinical-scribe-api-3dha.onrender.com"

try:
    configured_url = st.secrets.get("API_URL", DEFAULT_API_URL)
except Exception:
    configured_url = os.getenv("API_URL", DEFAULT_API_URL)

API_URL = str(configured_url).strip().rstrip("/")

if not API_URL.startswith("https://"):
    st.error("API_URL must be the HTTPS URL of your deployed FastAPI backend.")
    st.stop()


# ============================================================
# DEFAULT VALUES AND SESSION STATE
# ============================================================

DEFAULT_NOTE = {
    "Chief Complaint": "",
    "History of Present Illness": "",
    "Assessment": "",
    "Plan": "",
    "Allergies": "",
    "Medications": "",
    "Investigations": "",
    "Status": "draft",
    "Language": "English",
}

DEFAULTS = {
    "page": "Dashboard",
    "patient": {},
    "audio_file": None,
    "pipeline_result": None,
    "clinical_note": DEFAULT_NOTE.copy(),
    "note_id": None,
    "selected_language": "English",
    "recording_language": "English",
    "report_language": "English",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = (
            value.copy() if isinstance(value, dict) else value
        )

# Always use the configured backend URL. Do not reuse an old localhost URL.
st.session_state["backend_url"] = API_URL


# ============================================================
# BACKEND HELPERS
# ============================================================

def get_backend_url() -> str:
    """Return the configured Render backend URL."""
    return API_URL


def backend_request(
    method: str,
    endpoint: str,
    **kwargs: Any,
) -> requests.Response:
    """Send a request to FastAPI using the deployed backend."""
    endpoint = "/" + endpoint.lstrip("/")
    url = f"{get_backend_url()}{endpoint}"

    timeout = kwargs.pop("timeout", 60)

    return requests.request(
        method=method,
        url=url,
        timeout=timeout,
        **kwargs,
    )


def get_error_message(response: requests.Response) -> str:
    """Extract a readable API error."""
    try:
        payload = response.json()
        if isinstance(payload, dict) and payload.get("detail"):
            return str(payload["detail"])
        return json.dumps(payload, ensure_ascii=False)
    except (ValueError, json.JSONDecodeError):
        return response.text or f"HTTP {response.status_code}"


def clean_display(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def parse_list_field(value: str) -> list[str]:
    return [
        item.strip()
        for item in value.replace("\n", ",").split(",")
        if item.strip()
    ]


def check_backend() -> bool:
    try:
        response = backend_request("GET", "/api/health", timeout=15)
        return response.ok
    except requests.RequestException:
        return False


def load_note_from_pipeline(result: dict) -> None:
    structured = result.get("structured_note") or {}
    medical = result.get("medical_information") or {}

    recording_language = result.get("recording_language", "English")
    report_language = result.get(
        "report_language",
        result.get("language", "English"),
    )

    st.session_state.clinical_note = {
        "Chief Complaint": clean_display(
            structured.get("chief_complaint") or medical.get("symptoms")
        ),
        "History of Present Illness": clean_display(
            structured.get("history_of_present_illness")
        ),
        "Assessment": clean_display(
            structured.get("assessment") or medical.get("diagnosis")
        ),
        "Plan": clean_display(
            structured.get("plan") or medical.get("plan")
        ),
        "Allergies": clean_display(
            structured.get("allergies") or medical.get("allergies")
        ),
        "Medications": clean_display(
            structured.get("medications") or medical.get("medications")
        ),
        "Investigations": clean_display(
            structured.get("investigations") or medical.get("investigations")
        ),
        "Status": structured.get("status", "draft"),
        "Language": report_language,
        "Recording Language": recording_language,
        "Report Language": report_language,
    }

    st.session_state.note_id = structured.get("id")
    st.session_state.recording_language = recording_language
    st.session_state.report_language = report_language
    st.session_state.selected_language = report_language


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🏥 AI Clinical Scribe")
    st.caption("Intelligent Clinical Documentation")
    st.divider()

    pages = {
        "🏠 Dashboard": "Dashboard",
        "👤 Patient Information": "Patient",
        "🎙️ Consultation": "Consultation",
        "📝 Clinical Note": "Clinical Note",
    }

    for label, page in pages.items():
        if st.button(label, use_container_width=True):
            st.session_state.page = page
            st.rerun()

    st.divider()

    if st.button("🔌 Check Backend", use_container_width=True):
        with st.spinner("Checking Render backend..."):
            if check_backend():
                st.success("FastAPI is reachable.")
            else:
                st.error(
                    "Could not reach FastAPI. Check the Render service "
                    "and its logs."
                )

    st.caption("Backend endpoint")
    st.code(API_URL, language=None)

    st.divider()
    st.caption(
        "AI-generated clinical documentation must be reviewed and verified "
        "by a qualified healthcare professional before clinical use."
    )


# ============================================================
# DASHBOARD
# ============================================================

def dashboard_page():
    st.title("🏥 AI Clinical Scribe")
    st.subheader("Intelligent Clinical Documentation")

    st.write(
        "Turn doctor-patient conversations into structured clinical "
        "documentation for clinician review."
    )

    if st.button(
        "🚀 Start New Consultation",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.page = "Patient"
        st.rerun()

    st.divider()
    st.header("Current Session")

    patient = st.session_state.patient

    if patient:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Patient", patient.get("name", "-"))
        col2.metric("Patient ID", patient.get("id", "-"))
        col3.metric("Age", str(patient.get("age", "-")))
        col4.metric("Doctor", patient.get("doctor", "-"))
    else:
        st.info("No consultation has been started yet.")


# ============================================================
# PATIENT INFORMATION
# ============================================================

def patient_page():
    st.title("👤 Patient Information")
    st.write("Enter patient and doctor details before the consultation.")

    patient = st.session_state.patient

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Patient Name *",
            value=patient.get("name", ""),
        )
        patient_id = st.text_input(
            "Patient ID",
            value=patient.get("id", ""),
            placeholder="Example: PT-2026-001",
        )
        age = st.number_input(
            "Age *",
            min_value=0,
            max_value=120,
            value=int(patient.get("age", 0)),
        )

    with col2:
        genders = ["Select", "Male", "Female", "Other"]
        old_gender = patient.get("gender", "Select")
        if old_gender not in genders:
            old_gender = "Select"

        gender = st.selectbox(
            "Gender *",
            genders,
            index=genders.index(old_gender),
        )
        doctor = st.text_input(
            "Doctor Name *",
            value=patient.get("doctor", ""),
        )
        consultation_date = st.date_input(
            "Consultation Date",
            value=patient.get("date", date.today()),
        )

    if st.button(
        "Continue to Consultation →",
        type="primary",
        use_container_width=True,
    ):
        if not name.strip():
            st.error("Please enter the patient's name.")
        elif age <= 0:
            st.error("Please enter a valid age.")
        elif gender == "Select":
            st.error("Please select the patient's gender.")
        elif not doctor.strip():
            st.error("Please enter the doctor's name.")
        else:
            st.session_state.patient = {
                "name": name.strip(),
                "id": patient_id.strip(),
                "age": age,
                "gender": gender,
                "doctor": doctor.strip(),
                "date": consultation_date,
            }
            st.session_state.page = "Consultation"
            st.rerun()


# ============================================================
# CONSULTATION
# ============================================================

def consultation_page():
    st.title("🎙️ Consultation")
    st.write("Record a consultation or upload an existing audio recording.")

    patient = st.session_state.patient

    if not patient:
        st.warning("Please enter patient information first.")
        if st.button("Go to Patient Information"):
            st.session_state.page = "Patient"
            st.rerun()
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patient", patient.get("name", "-"))
    col2.metric("Patient ID", patient.get("id", "-"))
    col3.metric("Age", str(patient.get("age", "-")))
    col4.metric("Doctor", patient.get("doctor", "-"))

    st.divider()
    st.subheader("🎙️ Record Consultation")

    recording = st.audio_input("Start / Stop Recording")

    if recording is not None:
        st.session_state.audio_file = recording
        st.audio(recording)

    st.divider()
    st.subheader("📁 Upload Existing Recording")

    uploaded = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a", "webm", "ogg", "flac", "mp4"],
        help="Use a supported audio file. Keep within your deployment's size limits.",
    )

    if uploaded is not None:
        st.session_state.audio_file = uploaded
        st.audio(uploaded)

    st.divider()

    languages = ["English", "Hindi", "Telugu"]
    current_language = st.session_state.report_language

    if current_language not in languages:
        current_language = "English"

    report_language = st.selectbox(
        "Clinical report language",
        languages,
        index=languages.index(current_language),
        help="Select the language for the generated clinical report.",
    )

    st.session_state.report_language = report_language
    st.session_state.selected_language = report_language

    st.caption(
        "The recording may be in English, Hindi or Telugu. The backend "
        "must support transcription and report generation for the chosen "
        "languages."
    )

    if st.button(
        "🚀 Process Consultation",
        type="primary",
        use_container_width=True,
    ):
        if st.session_state.audio_file is None:
            st.warning("Please record or upload an audio file first.")
            return

        process_consultation()


# ============================================================
# AUDIO PROCESSING
# ============================================================

def process_consultation():
    """Upload audio to the deployed FastAPI process-audio endpoint."""

    audio_file = st.session_state.audio_file

    try:
        file_bytes = audio_file.getvalue()

        if not file_bytes:
            st.error("The selected audio file is empty.")
            return

        filename = getattr(audio_file, "name", "consultation.wav")
        mime_type = getattr(audio_file, "type", None) or "application/octet-stream"

        files = {
            "file": (filename, file_bytes, mime_type),
        }
        data = {
            "language": st.session_state.report_language,
        }

        with st.spinner(
            "Processing audio. This can take several minutes..."
        ):
            response = backend_request(
                "POST",
                "/api/notes/process-audio",
                files=files,
                data=data,
                timeout=300,
            )

        if not response.ok:
            st.error(
                f"FastAPI returned HTTP {response.status_code}: "
                f"{get_error_message(response)}"
            )
            return

        try:
            result = response.json()
        except ValueError:
            st.error("FastAPI returned a response that was not valid JSON.")
            return

        if not isinstance(result, dict):
            st.error("FastAPI returned an unexpected response format.")
            return

        st.session_state.pipeline_result = result
        load_note_from_pipeline(result)
        st.session_state.page = "Clinical Note"

        st.success("Audio processing completed.")
        st.rerun()

    except requests.Timeout:
        st.error(
            "The audio-processing request timed out. Check the Render logs "
            "and backend processing limits, then try a shorter recording."
        )

    except requests.ConnectionError:
        st.error(
            "Could not reach the configured FastAPI backend. "
            "The request was sent to: " + API_URL
        )

    except requests.RequestException as exc:
        st.error(f"FastAPI request failed: {exc}")

    except Exception as exc:
        st.error(f"Unexpected audio-processing error: {exc}")


# ============================================================
# CLINICAL NOTE
# ============================================================

def clinical_note_page():
    st.title("📝 Clinical Note")
    st.write("Review and edit the generated note before saving it.")

    patient = st.session_state.patient

    col1, col2, col3 = st.columns(3)
    col1.metric("Patient", patient.get("name", "Not provided"))
    col2.metric("Doctor", patient.get("doctor", "Not provided"))
    col3.metric("Note ID", str(st.session_state.note_id or "Not saved"))

    result = st.session_state.pipeline_result

    if result:
        st.subheader("🎙️ Transcript")
        st.text_area(
            "Transcribed consultation",
            value=result.get("transcript", ""),
            height=180,
            disabled=True,
        )

        with st.expander("View cleaned transcript"):
            st.write(result.get("cleaned_transcript", ""))

        medical = result.get("medical_information") or {}

        if medical:
            st.subheader("Extracted Medical Information")
            st.json(medical)

        st.warning(
            "Verify every extracted clinical detail against the transcript. "
            "Do not use an unverified AI-generated note for clinical decisions."
        )

    st.divider()
    note = st.session_state.clinical_note

    note["Chief Complaint"] = st.text_area(
        "Chief Complaint",
        value=note.get("Chief Complaint", ""),
        height=90,
    )

    note["History of Present Illness"] = st.text_area(
        "History of Present Illness",
        value=note.get("History of Present Illness", ""),
        height=130,
    )

    col1, col2 = st.columns(2)

    with col1:
        note["Assessment"] = st.text_area(
            "Assessment / Diagnosis",
            value=note.get("Assessment", ""),
            height=120,
        )
        note["Allergies"] = st.text_area(
            "Allergies",
            value=note.get("Allergies", ""),
        )
        note["Medications"] = st.text_area(
            "Medications",
            value=note.get("Medications", ""),
        )

    with col2:
        note["Plan"] = st.text_area(
            "Treatment Plan",
            value=note.get("Plan", ""),
            height=120,
        )
        note["Investigations"] = st.text_area(
            "Investigations",
            value=note.get("Investigations", ""),
        )

        statuses = ["draft", "reviewed"]
        current_status = note.get("Status", "draft")
        if current_status not in statuses:
            current_status = "draft"

        note["Status"] = st.selectbox(
            "Note Status",
            statuses,
            index=statuses.index(current_status),
        )

    st.session_state.clinical_note = note

    st.subheader("🌐 Language Information")
    col1, col2 = st.columns(2)
    col1.metric(
        "Recording Language",
        str(
            (result or {}).get(
                "recording_language",
                st.session_state.recording_language,
            )
        ),
    )
    col2.metric(
        "Report Language",
        str(
            (result or {}).get(
                "report_language",
                st.session_state.report_language,
            )
        ),
    )

    if st.button(
        "💾 Save Clinical Note",
        type="primary",
        use_container_width=True,
    ):
        save_note_changes()

    st.divider()
    st.subheader("📥 Export Clinical Note")

    export_format = st.selectbox(
        "Choose export format",
        ["soap", "txt", "json"],
        format_func=lambda value: value.upper(),
    )

    if st.button("Prepare Download", use_container_width=True):
        export_note_from_backend(export_format)


# ============================================================
# SAVE NOTE
# ============================================================

def save_note_changes():
    note_id = st.session_state.note_id

    if not note_id:
        st.warning("Process an audio consultation before saving a backend note.")
        return

    note = st.session_state.clinical_note

    payload = {
        "chief_complaint": note.get("Chief Complaint", ""),
        "history_of_present_illness": note.get(
            "History of Present Illness", ""
        ),
        "assessment": note.get("Assessment", ""),
        "plan": parse_list_field(note.get("Plan", "")),
        "allergies": parse_list_field(note.get("Allergies", "")),
        "medications": parse_list_field(note.get("Medications", "")),
        "negated_findings": [],
        "status": note.get("Status", "draft"),
    }

    try:
        response = backend_request(
            "PUT",
            f"/api/notes/{note_id}",
            json=payload,
            timeout=30,
        )

        if not response.ok:
            st.error(
                f"Could not save note (HTTP {response.status_code}): "
                f"{get_error_message(response)}"
            )
            return

        st.success("Clinical note saved successfully.")

    except requests.RequestException as exc:
        st.error(f"Could not connect to FastAPI: {exc}")


# ============================================================
# EXPORT NOTE
# ============================================================

def export_note_from_backend(export_format: str):
    note_id = st.session_state.note_id

    if not note_id:
        st.warning("Process an audio consultation before exporting a note.")
        return

    try:
        response = backend_request(
            "POST",
            f"/api/notes/{note_id}/export",
            params={"format": export_format},
            timeout=30,
        )

        if not response.ok:
            st.error(
                f"Export failed (HTTP {response.status_code}): "
                f"{get_error_message(response)}"
            )
            return

        extension = "md" if export_format == "soap" else export_format
        content_type = response.headers.get(
            "content-type", "application/octet-stream"
        )

        st.download_button(
            "📥 Download Clinical Note",
            data=response.content,
            file_name=f"clinical_note_{note_id}.{extension}",
            mime=content_type,
            use_container_width=True,
        )

    except requests.RequestException as exc:
        st.error(f"Could not connect to FastAPI: {exc}")


# ============================================================
# PAGE ROUTING
# ============================================================

if st.session_state.page == "Dashboard":
    dashboard_page()

elif st.session_state.page == "Patient":
    patient_page()

elif st.session_state.page == "Consultation":
    consultation_page()

elif st.session_state.page == "Clinical Note":
    clinical_note_page()

else:
    st.session_state.page = "Dashboard"
    dashboard_page()

st.divider()
st.caption("🏥 AI Clinical Scribe • Streamlit + FastAPI + Whisper")