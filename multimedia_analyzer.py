import argparse
from pathlib import Path


IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "tiff", "webp", "bmp"}
AUDIO_EXTENSIONS = {"mp3", "wav", "flac", "m4a", "ogg"}
VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}


def main():
    parser = argparse.ArgumentParser(description="Analyze image, audio, and video metadata.")
    parser.add_argument("file", help="Path to a supported media file")
    parser.add_argument("--play", action="store_true", help="Play a video preview after reading its metadata")
    args = parser.parse_args()

    extension = Path(args.file).suffix.lower().lstrip(".")
    if extension not in IMAGE_EXTENSIONS | AUDIO_EXTENSIONS | VIDEO_EXTENSIONS:
        parser.error(f"Unsupported media format: .{extension or 'unknown'}")
    if args.play and extension not in VIDEO_EXTENSIONS:
        parser.error("--play can only be used with video files")

    try:
        if extension in IMAGE_EXTENSIONS:
            from image_analyzer import analyze_image, print_report

            print_report(analyze_image(args.file))
        elif extension in AUDIO_EXTENSIONS:
            from audio_analyzer import analyze_audio, print_report

            print_report(analyze_audio(args.file))
        else:
            from video_analyzer import analyze_video, play_video, print_report

            print_report(analyze_video(args.file))
            if args.play:
                play_video(args.file)
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
