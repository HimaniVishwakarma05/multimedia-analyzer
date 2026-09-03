import os
import sys

from mutagen import File


def format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def analyze_audio(audio_path):
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"File not found: {audio_path}")
    audio = File(audio_path)
    if audio is None or not hasattr(audio, "info"):
        raise ValueError("The file is not a supported or valid audio file.")
    info = audio.info
    duration = getattr(info, "length", 0)
    minutes, seconds = divmod(int(duration), 60)
    bitrate = getattr(info, "bitrate", None)
    return {
        "File Name": os.path.basename(audio_path),
        "File Size": format_size(os.path.getsize(audio_path)),
        "Container": os.path.splitext(audio_path)[1].upper().lstrip("."),
        "Duration": f"{minutes}m {seconds}s ({duration:.2f} seconds)",
        "Sample Rate": f"{getattr(info, 'sample_rate', 'N/A')} Hz",
        "Channels": getattr(info, "channels", "N/A"),
        "Bit Rate": f"{bitrate // 1000} kbps" if bitrate else "N/A",
    }


def print_report(report):
    print("\nAUDIO METADATA REPORT")
    print("=" * 24)
    for label, value in report.items():
        print(f"{label:<14}: {value}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audio_analyzer.py <audio-path>")
        sys.exit(1)
    try:
        print_report(analyze_audio(sys.argv[1]))
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        sys.exit(1)
