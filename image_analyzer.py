from pathlib import Path
import sys

from PIL import ExifTags
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
    path = Path(image_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    with Image.open(path) as img:
        exif_data = img.getexif()
        exif = {TAGS.get(tag_id, tag_id): value for tag_id, value in exif_data.items()}
        exif_sub_ifd = exif_data.get_ifd(ExifTags.IFD.Exif)
        exif.update(
            (TAGS.get(tag_id, tag_id), value)
            for tag_id, value in exif_sub_ifd.items()
        )
        camera = " ".join(str(value) for value in (exif.get("Make"), exif.get("Model")) if value) or "N/A"
        dpi = img.info.get("dpi")
        resolution = f"{dpi[0]} x {dpi[1]} DPI" if dpi and len(dpi) >= 2 else "N/A"
        date_taken = next(
            (
                exif[tag]
                for tag in ("DateTimeOriginal", "DateTimeDigitized", "DateTime")
                if exif.get(tag)
            ),
            "N/A",
        )

        return {
            "File Name": path.name,
            "File Size": format_size(path.stat().st_size),
            "File Format": img.format or "Unknown",
            "Width": f"{img.width} px",
            "Height": f"{img.height} px",
            "Resolution": resolution,
            "Color Mode": img.mode,
            "Camera": camera,
            "Date Taken": date_taken,
            "Orientation": exif.get("Orientation", "N/A"),
        }


def print_report(report):
    print("\nIMAGE METADATA REPORT") 
    print("="* 24)
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