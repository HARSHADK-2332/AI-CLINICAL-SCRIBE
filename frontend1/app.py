import json
from datetime import date
from typing import Any, Dict, Optional

import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Clinical Scribe",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
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


if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "patient" not in st.session_state:
    st.session_state.patient = {}

if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

if "clinical_note" not in st.session_state:
    st.session_state.clinical_note = DEFAULT_NOTE.copy()

if "note_id" not in st.session_state:
    st.session_state.note_id = None

if "backend_url" not in st.session_state:
    st.session_state.backend_url = "http://127.0.0.1:8000"

if "backend_status" not in st.session_state:
    st.session_state.backend_status = None

if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

if "recording_language" not in st.session_state:
    st.session_state.recording_language = "English"

if "report_language" not in st.session_state:
    st.session_state.report_language = "English"


# ============================================================
# BACKEND HELPERS
# ============================================================


def get_backend_url() -> str:
    """Return the configured FastAPI URL without a trailing slash."""
    return st.session_state.backend_url.rstrip("/")


def backend_request(
    method: str,
    endpoint: str,
    **kwargs: Any,
) -> requests.Response:
    """Send a request to FastAPI with a configurable timeout."""
    url = f"{get_backend_url()}{endpoint}"

    # Remove timeout from kwargs first so it is never passed twice.
    request_timeout = kwargs.pop("timeout", 180)

    return requests.request(
        method=method,
        url=url,
        timeout=request_timeout,
        **kwargs,
    )


def get_error_message(response: requests.Response) -> str:
    """Extract a readable FastAPI error message."""
    try:
        data = response.json()
        if isinstance(data, dict):
            detail = data.get("detail")
            if detail:
                return str(detail)
    except ValueError:
        pass

    return response.text or f"Backend returned HTTP {response.status_code}."


def check_backend() -> bool:
    """Check the FastAPI health endpoint."""
    try:
        response = backend_request("GET", "/api/health", timeout=10)
        return response.ok
    except requests.RequestException:
        return False


def clean_display(value: Any) -> str:
    """Convert backend values into readable text for Streamlit fields."""
    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    if isinstance(value, dict):
        return json.dumps(value, indent=2, ensure_ascii=False)

    return str(value)


def parse_list_field(value: str):
    """Convert a comma/newline separated field into a list."""
    if not value.strip():
        return []

    parts = []
    for line in value.replace("\n", ",").split(","):
        item = line.strip()
        if item:
            parts.append(item)
    return parts


def load_note_from_pipeline(result: Dict[str, Any]) -> None:
    """Map the backend process-audio response into editable UI fields."""
    structured = result.get("structured_note") or {}
    medical = result.get("medical_information") or {}

    recording_language = result.get(
        "recording_language",
        "English",
    )

    report_language = result.get(
        "report_language",
        result.get("language", "English"),
    )

    st.session_state.clinical_note = {
        "Chief Complaint": clean_display(
            structured.get("chief_complaint")
            or medical.get("symptoms")
        ),
        "History of Present Illness": clean_display(
            structured.get("history_of_present_illness")
        ),
        "Assessment": clean_display(
            structured.get("assessment")
            or medical.get("diagnosis")
        ),
        "Plan": clean_display(
            structured.get("plan")
            or medical.get("plan")
        ),
        "Allergies": clean_display(
            structured.get("allergies")
            or medical.get("allergies")
        ),
        "Medications": clean_display(
            structured.get("medications")
            or medical.get("medications")
        ),
        "Investigations": clean_display(
            structured.get("investigations")
            or medical.get("investigations")
        ),
        "Status": structured.get("status", "draft"),
        "Language": report_language,
        "Recording Language": recording_language,
        "Report Language": report_language,
    }

    st.session_state.note_id = structured.get("id")

    st.session_state.recording_language = (
        recording_language
    )

    st.session_state.report_language = (
        report_language
    )

    st.session_state.selected_language = (
        report_language
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🏥 AI Clinical Scribe")
    st.caption("Intelligent Clinical Documentation")
    st.divider()

    st.divider()
    st.subheader("Navigation")

    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button("👤 Patient Information", use_container_width=True):
        st.session_state.page = "Patient"
        st.rerun()

    if st.button("🎙️ Consultation", use_container_width=True):
        st.session_state.page = "Consultation"
        st.rerun()

    if st.button("📝 Clinical Note", use_container_width=True):
        st.session_state.page = "Clinical Note"
        st.rerun()

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
        "Turn doctor-patient conversations into clear, structured clinical "
        "documentation for clinician review."
    )
    st.divider()

    st.info(
        "💡 Start a new consultation by entering patient information first."
    )

    if st.button(
        "🚀 Start New Consultation",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.page = "Patient"
        st.rerun()

    st.divider()

    st.divider()

    st.header("Current Session")

    if st.session_state.patient:
        patient = st.session_state.patient

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.write("**Patient**")
            st.write(patient.get("name", "-"))

        with col2:
            st.write("**Patient ID**")
            st.write(patient.get("id", "-"))

        with col3:
            st.write("**Age**")
            st.write(patient.get("age", "-"))

        with col4:
            st.write("**Doctor**")
            st.write(patient.get("doctor", "-"))
    else:
        st.info("No consultation has been started yet.")


# ============================================================
# PATIENT PAGE
# ============================================================


def patient_page():
    st.title("👤 Patient Information")
    st.write(
        "Enter the patient and doctor details before starting the consultation."
    )
    st.divider()

    patient = st.session_state.patient

    col1, col2 = st.columns(2)

    with col1:
        patient_name = st.text_input(
            "Patient Name *",
            value=patient.get("name", ""),
            placeholder="Enter patient name",
        )

        patient_id = st.text_input(
            "Patient ID",
            value=patient.get("id", ""),
            placeholder="Example: PT-2026-001",
            help=(
                "This is the hospital/application patient identifier. "
                "The current process-audio endpoint accepts an optional "
                "numeric database patient_id, so this display ID is kept "
                "in the current frontend session."
            ),
        )

        age = st.number_input(
            "Age *",
            min_value=0,
            max_value=120,
            value=patient.get("age", 0),
        )

    with col2:
        gender_options = ["Select", "Male", "Female", "Other"]
        current_gender = patient.get("gender", "Select")

        if current_gender not in gender_options:
            current_gender = "Select"

        gender = st.selectbox(
            "Gender *",
            gender_options,
            index=gender_options.index(current_gender),
        )

        doctor_name = st.text_input(
            "Doctor Name *",
            value=patient.get("doctor", ""),
            placeholder="Enter doctor name",
        )

        consultation_date = st.date_input(
            "Consultation Date",
            value=patient.get("date", date.today()),
        )

    st.divider()

    st.info(
        "Please verify the patient details before starting the consultation."
    )

    if st.button(
        "Continue to Consultation →",
        type="primary",
        use_container_width=True,
    ):
        if not patient_name.strip():
            st.error("Please enter the patient name.")
        elif age == 0:
            st.error("Please enter the patient's age.")
        elif gender == "Select":
            st.error("Please select the patient's gender.")
        elif not doctor_name.strip():
            st.error("Please enter the doctor's name.")
        else:
            st.session_state.patient = {
                "name": patient_name.strip(),
                "id": patient_id.strip(),
                "age": age,
                "gender": gender,
                "doctor": doctor_name.strip(),
                "date": consultation_date,
            }
            st.session_state.page = "Consultation"
            st.rerun()


# ============================================================
# CONSULTATION PAGE
# ============================================================


def consultation_page():
    st.title("🎙️ Consultation")
    st.write(
        "Record the doctor-patient conversation or upload an existing "
        "consultation recording."
    )
    st.divider()

    patient = st.session_state.patient

    if not patient:
        st.warning("Please enter patient information first.")
        if st.button("Go to Patient Information", type="primary"):
            st.session_state.page = "Patient"
            st.rerun()
        return

    st.subheader("Patient")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("**Name**")
        st.write(patient.get("name", "-"))

    with col2:
        st.write("**Patient ID**")
        st.write(patient.get("id", "-"))

    with col3:
        st.write("**Age**")
        st.write(patient.get("age", "-"))

    with col4:
        st.write("**Doctor**")
        st.write(patient.get("doctor", "-"))

    st.divider()

    st.header("🎙️ Record Consultation")

    audio_recording = st.audio_input(
        "Start / Stop Recording"
    )

    if audio_recording:
        st.session_state.audio_file = audio_recording
        st.success("Consultation recording captured successfully.")
        st.audio(audio_recording)

    st.divider()

    st.header("📁 Upload Existing Recording")

    uploaded_audio = st.file_uploader(
        "Choose an audio file",
        type=[
            "wav",
            "mp3",
            "m4a",
            "webm",
            "ogg",
            "flac",
            "mp4",
        ],
        help="Maximum size: 25 MB.",
    )

    if uploaded_audio:
        st.session_state.audio_file = uploaded_audio
        st.success(f"Uploaded: {uploaded_audio.name}")
        st.audio(uploaded_audio)

    st.divider()

    st.subheader("🌐 Doctor Report Language")

    language_options = [
        "English",
        "Hindi",
        "Telugu",
    ]

    current_report_language = st.session_state.get(
        "report_language",
        "English",
    )

    if current_report_language not in language_options:
        current_report_language = "English"

    selected_language = st.selectbox(
        "Clinical report language",
        language_options,
        index=language_options.index(
            current_report_language
        ),
        help=(
            "Choose the language in which the clinical report "
            "should be generated for the doctor."
        ),
    )

    st.session_state.selected_language = selected_language
    st.session_state.report_language = selected_language

    st.caption(
        "The consultation recording may be in English, Hindi or Telugu. "
        "The recording language is detected separately, while the clinical "
        "report is generated in the language selected above."
    )

    st.divider()

    if st.button(
        "🚀 Process Consultation",
        type="primary",
        use_container_width=True,
    ):
        if st.session_state.audio_file is None:
            st.warning("Please record or upload a consultation first.")
            return

        process_consultation()


# ============================================================
# PROCESS AUDIO
# ============================================================


def process_consultation():
    """Send audio directly to POST /api/notes/process-audio."""

    audio_file = st.session_state.audio_file

    if audio_file == "demo_audio":
        st.error(
            "Demo processing has been removed because the backend now "
            "performs real Whisper transcription. Please upload or record "
            "an actual consultation audio file."
        )
        return

    try:
        with st.spinner(
            "🎙️ Processing consultation and preparing the clinical note..."
        ):
            file_bytes = audio_file.getvalue()

            filename = getattr(
                audio_file,
                "name",
                "consultation.wav",
            )

            mime_type = getattr(
                audio_file,
                "type",
                None,
            ) or "audio/wav"

            files = {
                "file": (
                    filename,
                    file_bytes,
                    mime_type,
                )
            }

            # The current backend accepts patient_id as an optional numeric
            # database ID. The frontend's human-readable patient ID is kept
            # separately, so we intentionally do not send it as patient_id.
            report_language = st.session_state.get(
                "report_language",
                "English",
            )

            data = {
                "language": report_language,
            }

            response = backend_request(
                "POST",
                "/api/notes/process-audio",
                files=files,
                data=data,
                timeout=300,
            )

        if not response.ok:
            st.error(
                "Backend processing failed: "
                + get_error_message(response)
            )
            return

        result = response.json()

        st.session_state.pipeline_result = result
        load_note_from_pipeline(result)
        st.session_state.page = "Clinical Note"

        st.success(
            "✅ Consultation processed and clinical note generated successfully."
        )
        st.rerun()

    except requests.Timeout:
        st.error(
            "The AI pipeline took too long to respond. "
            "Whisper can take time on CPU for longer recordings."
        )

    except requests.RequestException as exc:
        st.error(
            f"Could not connect to FastAPI: {exc}"
        )

    except Exception as exc:
        st.error(
            f"Unexpected frontend error: {exc}"
        )


# ============================================================
# CLINICAL NOTE PAGE
# ============================================================


def clinical_note_page():
    st.title("📝 Clinical Note")
    st.write(
        "Review, edit and save the clinical documentation generated by "
        "the FastAPI AI pipeline."
    )
    st.divider()

    patient = st.session_state.patient

    st.subheader("Patient Information")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write("**Patient**")
        st.write(patient.get("name", "Not provided"))

    with col2:
        st.write("**Patient ID**")
        st.write(patient.get("id", "Not provided"))

    with col3:
        st.write("**Doctor**")
        st.write(patient.get("doctor", "Not provided"))

    with col4:
        st.write("**Note ID**")
        st.write(st.session_state.note_id or "Not saved")

    st.divider()

    result = st.session_state.pipeline_result

    if result:
        st.subheader("📝 Transcript")
        st.text_area(
            "Whisper Transcript",
            value=result.get("transcript", ""),
            height=180,
            disabled=True,
        )

        with st.expander("View cleaned transcript"):
            st.write(
                result.get(
                    "cleaned_transcript",
                    "",
                )
            )

        st.divider()

        st.subheader("🔍 AI Extracted Information")

        medical = result.get(
            "medical_information",
            {},
        )

        if isinstance(medical, dict) and medical:
            # Keep the complete backend output visible for debugging.
            st.json(medical)

            # Show a clear warning when extraction returned no useful values.
            empty_values = {
                None,
                "",
                "Not mentioned",
                "None reported",
                "null",
            }

            def has_content(value):
                if value is None:
                    return False
                if isinstance(value, str):
                    return value.strip() not in empty_values
                if isinstance(value, (list, tuple, set)):
                    return any(has_content(item) for item in value)
                if isinstance(value, dict):
                    return any(has_content(item) for item in value.values())
                return True

            useful_fields = [
                key for key, value in medical.items()
                if has_content(value)
            ]

            if not useful_fields:
                st.warning(
                    "The audio transcript was received, but the backend did not "
                    "extract any clinical details. This is not a frontend default. "
                    "Check the transcript above and update ai/clinical_extractor.py "
                    "to recognize the words used in this recording."
                )
            else:
                st.success(
                    f"Extracted information is available for {len(useful_fields)} "
                    "field(s). Please verify it against the transcript."
                )

            # Human-readable summary makes missing fields easy to spot.
            st.markdown("**Extraction summary**")
            summary_fields = [
                ("Age", "age"),
                ("Symptoms", "symptoms"),
                ("Duration", "duration"),
                ("Severity", "severity"),
                ("Allergies", "allergies"),
                ("Medications", "medications"),
                ("Medical history", "medical_history"),
                ("Investigations", "investigations"),
                ("Diagnosis", "diagnosis"),
                ("Plan", "plan"),
            ]

            for label, key in summary_fields:
                value = medical.get(key)
                if not has_content(value):
                    display_value = "Not extracted — check transcript/backend extractor"
                else:
                    display_value = clean_display(value)
                st.write(f"**{label}:** {display_value}")
        else:
            st.warning(
                "No structured medical information was returned by the backend. "
                "Check the API response and ai/clinical_extractor.py."
            )

        st.divider()

    st.subheader("Clinical Documentation")

    note = st.session_state.clinical_note

    note["Chief Complaint"] = st.text_area(
        "Chief Complaint",
        value=note.get("Chief Complaint", ""),
        height=100,
    )

    note["History of Present Illness"] = st.text_area(
        "History of Present Illness",
        value=note.get(
            "History of Present Illness",
            "",
        ),
        height=140,
    )

    col1, col2 = st.columns(2)

    with col1:
        note["Assessment"] = st.text_area(
            "Assessment / Diagnosis",
            value=note.get("Assessment", ""),
            height=130,
        )

        note["Allergies"] = st.text_area(
            "Allergies",
            value=note.get("Allergies", ""),
            height=100,
        )

        note["Medications"] = st.text_area(
            "Medications",
            value=note.get("Medications", ""),
            height=120,
        )

    with col2:
        note["Plan"] = st.text_area(
            "Treatment Plan",
            value=note.get("Plan", ""),
            height=130,
        )

        note["Investigations"] = st.text_area(
            "Investigations",
            value=note.get("Investigations", ""),
            height=120,
        )

        note["Status"] = st.selectbox(
            "Note Status",
            ["draft", "reviewed"],
            index=0 if note.get("Status", "draft") == "draft" else 1,
        )

    st.session_state.clinical_note = note

    st.divider()

    st.subheader("🌐 Language Information")

    recording_language = (
        result.get(
            "recording_language",
            note.get(
                "Recording Language",
                st.session_state.get(
                    "recording_language",
                    "English",
                ),
            ),
        )
        if result
        else note.get(
            "Recording Language",
            st.session_state.get(
                "recording_language",
                "English",
            ),
        )
    )

    report_language = (
        result.get(
            "report_language",
            note.get(
                "Report Language",
                note.get(
                    "Language",
                    st.session_state.get(
                        "report_language",
                        "English",
                    ),
                ),
            ),
        )
        if result
        else note.get(
            "Report Language",
            note.get(
                "Language",
                st.session_state.get(
                    "report_language",
                    "English",
                ),
            ),
        )
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Recording Language",
            recording_language,
        )

    with col2:
        st.metric(
            "Report Language",
            report_language,
        )

    st.caption(
        "Recording Language shows the language detected from the consultation. "
        "Report Language shows the language selected by the doctor for the "
        "generated clinical note."
    )

    st.divider()

    # ========================================================
    # SAVE EDITS TO BACKEND
    # ========================================================

    if st.button(
        "💾 Save Clinical Note",
        type="primary",
        use_container_width=True,
    ):
        save_note_changes()

    st.divider()

    # ========================================================
    # EXPORT FROM BACKEND
    # ========================================================

    st.subheader("📥 Export Clinical Note")

    export_format = st.selectbox(
        "Choose export format",
        [
            "soap",
            "txt",
            "json",
        ],
        format_func=lambda value: value.upper(),
    )

    if st.button(
        "Prepare Download",
        use_container_width=True,
    ):
        export_note_from_backend(export_format)


# ============================================================
# SAVE NOTE
# ============================================================


def save_note_changes():
    """Update the database note using PUT /api/notes/{note_id}."""

    note_id = st.session_state.note_id

    if not note_id:
        st.warning(
            "There is no backend note ID yet. Process an audio consultation first."
        )
        return

    note = st.session_state.clinical_note

    payload = {
        "chief_complaint": note.get("Chief Complaint", ""),
        "history_of_present_illness": note.get(
            "History of Present Illness",
            "",
        ),
        "assessment": note.get("Assessment", ""),
        "plan": parse_list_field(note.get("Plan", "")),
        "allergies": parse_list_field(note.get("Allergies", "")),
        "medications": parse_list_field(
            note.get("Medications", "")
        ),
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
                "Could not save changes: "
                + get_error_message(response)
            )
            return

        updated = response.json()
        st.success(
            f"✅ Clinical note #{note_id} updated successfully."
        )

        # Keep the UI synchronized with the backend response.
        if isinstance(updated, dict):
            st.session_state.clinical_note["Status"] = updated.get(
                "status",
                st.session_state.clinical_note["Status"],
            )

    except requests.RequestException as exc:
        st.error(f"Could not connect to FastAPI: {exc}")


# ============================================================
# EXPORT NOTE
# ============================================================


def export_note_from_backend(export_format: str):
    """Download the note using the backend export endpoint."""

    note_id = st.session_state.note_id

    if not note_id:
        st.warning(
            "There is no backend note ID yet. Process an audio consultation first."
        )
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
                "Export failed: "
                + get_error_message(response)
            )
            return

        content_type = response.headers.get(
            "content-type",
            "text/plain",
        )

        extension = export_format
        if export_format == "soap":
            extension = "md"

        filename = (
            f"clinical_note_{note_id}.{extension}"
        )

        content = response.content

        st.download_button(
            "📥 Download Clinical Note",
            data=content,
            file_name=filename,
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


st.divider()

st.caption(
    "🏥 AI Clinical Scribe • FastAPI + Whisper + Clinical AI"
)
