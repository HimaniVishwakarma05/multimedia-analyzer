from io import BytesIO
from pathlib import Path

from mutagen import File as MutagenFile
from mutagen import MutagenError

from vt.config import ALLOWED_AUDIO_MIME_TYPES, MAX_AUDIO_BYTES, MAX_AUDIO_SECONDS


class AudioValidationError(ValueError):
    """Raised when an uploaded audio file is unsupported or cannot be parsed."""


def validate_audio(filename: str, audio_bytes: bytes, declared_mime: str = "") -> float:
    if not audio_bytes:
        raise AudioValidationError("The audio file is empty.")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise AudioValidationError("Audio must be 15 MB or smaller.")

    extension = Path(filename).suffix.lower()
    allowed_mime_types = ALLOWED_AUDIO_MIME_TYPES.get(extension)
    if allowed_mime_types is None:
        raise AudioValidationError("Use an MP3, WAV, M4A, OGG/OGA, FLAC, or WebM audio file.")

    declared_mime = declared_mime.lower().split(";", 1)[0].strip()
    if (
        declared_mime
        and declared_mime != "application/octet-stream"
        and declared_mime not in allowed_mime_types
    ):
        raise AudioValidationError("The file type does not match its audio extension.")

    try:
        audio = MutagenFile(BytesIO(audio_bytes))
        info = getattr(audio, "info", None) if audio is not None else None
        duration = float(info.length) if info is not None else 0.0
    except (AttributeError, MutagenError, OSError, TypeError, ValueError):
        duration = 0.0

    if duration <= 0:
        raise AudioValidationError("The audio file is corrupt or unreadable.")
    if duration > MAX_AUDIO_SECONDS:
        raise AudioValidationError("Audio must be 30 seconds or shorter.")
    return duration
