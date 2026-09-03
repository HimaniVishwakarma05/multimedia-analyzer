import argparse


def main():
    parser = argparse.ArgumentParser(description="Analyze image, audio, and video metadata.")
    parser.add_argument("file", help="Path to a supported media file")
    args = parser.parse_args()
    extension = args.file.lower().rsplit(".", 1)[-1] if "." in args.file else ""
    if extension in {"jpg", "jpeg", "png", "tiff", "webp", "bmp"}:
        from image_analyzer import analyze_image

        analyze_image(args.file)
    elif extension in {"mp3", "wav", "flac", "m4a", "ogg"}:
        from audio_analyzer import analyze_audio, print_report

        print_report(analyze_audio(args.file))
    elif extension in {"mp4", "avi", "mov", "mkv", "webm"}:
        from video_analyzer import analyze_video, print_report

        print_report(analyze_video(args.file))
    else:
        parser.error(f"Unsupported media format: .{extension or 'unknown'}")


if __name__ == "__main__":
    main()