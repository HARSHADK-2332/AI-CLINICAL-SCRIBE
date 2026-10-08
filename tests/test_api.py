import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app
from backend.database import init_db
from backend.seed import seed_database
from backend.services.speech import speech_service, FFmpegNotFoundError

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    seed_database()


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "whisper_loaded" in data
    assert "ffmpeg_available" in data
    assert data["version"] == "1.0.0"


def test_patients_list():
    response = client.get("/api/patients")
    assert response.status_code == 200
    patients = response.json()
    assert len(patients) >= 3
    names = [p["name"] for p in patients]
    assert "Sarah Jenkins" in names


def test_transcribe_missing_ffmpeg():
    with patch.object(speech_service, "is_ffmpeg_available", return_value=False):
        response = client.post(
            "/api/transcribe",
            files={"audio": ("test.wav", b"dummy audio content", "audio/wav")}
        )
        assert response.status_code == 503
        assert "FFmpeg is missing" in response.json()["detail"]


def test_transcribe_success_mocked():
    mock_result = {
        "segments": [
            {"speaker": "Doctor", "start": 0.0, "end": 2.5, "text": "How can I help you today?"},
            {"speaker": "Patient", "start": 2.6, "end": 5.0, "text": "I have had a cough for 3 days."}
        ],
        "language": "en",
        "duration": 5.0
    }
    with patch.object(speech_service, "is_ffmpeg_available", return_value=True):
        with patch.object(speech_service, "transcribe", return_value=mock_result):
            response = client.post(
                "/api/transcribe",
                files={"audio": ("test.wav", b"dummy audio content", "audio/wav")}
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["segments"]) == 2
            assert data["segments"][0]["speaker"] == "Doctor"
            assert data["segments"][1]["speaker"] == "Patient"


def test_notes_generate_regression_fixture():
    """
    Section 5 regression test fixture:
    - Duration regex extracts '2 weeks'
    - 'No fever, no chest pain' are captured as negated findings, not positive symptoms.
    """
    payload = {
        "transcript": [
            {
                "speaker": "Doctor",
                "start": 0.0,
                "end": 2.8,
                "text": "How long have you been experiencing these symptoms?"
            },
            {
                "speaker": "Patient",
                "start": 3.0,
                "end": 7.5,
                "text": "About 2 weeks now. It started with a mild cough and then I began to feel short of breath when I move around."
            },
            {
                "speaker": "Doctor",
                "start": 7.8,
                "end": 10.2,
                "text": "Do you have any fever, chest pain or other symptoms?"
            },
            {
                "speaker": "Patient",
                "start": 10.5,
                "end": 15.0,
                "text": "No fever. Just the cough and shortness of breath. It's worse in the morning."
            }
        ],
        "language": "en"
    }

    response = client.post("/api/notes/generate", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Assert duration and chief complaint
    assert "2 weeks" in data["chief_complaint"].lower()
    assert "cough" in data["chief_complaint"].lower()
    assert "shortness of breath" in data["chief_complaint"].lower()

    # Assert negated findings capture fever and chest pain
    assert "fever" in data["negated_findings"]
    assert "chest pain" in data["negated_findings"]

    # Crucial clinical safety check: 'fever' must NOT be in the positive chief complaint
    assert "fever" not in data["chief_complaint"].lower()

    # Check status and structure
    assert data["status"] == "draft"
    assert len(data["plan"]) > 0
    assert data["capabilities"]["negation"] is True
    assert data["capabilities"]["allergies"] is False


def test_notes_crud_and_exports():
    # 1. Generate note
    gen_payload = {
        "transcript": [
            {"speaker": "Doctor", "start": 0.0, "end": 1.0, "text": "Hello."},
            {"speaker": "Patient", "start": 1.1, "end": 4.0, "text": "I have had severe headache for past 3 days."}
        ],
        "language": "en"
    }
    gen_res = client.post("/api/notes/generate", json=gen_payload)
    assert gen_res.status_code == 200
    note_id = gen_res.json()["id"]

    # 2. Get note by ID
    get_res = client.get(f"/api/notes/{note_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == note_id

    # 3. Update note (inline edit and approve)
    update_res = client.put(
        f"/api/notes/{note_id}",
        json={"status": "reviewed", "assessment": "Tension headache resolved with hydration."}
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "reviewed"
    assert "Tension headache" in update_res.json()["assessment"]

    # 4. Export TXT
    txt_res = client.post(f"/api/notes/{note_id}/export?format=txt")
    assert txt_res.status_code == 200
    assert "SCRIBECARE CLINICAL NOTE" in txt_res.text

    # 5. Export JSON
    json_res = client.post(f"/api/notes/{note_id}/export?format=json")
    assert json_res.status_code == 200
    export_json = json_res.json()
    assert export_json["id"] == note_id

    # 6. Export SOAP
    soap_res = client.post(f"/api/notes/{note_id}/export?format=soap")
    assert soap_res.status_code == 200
    assert "# SOAP CLINICAL NOTE" in soap_res.text

    # 7. Export FHIR (must return 501 with clear message)
    fhir_res = client.post(f"/api/notes/{note_id}/export?format=fhir")
    assert fhir_res.status_code == 501
    assert "FHIR R4 export is scheduled for Phase 4 roadmap" in fhir_res.json()["detail"]


def test_demo_requests():
    valid_payload = {
        "name": "Dr. Emily Taylor",
        "email": "emily.taylor@healthsystem.org",
        "organization": "Metro General Hospital",
        "role": "Chief Medical Information Officer",
        "message": "Interested in evaluating ambient scribe for our outpatient clinics."
    }
    res = client.post("/api/demo-requests", json=valid_payload)
    assert res.status_code == 201
    assert res.json()["status"] == "received"

    # Test invalid email format rejection
    invalid_payload = {
        "name": "Dr. Test",
        "email": "not-an-email",
        "organization": "Test Org",
        "role": "Clinician"
    }
    bad_res = client.post("/api/demo-requests", json=invalid_payload)
    assert bad_res.status_code == 422


def test_spa_static_serving():
    # Root returns index.html
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert "ScribeCare" in root_res.text
    assert "<div id=\"root\"></div>" in root_res.text

    # Route /app returns index.html for client routing
    app_res = client.get("/app")
    assert app_res.status_code == 200
    assert "<div id=\"root\"></div>" in app_res.text
