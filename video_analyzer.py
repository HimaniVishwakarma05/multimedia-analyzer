import os
import sys

import cv2


def format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def analyze_video(video_path):
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"File not found: {video_path}")
    capture = cv2.VideoCapture(video_path)
    try:
        if not capture.isOpened():
            raise ValueError("Could not open the video file.")
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        minutes, seconds = divmod(int(duration), 60)
        return {
            "File Name": os.path.basename(video_path),
            "File Size": format_size(os.path.getsize(video_path)),
            "Container": os.path.splitext(video_path)[1].upper().lstrip("."),
            "Duration": f"{minutes}m {seconds}s ({duration:.2f} seconds)",
            "Resolution": f"{int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))} x {int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
            "Frame Rate": f"{fps:.2f} FPS",
            "Frame Count": frame_count,
            "Codec": "Detected by OpenCV",
        }
    finally:
        capture.release()


def print_report(report):
    print("\nVIDEO METADATA REPORT")
    print("=" * 24)
    for label, value in report.items():
        print(f"{label:<14}: {value}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python video_analyzer.py <video-path>")
        sys.exit(1)
    try:
        print_report(analyze_video(sys.argv[1]))
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        sys.exit(1)