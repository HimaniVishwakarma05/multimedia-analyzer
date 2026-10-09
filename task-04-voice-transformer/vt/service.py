from mimetypes import guess_type
from pathlib import Path

from vt.audio_validation import validate_audio
from vt.config import get_api_key
from vt.providers import transform_audio
from vt.voices import get_voice_id_if_configured


def transform_upload(filename: str, audio_bytes: bytes, mime_type: str, voice_slug: str) -> bytes:
    validate_audio(filename, audio_bytes, mime_type)
    if not get_voice_id_if_configured(voice_slug):
        raise ValueError("The selected target voice is not configured in the .env file.")

    api_key = get_api_key()
    inferred_mime = mime_type or guess_type(filename)[0] or "application/octet-stream"
    return transform_audio(audio_bytes, Path(filename).name, inferred_mime, voice_slug, api_key)
