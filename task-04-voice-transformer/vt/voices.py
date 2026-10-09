from vt.config import VOICES, get_voice_id


def available_voices() -> list[dict[str, str]]:
    return [
        {
            "slug": voice["slug"],
            "name": voice["name"],
            "description": voice["description"],
            "configured": bool(get_voice_id_if_configured(voice["slug"])),
        }
        for voice in VOICES
    ]


def get_voice_id_if_configured(slug: str) -> str:
    try:
        return get_voice_id(slug)
    except ValueError:
        return ""
