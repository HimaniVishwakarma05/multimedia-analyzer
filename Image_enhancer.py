
"""
Task 05: Image Processing & Enhancement
Multimedia Systems Laboratory
Author: Himani Vishwakarma
"""

import sys
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps

TASK_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE = TASK_DIR.parent / "datasets" / "images" / "flower.jpg"
OUTPUT_DIR = TASK_DIR / "outputs"


def basic_operations(image: Image.Image) -> dict:
    """Grayscale, resize, threshold, blur, edge detection and rotation."""
    gray = ImageOps.grayscale(image)
    half_size = (max(1, image.width // 2), max(1, image.height // 2))

    return {
        "grayscale": gray,
        "resize_half": image.resize(half_size, Image.LANCZOS),
        "threshold": gray.point(lambda value: 255 if value >= 128 else 0),
        "gaussian_blur": image.filter(ImageFilter.GaussianBlur(radius=2)),
        "canny_edges": Image.fromarray(cv2.Canny(np.array(gray), 100, 200)),
        "rotate_clockwise": image.rotate(-90, expand=True),
    }


def histogram_equalization(image: Image.Image) -> Image.Image:
    """Equalize only the brightness (Y) channel so colours are not changed."""
    ycrcb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return Image.fromarray(cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB))


def gamma_correction(image: Image.Image, gamma: float) -> Image.Image:
    """Apply gamma correction. gamma < 1 brightens, gamma > 1 darkens."""
    table = [round(255 * (value / 255) ** gamma) for value in range(256)]
    return image.point(table * 3)


def enhancement_operations(image: Image.Image, gamma: float) -> dict:
    """Contrast, brightness, sharpness and noise enhancements."""
    return {
        "histogram_equalization": histogram_equalization(image),
        "gamma_correction": gamma_correction(image, gamma),
        "sharpen": image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)),
        "median_denoise": image.filter(ImageFilter.MedianFilter(size=3)),
    }


def image_stats(image: Image.Image) -> tuple:
    """Return (brightness, contrast, sharpness) measured on the grayscale image."""
    gray = np.array(ImageOps.grayscale(image), dtype=np.float64)
    brightness = gray.mean()
    contrast = gray.std()
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    return brightness, contrast, sharpness


def before_after(original: Image.Image, enhanced: Image.Image) -> Image.Image:
    """Place the original and enhanced images side by side."""
    canvas = Image.new("RGB", (original.width * 2, original.height), "white")
    canvas.paste(original, (0, 0))
    canvas.paste(enhanced, (original.width, 0))
    return canvas


def process_image(image_path: str, gamma: float) -> bool:
    """Run all operations, save the results and print the comparison table."""
    path = Path(image_path).resolve()

    if not path.exists():
        print(f"[Error] File not found: {path}")
        return False

    try:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
    except Exception as error:
        print(f"[Error] Could not open image: {error}")
        return False

    output_dir = OUTPUT_DIR / path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    basic = basic_operations(image)
    enhanced = enhancement_operations(image, gamma)

    print("=" * 60)
    print("      TASK 05: IMAGE PROCESSING & ENHANCEMENT REPORT      ")
    print("=" * 60)
    print(f"Input Image    : {path.name}")
    print(f"Dimensions     : {image.width} x {image.height} px")
    print(f"Output Folder  : {output_dir}")

    print("\n[Basic Processing]")
    print("-" * 45)
    for name, result in {**basic, **enhanced}.items():
        if name == "histogram_equalization":
            print("\n[Enhancement]")
            print("-" * 45)
        result.save(output_dir / f"{name}.png")
        print(f"Saved {name + '.png':<28}: {result.width} x {result.height}")

    before_after(image, enhanced["histogram_equalization"]).save(output_dir / "before_after.png")
    print(f"Saved {'before_after.png':<28}: original | equalized")

    print("\n[Enhancement Comparison]")
    print("-" * 60)
    print(f"{'Image':<24}{'Brightness':>12}{'Contrast':>12}{'Sharpness':>12}")
    for name, result in {"original": image, **enhanced}.items():
        brightness, contrast, sharpness = image_stats(result)
        print(f"{name:<24}{brightness:>12.2f}{contrast:>12.2f}{sharpness:>12.1f}")

    print("\nBrightness = mean gray level, Contrast = standard deviation,")
    print("Sharpness = variance of the Laplacian (higher means more edges).")
    return True


def main():
    parser = argparse.ArgumentParser(description="Task 05: Image Processing & Enhancement")
    parser.add_argument("-f", "--file", default=str(DEFAULT_IMAGE), help="Path to the input image")
    parser.add_argument("-g", "--gamma", type=float, default=0.7, help="Gamma value (default 0.7)")
    args = parser.parse_args()

    if args.gamma <= 0:
        print("[Error] Gamma must be greater than 0.")
        sys.exit(1)

    if not process_image(args.file, args.gamma):
        sys.exit(1)


if __name__ == "__main__":
    main()
