from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db
from backend.seed import seed_database

from backend.routes import (
    health,
    transcribe,
    notes,
    patients,
    demo,
    audio,
)


# ============================================================
# HIPAA NOTICE
# ============================================================
#
# ScribeCare architecture is designed for HIPAA-readiness.
#
# Organizational compliance, BAAs, encryption-at-rest,
# access control, RBAC policies, audit logging, and
# deployment security must be configured in production.
#
# Raw transcripts and patient PHI should not be logged
# to stdout in production mode.
#
# ============================================================


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Initialize database
    init_db()

    # Insert initial/demo data if required
    seed_database()

    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ScribeCare API",
    description=(
        "Clinical AI Scribe API that converts "
        "clinician-patient conversations into "
        "structured clinical notes using AI."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

# Health check
app.include_router(
    health.router
)


# Existing transcription routes
app.include_router(
    transcribe.router
)


# Clinical notes / scribe routes
app.include_router(
    notes.router
)


# Patient routes
app.include_router(
    patients.router
)


# Demo routes
app.include_router(
    demo.router
)


# AI Audio Pipeline
#
# This connects:
#
# Audio
#   ↓
# Whisper
#   ↓
# Transcript
#   ↓
# Transcript Processor
#   ↓
# Clinical Extractor
#   ↓
# Clinical Note Generator
#
app.include_router(
    audio.router
)


# ============================================================
# FRONTEND STATIC FILES
# ============================================================

# Expected structure:
#
# AI-Clinical-Scribe/
# │
# ├── backend/
# │   └── main.py
# │
# └── frontend/
#     └── dist/
#
# If frontend/dist exists, FastAPI can serve the
# production frontend.


FRONTEND_DIST = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "dist"
)


if FRONTEND_DIST.exists():

    # Serve frontend assets
    assets_directory = FRONTEND_DIST / "assets"

    if assets_directory.exists():

        app.mount(
            "/assets",
            StaticFiles(
                directory=assets_directory
            ),
            name="assets",
        )


    # ========================================================
    # SPA FALLBACK
    # ========================================================

    @app.get("/{full_path:path}")
    async def serve_spa(
        request: Request,
        full_path: str,
    ):
        """
        Serve frontend files for production SPA.

        API and documentation routes are not intercepted.
        """

        # Never intercept API routes
        if full_path.startswith("api/"):
            return None

        # Never intercept FastAPI documentation
        if full_path.startswith("docs"):
            return None

        if full_path.startswith("redoc"):
            return None

        if full_path == "openapi.json":
            return None

        # Check whether requested frontend file exists
        candidate_file = (
            FRONTEND_DIST / full_path
        )

        if candidate_file.is_file():
            return FileResponse(
                candidate_file
            )

        # Otherwise return React/Vite SPA
        # entry point
        index_file = (
            FRONTEND_DIST / "index.html"
        )

        if index_file.exists():
            return FileResponse(
                index_file
            )

        return {
            "detail": "Frontend not built."
        }


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    """
    Basic API information.
    """

    return {
        "name": "ScribeCare API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "ai_pipeline": {
            "speech_to_text": "Whisper",
            "transcript_processing": True,
            "clinical_extraction": True,
            "clinical_note_generation": True,
            "multilingual": [
                "English",
                "Hindi",
                "Telugu",
            ],
        },
    }