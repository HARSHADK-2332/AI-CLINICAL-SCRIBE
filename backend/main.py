
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.audio import router as audio_router
from routes.notes import router as notes_router

app = FastAPI(
    title="AI Clinical Scribe API",
    description="Backend API for AI-assisted clinical documentation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_router)
app.include_router(notes_router)


@app.get("/")
def root():
    return {"message": "AI Clinical Scribe API is running"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}