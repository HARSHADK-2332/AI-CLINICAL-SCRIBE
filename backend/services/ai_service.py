# =========================================================
# AI CLINICAL SCRIBE
# AI Service
# Connects FastAPI backend with AI pipeline
# =========================================================

from pathlib import Path

from ai.pipeline import process_audio


# ---------------------------------------------------------
# RUN AUDIO AI PIPELINE
# ---------------------------------------------------------

def run_audio_pipeline(
    audio_path: str,
    report_language="English"
):
    """
    Run the complete AI Clinical Scribe pipeline.

    Parameters
    ----------
    audio_path:
        Path of the uploaded consultation audio.

    report_language:
        Language selected by the doctor for the
        generated clinical report.

        Supported:
            English
            Hindi
            Telugu

    Returns
    -------
    dict
        Complete AI pipeline result.
    """

    # -----------------------------------------------------
    # Validate audio file
    # -----------------------------------------------------

    path = Path(audio_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    # -----------------------------------------------------
    # Run AI pipeline
    #
    # IMPORTANT:
    # Pass the doctor's selected report language
    # to the pipeline.
    # -----------------------------------------------------

    result = process_audio(
        str(path),
        report_language=report_language
    )

    return result