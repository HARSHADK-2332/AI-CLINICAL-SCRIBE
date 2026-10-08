import os
import shutil
from typing import List, Dict, Any, Optional

try:
    import whisper
except ImportError:
    whisper = None


def ensure_ffmpeg() -> bool:
    """Ensure ffmpeg binary is found in PATH, auto-configuring from imageio_ffmpeg if available."""
    if shutil.which("ffmpeg") is not None:
        return True
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        d = os.path.dirname(exe)
        target = os.path.join(d, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if not os.path.exists(target):
            shutil.copyfile(exe, target)
        if d not in os.environ.get("PATH", ""):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
        return shutil.which("ffmpeg") is not None
    except Exception:
        return False


class FFmpegNotFoundError(Exception):
    """Raised when FFmpeg is not found in the system PATH."""
    pass


class SpeechToTextService:
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._model = None
        ensure_ffmpeg()

    @staticmethod
    def is_ffmpeg_available() -> bool:
        """Check whether ffmpeg executable is discovered on system PATH."""
        return ensure_ffmpeg()

    def is_model_loaded(self) -> bool:
        """Check whether Whisper model weights are currently in memory."""
        return self._model is not None

    def get_model(self):
        """Lazy loader for Whisper model weights."""
        if self._model is None:
            if whisper is None:
                raise RuntimeError("openai-whisper library is not installed in the Python environment.")
            self._model = whisper.load_model(self.model_name)
        return self._model

    def transcribe(
        self,
        audio_file_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes given audio file path.
        Raises FFmpegNotFoundError if FFmpeg is missing.
        """
        if not self.is_ffmpeg_available():
            raise FFmpegNotFoundError(
                "FFmpeg is not installed or not found on the system PATH. "
                "Whisper requires FFmpeg to decode audio. "
                "To resolve: "
                "1. Windows: run 'winget install Gyan.FFmpeg' or download from gyan.dev and add bin to PATH. "
                "2. macOS: run 'brew install ffmpeg'. "
                "3. Linux: run 'sudo apt install ffmpeg'. "
                "Alternatively, test the UI using Mock Mode by setting VITE_USE_MOCK=true in the frontend."
            )

        model = self.get_model()
        transcribe_args: Dict[str, Any] = {
            "fp16": False  # Prevent CPU warning
        }
        if language and language in ["en", "hi", "te"]:
            transcribe_args["language"] = language

        result = model.transcribe(audio_file_path, **transcribe_args)
        raw_segments = result.get("segments", [])

        # Speaker tag heuristics (Doctor asks, Patient answers) or default
        segments: List[Dict[str, Any]] = []
        for idx, seg in enumerate(raw_segments):
            text = seg.get("text", "").strip()
            # Alternating heuristic if multiple segments
            speaker = "Doctor" if (idx % 2 == 0) else "Patient"
            segments.append({
                "speaker": speaker,
                "start": round(seg.get("start", 0.0), 2),
                "end": round(seg.get("end", 0.0), 2),
                "text": text
            })

        if not segments and result.get("text"):
            segments.append({
                "speaker": "Unknown",
                "start": 0.0,
                "end": 0.0,
                "text": result.get("text", "").strip()
            })

        return {
            "segments": segments,
            "language": result.get("language", language or "en"),
            "duration": raw_segments[-1]["end"] if raw_segments else 0.0
        }


# Singleton instance
speech_service = SpeechToTextService()
