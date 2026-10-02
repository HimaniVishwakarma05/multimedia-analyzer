import argparse
import json
import mimetypes
import os
import sys

try:
    import requests
except ImportError as exc:  # pragma: no cover - handled at runtime for CLI usability
    raise SystemExit(
        "Missing dependency: install 'requests' with 'python -m pip install requests' "
        "before using voice cloning."
    ) from exc

ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"


def _resolve_api_key(api_key=None):
    key = api_key or os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise ValueError(
            "An ElevenLabs API key is required. Pass --api-key or set ELEVENLABS_API_KEY."
        )
    return key


def _detect_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("audio/"):
        return mime_type
    extension = os.path.splitext(file_path)[1].lower()
    if extension in {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".webm"}:
        return {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".flac": "audio/flac",
            ".m4a": "audio/mp4",
            ".ogg": "audio/ogg",
            ".webm": "audio/webm",
        }[extension]
    return "application/octet-stream"


def clone_voice(audio_path, voice_name, description=None, api_key=None, base_url=ELEVENLABS_API_BASE):
    """Clone a voice from a sample audio file using ElevenLabs."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    key = _resolve_api_key(api_key)
    headers = {"xi-api-key": key}
    with open(audio_path, "rb") as handle:
        file_bytes = handle.read()

    files = {"files": (os.path.basename(audio_path), file_bytes, _detect_mime_type(audio_path))}
    payload = {"name": voice_name}
    if description:
        payload["description"] = description

    response = requests.post(
        f"{base_url.rstrip('/')}/voices/add",
        headers=headers,
        files=files,
        data=payload,
        timeout=120,
    )
    if response.status_code >= 400:
        detail = response.text.strip() or response.reason
        raise RuntimeError(f"Voice cloning failed ({response.status_code}): {detail}")

    data = response.json()
    if isinstance(data, dict) and data.get("voice"):
        return data["voice"]
    if isinstance(data, dict) and data.get("voice_id"):
        return data
    return data


def synthesize_text(text, voice_id, api_key=None, output_path=None, model_id="eleven_multilingual_v2", base_url=ELEVENLABS_API_BASE):
    """Generate speech from text using a previously created voice ID."""
    if not text or not text.strip():
        raise ValueError("Text for synthesis cannot be empty.")

    key = _resolve_api_key(api_key)
    headers = {"xi-api-key": key, "Content-Type": "application/json"}
    body = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.8,
        },
    }

    response = requests.post(
        f"{base_url.rstrip('/')}/text-to-speech/{voice_id}",
        headers=headers,
        json=body,
        timeout=120,
    )
    if response.status_code >= 400:
        detail = response.text.strip() or response.reason
        raise RuntimeError(f"Text-to-speech failed ({response.status_code}): {detail}")

    if output_path:
        destination = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
        with open(destination, "wb") as handle:
            handle.write(response.content)
        return {"voice_id": voice_id, "output_path": destination, "bytes_written": len(response.content)}

    return response.content


def clone_and_synthesize(audio_path, voice_name, text, description=None, api_key=None, output_path=None, model_id="eleven_multilingual_v2"):
    """Convenience wrapper: clone a voice from a sample and generate speech from text."""
    voice_info = clone_voice(audio_path, voice_name, description=description, api_key=api_key)
    voice_id = voice_info.get("voice_id") or voice_info.get("id")
    if not voice_id:
        raise ValueError(f"No voice ID returned from ElevenLabs; response was: {voice_info}")
    result = synthesize_text(
        text,
        voice_id=voice_id,
        api_key=api_key,
        output_path=output_path,
        model_id=model_id,
    )
    return {"voice": voice_info, "voice_id": voice_id, "result": result}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Clone a voice from an audio sample and/or generate speech from text using ElevenLabs."
    )
    parser.add_argument("--source", help="Path to a source audio sample used to clone a voice.")
    parser.add_argument("--voice-name", help="Name for the cloned voice.")
    parser.add_argument("--description", help="Optional description for the cloned voice.")
    parser.add_argument("--text", help="Text to synthesize after cloning.")
    parser.add_argument("--output", help="Optional file path to save generated audio.")
    parser.add_argument("--voice-id", help="Existing ElevenLabs voice ID to use for synthesis.")
    parser.add_argument("--model-id", default="eleven_multilingual_v2", help="ElevenLabs model ID to use.")
    parser.add_argument("--api-key", help="ElevenLabs API key. Overrides ELEVENLABS_API_KEY.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.voice_id and args.text:
        result = synthesize_text(
            args.text,
            voice_id=args.voice_id,
            api_key=args.api_key,
            output_path=args.output,
            model_id=args.model_id,
        )
        if args.output:
            print(json.dumps({"status": "success", "output_path": os.path.abspath(args.output)}, indent=2))
            return 0
        print(f"Generated speech in memory for voice {args.voice_id}")
        return 0

    if args.source and args.voice_name and args.text:
        response = clone_and_synthesize(
            audio_path=args.source,
            voice_name=args.voice_name,
            text=args.text,
            description=args.description,
            api_key=args.api_key,
            output_path=args.output,
            model_id=args.model_id,
        )
        print(json.dumps(response, indent=2, default=str))
        return 0

    if args.source and args.voice_name:
        voice = clone_voice(
            args.source,
            args.voice_name,
            description=args.description,
            api_key=args.api_key,
        )
        print(json.dumps(voice, indent=2, default=str))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
