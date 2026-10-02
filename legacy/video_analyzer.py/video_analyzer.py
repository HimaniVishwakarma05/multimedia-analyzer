import argparse
from pathlib import Path

import cv2


def format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def _codec_name(capture):
    fourcc = int(capture.get(cv2.CAP_PROP_FOURCC))
    if not fourcc:
        return "Unknown"
    return "".join(chr((fourcc >> (8 * index)) & 0xFF) for index in range(4)).strip() or "Unknown"


def analyze_video(video_path):
    path = Path(video_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError("Could not open the video file.")
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        hours, remainder = divmod(int(duration), 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_text = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
        return {
            "File Name": path.name,
            "File Size": format_size(path.stat().st_size),
            "Container": path.suffix.upper().lstrip("."),
            "Duration": f"{duration_text} ({duration:.2f} seconds)",
            "Resolution": f"{int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))} x {int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
            "Frame Rate": f"{fps:.2f} FPS",
            "Frame Count": frame_count,
            "Codec": _codec_name(capture),
        }
    finally:
        capture.release()


def play_video(video_path, max_width=1280, max_height=720):
    path = Path(video_path).expanduser()
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"Could not open the video file: {path}")

    window_name = f"Video Preview - {path.name} (Q or Esc to quit)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, max_width, max_height)
    fps = capture.get(cv2.CAP_PROP_FPS)
    delay = max(1, round(1000 / fps)) if fps > 0 else 33

    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            height, width = frame.shape[:2]
            scale = min(max_width / width, max_height / height, 1)
            if scale < 1:
                frame = cv2.resize(frame, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)
            cv2.imshow(window_name, frame)
            if cv2.waitKey(delay) & 0xFF in (ord("q"), 27):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()


def print_report(report):
    print("\nVIDEO METADATA REPORT")
    print("=" * 24)
    for label, value in report.items():
        print(f"{label:<14}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read video metadata and optionally play a preview.")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("--play", action="store_true", help="Open an HD-sized video preview window")
    args = parser.parse_args()

    try:
        print_report(analyze_video(args.video))
        if args.play:
            play_video(args.video)
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    
