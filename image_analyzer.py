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
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    # Basic file details
    file_name = os.path.basename(image_path)
    file_size = format_size(os.path.getsize(image_path))

    try:
        with Image.open(image_path) as img:
            file_format = img.format
            width, height = img.size
            color_mode = img.mode
            
            # Resolution / DPI (defaulting to N/A if not embedded)
            dpi = img.info.get('dpi')
            resolution = f"{dpi[0]} x {dpi[1]} DPI" if dpi else "N/A"

            print("================================")
            print("IMAGE METADATA REPORT")
            print("================================")
            print(f"File Name       : {file_name}")
            print(f"File Size       : {file_size}")
            print(f"File Format     : {file_format}")
            print(f"Width           : {width} px")
            print(f"Height          : {height} px")
            print(f"Resolution      : {resolution}")
            print(f"Color Mode      : {color_mode}")
            print("\nEXIF Metadata")
            print("--------------------------------")

            # Extract EXIF tags
            exif_data = img.getexif()
            if not exif_data:
                print("No EXIF metadata found.")
            else:
                camera_make = "N/A"
                camera_model = "N/A"
                date_taken = "N/A"
                orientation = "N/A"

                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == "Make":
                        camera_make = value
                    elif tag_name == "Model":
                        camera_model = value
                    elif tag_name == "DateTime":
                        date_taken = value
                    elif tag_name == "Orientation":
                        orientation = value

                camera = f"{camera_make} {camera_model}".strip()
                if camera == "N/A N/A" or not camera:
                    camera = "N/A"

                print(f"Camera          : {camera}")
                print(f"Date Taken      : {date_taken}")
                print(f"Orientation     : {orientation}")

    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = input("Enter image path: ").strip().strip('"').strip("'")
    
analyze_image(target_path)