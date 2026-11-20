"""Optional local voice adapters.

The worker stays usable without these packages. Install the chosen local
backend separately before calling these functions.
"""

from __future__ import annotations

from pathlib import Path


def transcribe(audio_path: str | Path, model_name: str = "base") -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError("voice input requires optional dependency: faster-whisper") from error
    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path))
    return " ".join(segment.text.strip() for segment in segments).strip()


def speak(text: str, output_path: str | Path) -> Path:
    try:
        import kokoro_onnx  # type: ignore
    except ImportError as error:
        raise RuntimeError("voice output requires optional dependency: kokoro-onnx and a model file") from error
    raise RuntimeError("kokoro output adapter needs a configured model path; configure it before use")
