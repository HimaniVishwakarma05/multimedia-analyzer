import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS

def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def analyze_image(image_path):
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    with Image.open(image_path) as img:
        exif_data = img.getexif()
        exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
        camera = " ".join(str(value) for value in (exif.get("Make"), exif.get("Model")) if value) or "N/A"
        dpi = img.info.get("dpi")
        resolution = f"{dpi[0]} x {dpi[1]} DPI" if dpi and len(dpi) >= 2 else "N/A"

        return {
            "File Name": os.path.basename(image_path),
            "File Size": format_size(os.path.getsize(image_path)),
            "File Format": img.format or "Unknown",
            "Width": f"{img.width} px",
            "Height": f"{img.height} px",
            "Resolution": resolution,
            "Color Mode": img.mode,
            "Camera": camera,
            "Date Taken": exif.get("DateTime", "N/A"),
            "Orientation": exif.get("Orientation", "N/A"),
        }


def print_report(report):
    print("\nIMAGE METADATA REPORT")
    print("=" * 24)
    for label, value in report.items():
        print(f"{label:<14}: {value}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = input("Enter image path: ").strip().strip('"').strip("'")
    try:
        print_report(analyze_image(target_path))
    except (FileNotFoundError, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)