import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from vt.config import MAX_AUDIO_BYTES, PROJECT_ROOT
from vt.providers import ProviderError
from vt.service import transform_upload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transform an authorized recording into a configured synthetic voice."
    )
    parser.add_argument("--serve", action="store_true", help="Start the local browser interface.")
    parser.add_argument("--host", default="127.0.0.1", help="Web server host (default: localhost).")
    parser.add_argument("--port", type=int, default=5000, help="Web server port (default: 5000).")
    parser.add_argument("--input", help="Path to an audio recording to transform.")
    parser.add_argument(
        "--voice",
        choices=("warm-narrator", "deep-studio", "bright-conversational"),
        help="Configured target voice slug.",
    )
    parser.add_argument("--output", help="Path where the transformed MP3 will be saved.")
    parser.add_argument(
        "--confirm-permission",
        action="store_true",
        help="Confirm that you have permission to use the source recording.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.serve:
        if args.input or args.voice or args.output or args.confirm_permission:
            parser.error("--serve cannot be combined with CLI conversion options.")
        from vt.server import create_app

        create_app().run(host=args.host, port=args.port, debug=False)
        return 0

    if not (args.input and args.voice and args.output):
        parser.error("CLI conversion requires --input, --voice, and --output.")
    if not args.confirm_permission:
        parser.error("CLI conversion requires --confirm-permission.")

    source = Path(args.input).expanduser()
    if not source.is_file():
        parser.error(f"Input audio file does not exist: {source}")
    if source.stat().st_size > MAX_AUDIO_BYTES:
        parser.error("Audio must be 15 MB or smaller.")

    try:
        output = Path(args.output).expanduser()
        result = transform_upload(
            source.name,
            source.read_bytes(),
            "",
            args.voice,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(result)
    except (OSError, ValueError, ProviderError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Transformed audio saved to {output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
