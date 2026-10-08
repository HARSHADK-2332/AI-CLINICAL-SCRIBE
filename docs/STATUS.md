# ScribeCare Roadmap Implementation Status

This document tracks the implementation progress of ScribeCare against the modernized architectural roadmap (Phases 1 through 4).

---

## 1. Roadmap Phase Matrix

| Phase | Milestone / Feature | Status | Implementing Files / Components | Notes |
|---|---|---|---|---|
| **Phase 1** | `.gitignore` file | **Done** | [`.gitignore`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/.gitignore) | Covers Python, Node, Vite, SQLite, audio caches. |
| **Phase 1** | Clean committed `__pycache__` | **Done** | Git index cleaned | Untracked cached bytecode from repository index. |
| **Phase 1** | Populate `requirements.txt` | **Done** | [`requirements.txt`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/requirements.txt) | Added FastAPI, Uvicorn, SQLAlchemy, Whisper, PyTorch, Pytest. |
| **Phase 1** | Fix duration regex quantifier | **Done** | [`ai/clinical_extractor.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/ai/clinical_extractor.py#L39-L50) | Updated to `(?:past\|for\|from\|about\|since)\s+(\d+)\s+(days?\|weeks?\|months?\|years?)`. |
| **Phase 1** | Fix false-positive age regex | **Done** | [`ai/clinical_extractor.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/ai/clinical_extractor.py#L4-L20) | Anchored to patient self-reference to avoid matching duration statements as age. |
| **Phase 1** | Migrate tests to `pytest` | **Done** | [`tests/test_api.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/tests/test_api.py) | Full regression suite with assertions and mocks. |
| **Phase 2** | NegEx-style negation detection | **Done** | [`backend/services/clinical.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/clinical.py#L19-L52) | Detects negated symptoms ("no fever", "denies chest pain") and records them under `negated_findings`. |
| **Phase 2** | Medical NER (spaCy / LLM) | **In Progress** | [`backend/services/clinical.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/clinical.py) | Hybrid rule-based wrapper active; scispaCy integration planned. |
| **Phase 2** | Structured allergy & medication extraction | **In Progress** | [`backend/services/clinical.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/clinical.py) | Schema ready; capability flag toggleable in UI. |
| **Phase 3** | `SpeechToTextService` with lazy model loading | **Done** | [`backend/services/speech.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/speech.py), [`ai/speech_to_text.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/ai/speech_to_text.py) | Whisper weights loaded on-demand; no blocking on import. |
| **Phase 3** | FFmpeg check with actionable error | **Done** | [`backend/services/speech.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/speech.py), [`backend/routes/transcribe.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/routes/transcribe.py) | Returns clear 503 error with platform-specific install steps. |
| **Phase 3** | Speaker Diarization | **In Progress** | [`backend/services/speech.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/speech.py) | Heuristic conversational turn alternating active; Pyannote neural diarization scheduled. |
| **Phase 4** | FastAPI Backend API | **Done** | [`backend/main.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/main.py), [`backend/routes/`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/routes) | Health, Transcribe, Notes, Patients, Demo Requests endpoints. |
| **Phase 4** | React + Vite + Tailwind CSS Frontend | **Done** | [`frontend/`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/frontend) | Accessible, responsive UI matching clinical design system. |
| **Phase 4** | Multilingual Support (`react-i18next`) | **Done** | [`frontend/src/i18n/`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/frontend/src/i18n) | Complete English, Hindi, and Telugu UI localizations. |
| **Phase 4** | Zero-dependency Mock Mode | **Done** | [`frontend/src/services/api.ts`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/frontend/src/services/api.ts) | Enabled via `VITE_USE_MOCK=true` for environments without GPU/FFmpeg. |
| **Phase 4** | SQLite Persistence & Demo Seed | **Done** | [`backend/database.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/database.py), [`backend/models.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/models.py), [`backend/seed.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/seed.py) | Seeds 3 demo patients; persists notes and demo requests. |
| **Phase 4** | Note Export (TXT, JSON, SOAP) | **Done** | [`backend/services/export.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/export.py) | File download headers and formatted SOAP markdown. |
| **Phase 4** | FHIR R4 Bundle Export | **Not Started** | [`backend/services/export.py`](file:///c:/Users/HP/OneDrive/Desktop/AI-Clinical-Scribe/backend/services/export.py#L112-L118) | Returns HTTP 501 with roadmap status notice. |

---

## 2. Known Limitations & Technical Debt

1. **Acoustic Speaker Diarization:**
   - Whisper alone transcribes audio segments but does not distinguish distinct speaker embeddings.
   - Current implementation uses a turn-alternation heuristic (`Doctor` vs. `Patient`). Neural diarization using `pyannote.audio` is scheduled for the full Phase 3 release.
2. **FHIR R4 Composition Generation:**
   - The export endpoint currently supports Plain Text, Structured JSON, and SOAP Markdown.
   - Requesting `format=fhir` returns HTTP 501 with a descriptive message explaining that FHIR R4 clinical composition bundles are slated for the Phase 4 productionization milestone.
3. **Multilingual Clinical Note Synthesis:**
   - Speech transcription accepts Hindi (`hi`) and Telugu (`te`) audio.
   - However, the extraction and note generator services currently synthesize clinical SOAP outputs in English. When Hindi or Telugu is selected in the UI, an informative banner notifies the clinician: *"Note generated in English (Multilingual clinical synthesis active)"*.
4. **Host FFmpeg Requirement:**
   - In live mode (when `VITE_USE_MOCK=false`), Whisper requires the `ffmpeg` system binary to decode uploaded audio containers. If missing, the API surfaces an informative 503 response. Mock Mode circumvents this requirement.

---

## 3. Regulatory & Clinical Safety Notice

- **HIPAA-Ready Architecture:** ScribeCare is designed to conform to HIPAA data handling standards (no logging of raw PHI to standard output, isolated local SQLite/PostgreSQL storage, local model inference). However, production HIPAA compliance requires organizational business associate agreements (BAAs), encrypted storage volumes, and institutional access control policies.
- **Clinician Review:** All clinical notes generated by ScribeCare carry draft status and explicit warnings mandating review and authentication by a licensed medical provider before entry into the medical record.
