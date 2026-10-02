

def main():
    parser = argparse.ArgumentParser(description="Analyze image, audio, and video metadata.")
    parser.add_argument("file", help="Path to a supported media file")
    parser.add_argument("--play", action="store_true", help="Play a video preview after reading its metadata")
    args = parser.parse_args()
    extension = args.file.lower().rsplit(".", 1)[-1] if "." in args.file else ""
    if extension not in {"jpg", "jpeg", "png", "tiff", "webp", "bmp", "mp3", "wav", "flac", "m4a", "ogg", "mp4", "avi", "mov", "mkv", "webm"}:
        parser.error(f"Unsupported media format: .{extension or 'unknown'}")

    try:
        if extension in {"jpg", "jpeg", "png", "tiff", "webp", "bmp"}:
            from image_analyzer import analyze_image, print_report

            print_report(analyze_image(args.file))
        elif extension in {"mp3", "wav", "flac", "m4a", "ogg"}:
            from audio_analyzer import analyze_audio, print_report

        print_report(analyze_audio(args.file))
    elif extension in {"mp4", "avi", "mov", "mkv", "webm"}:
        from video_analyzer import analyze_video, play_video, print_report

            print_report(analyze_video(args.file))
            if args.play:
                play_video(args.file)
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()