import requests
from urllib.parse import quote

from vt.config import (
    ELEVENLABS_API_BASE,
    ELEVENLABS_MODEL_ID,
    ELEVENLABS_OUTPUT_FORMAT,
    get_voice_id,
)


class ProviderError(RuntimeError):
    """Raised for safe-to-display errors returned by the speech provider."""


def transform_audio(
    audio_bytes: bytes,
    filename: str,
    mime_type: str,
    voice_slug: str,
    api_key: str,
) -> bytes:
    voice_id = get_voice_id(voice_slug)
    url = (
        f"{ELEVENLABS_API_BASE}/speech-to-speech/{quote(voice_id, safe='')}"
        f"?output_format={ELEVENLABS_OUTPUT_FORMAT}"
    )
    try:
        response = requests.post(
            url,
            headers={"xi-api-key": api_key, "Accept": "audio/mpeg"},
            files={"audio": (filename, audio_bytes, mime_type)},
            data={"model_id": ELEVENLABS_MODEL_ID},
            timeout=(10, 120),
        )
    except requests.RequestException as error:
        raise ProviderError("Could not connect to the ElevenLabs voice service.") from error

    if response.status_code in (401, 403):
        raise ProviderError("ElevenLabs rejected the API key or this request is not authorized.")
    if response.status_code == 429:
        raise ProviderError("ElevenLabs rate limit or account quota has been reached.")
    if response.status_code >= 400:
        raise ProviderError(
            f"ElevenLabs could not transform the audio (HTTP {response.status_code})."
        )
    if not response.content:
        raise ProviderError("ElevenLabs returned an empty audio result.")
    return response.content
