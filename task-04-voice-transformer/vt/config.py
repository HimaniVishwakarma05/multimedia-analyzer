import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

MAX_AUDIO_BYTES = 15 * 1024 * 1024
MAX_AUDIO_SECONDS = 30
MAX_MULTIPART_BYTES = MAX_AUDIO_BYTES + 1024 * 1024
ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"
ELEVENLABS_MODEL_ID = "eleven_multilingual_sts_v2"
ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128"
ALLOWED_AUDIO_MIME_TYPES = {
    ".mp3": ("audio/mpeg", "audio/mp3"),
    ".wav": ("audio/wav", "audio/x-wav", "audio/wave"),
    ".m4a": ("audio/mp4", "audio/x-m4a"),
    ".ogg": ("audio/ogg", "audio/x-ogg", "application/ogg"),
    ".oga": ("audio/ogg", "audio/x-ogg", "application/ogg"),
    ".flac": ("audio/flac", "audio/x-flac"),
    ".webm": ("audio/webm",),
}

VOICES = (
    {
        "slug": "warm-narrator",
        "name": "Warm Narrator",
        "description": "A composed, welcoming voice for stories and presentations.",
        "env_name": "ELEVENLABS_VOICE_WARM_ID",
    },
    {
        "slug": "deep-studio",
        "name": "Deep Studio",
        "description": "A resonant studio tone with a confident, measured delivery.",
        "env_name": "ELEVENLABS_VOICE_DEEP_ID",
    },
    {
        "slug": "bright-conversational",
        "name": "Bright Conversational",
        "description": "An upbeat, natural-sounding voice for everyday conversation.",
        "env_name": "ELEVENLABS_VOICE_BRIGHT_ID",
    },
)


class ConfigurationError(ValueError):
    """Raised when a required provider credential or target voice is unavailable."""


def get_api_key() -> str:
    key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not key or "your_" in key.lower() or "replace_" in key.lower():
        raise ConfigurationError(
            "Set a valid ELEVENLABS_API_KEY in task-04-voice-transformer/.env."
        )
    return key


def get_voice_id(slug: str) -> str:
    voice = next((item for item in VOICES if item["slug"] == slug), None)
    if voice is None:
        raise ConfigurationError("Choose one of the available target voices.")

    voice_id = os.getenv(voice["env_name"], "").strip()
    if not voice_id or "your_" in voice_id.lower() or "replace_" in voice_id.lower():
        raise ConfigurationError(
            f"Set {voice['env_name']} in task-04-voice-transformer/.env."
        )
    return voice_id
