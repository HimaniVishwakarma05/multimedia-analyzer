#!/usr/bin/env python3
"""Task Pipe — fix blurry/dark/rotated photos, then OCR in 10+ languages.

Usage (shared venv, see README):
    uv sync                                  # one-time setup
    uv run task_pipe.py --input photo.jpg
    uv run task_pipe.py --input samples/ --langs en,hi,ar,ch_sim,ch_tra,es,fr,de,ru,ja,ko,pt
    uv run task_pipe.py --input photo.jpg --no-fix        # ablation: OCR without fixes
    uv run task_pipe.py --input photo.jpg --show --output-dir out/

Pipe per image:
  1. EXIF auto-rotate (phone photos)            [Pillow exif_transpose]
  2. Brighten if dark: mean-V < 125 → CLAHE + gamma lift to ~130
  3. Denoise + sharpen if blurry: Laplacian-var < 300 → bilateral + unsharp
  4. Deskew: Hough median angle (fallback: text-block minAreaRect) → warpAffine
  5. Upscale small images (h < 800px) for OCR
  6. OCR with EasyOCR (multilingual, pure-pip — no system tesseract needed)

Outputs per input:  fixed_<name>.jpg  +  <name>.txt  (+ console metrics).
Default langs cover Hindi, Arabic, Chinese (simp+trad) + 8 more = 12 total.
First run downloads EasyOCR detection/recognition models (~100MB, cached after).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_LANGS = ["en", "hi", "ar", "ch_sim", "ch_tra",
                 "es", "fr", "de", "ru", "ja", "ko", "pt"]

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


# --------------------------------------------------------------------------
def load_image(path: Path):
    import cv2
    from PIL import Image, ImageOps
    import numpy as np

    # EXIF auto-rotate first (phone rotation fix), then to OpenCV BGR.
    pil = Image.open(path)
    pil = ImageOps.exif_transpose(pil).convert("RGB")
    rgb = np.asarray(pil)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def brightness_v(img) -> float:
    import cv2
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return float(hsv[:, :, 2].mean())


def fix_brightness(img, target_v: float = 130.0):
    """CLAHE on L channel + gamma lift. Returns (img, applied, info)."""
    import cv2
    import numpy as np

    v = brightness_v(img)
    if v >= 125:
        return img, False, f"V-mean={v:.0f} (ok)"
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    img2 = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    # Gamma lift toward target brightness: want (v/255)^g = target/255.
    gamma = float(np.log(target_v / 255.0) / np.log(max(v, 1) / 255.0))
    gamma = min(max(gamma, 0.4), 2.5)
    lut = np.array([((i / 255.0) ** gamma) * 255
                    for i in range(256)]).astype("uint8")
    img2 = cv2.LUT(img2, lut)
    return img2, True, f"V-mean {v:.0f}->{brightness_v(img2):.0f} (CLAHE+γ={gamma:.2f})"


def blur_score(img) -> float:
    import cv2
    return float(cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                              cv2.CV_64F).var())


def fix_blur(img, thresh: float = 300.0):
    """Bilateral denoise + unsharp mask if Laplacian variance is low."""
    import cv2
    import numpy as np

    s = blur_score(img)
    if s >= thresh:
        return img, False, f"lap-var={s:.0f} (ok)"
    den = cv2.bilateralFilter(img, 7, 60, 60)
    gauss = cv2.GaussianBlur(den, (0, 0), 2.0)
    sharp = cv2.addWeighted(den, 1.6, gauss, -0.6, 0)
    return sharp, True, f"lap-var {s:.0f}->{blur_score(sharp):.0f} (denoise+unsharp)"


def estimate_skew_hough(img) -> float | None:
    """Skew via median angle of near-horizontal Hough segments (text baselines,
    table/page edges). Returns None if too few lines found."""
    import cv2
    import numpy as np

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gray, 50, 200)
    h, w = gray.shape
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50,
                            minLineLength=max(60, w // 8), maxLineGap=10)
    if lines is None or len(lines) < 4:
        return None
    angs = []
    for x1, y1, x2, y2 in np.asarray(lines).reshape(-1, 4):
        a = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        # Fold to [-45, 45]: near-horizontal vs near-vertical line families.
        while a <= -45:
            a += 90
        while a > 45:
            a -= 90
        if abs(a) < 45:
            angs.append(a)
    if len(angs) < 4:
        return None
    return float(np.median(angs))


def estimate_skew_contour(img) -> float:
    """Fallback: angle of dominant text-block contour via minAreaRect."""
    import cv2

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    dil = cv2.dilate(th, k, iterations=2)
    cnts, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return 0.0
    # Skip near-full-image contours (rotation border / page edge), use the
    # largest remaining text-block contour.
    img_area = float(img.shape[0] * img.shape[1])
    c = None
    for cand in sorted(cnts, key=cv2.contourArea, reverse=True):
        a = cv2.contourArea(cand)
        if a > 0.8 * img_area:
            continue
        if a < 500:
            break
        c = cand
        break
    if c is None:
        return 0.0
    angle = cv2.minAreaRect(c)[-1]
    # Normalize OpenCV's [-90, 0) to [-45, 45].
    if angle < -45:
        angle += 90
    return float(angle)


def estimate_skew(img) -> float:
    """Angle (deg) of dominant text direction. 0 = straight."""
    hough = estimate_skew_hough(img)
    if hough is not None and abs(hough) > 0.3:
        return hough
    return estimate_skew_contour(img)


def deskew(img, max_angle: float = 30.0):
    import cv2

    ang = estimate_skew(img)
    if abs(ang) < 0.5 or abs(ang) > max_angle:
        return img, False, f"skew={ang:+.1f}° (skipped)"
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    # Keep full content: expand canvas.
    import numpy as np
    cos, sin = abs(m[0, 0]), abs(m[0, 1])
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    m[0, 2] += (nw - w) / 2
    m[1, 2] += (nh - h) / 2
    out = cv2.warpAffine(img, m, (nw, nh),
                         flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    return out, True, f"skew {ang:+.1f}° corrected"


def upscale_small(img, min_h: int = 800):
    import cv2

    h = img.shape[0]
    if h >= min_h:
        return img, False
    s = min_h / h
    return cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC), True


# --------------------------------------------------------------------------
def run_pipe(path: Path, langs, no_fix: bool):
    import cv2

    img = load_image(path)
    metrics: list[str] = [f"input {img.shape[1]}x{img.shape[0]}"]
    if no_fix:
        metrics.append("fixes skipped (--no-fix)")
        return img, {"metrics": metrics}

    img, ok, m = fix_brightness(img)
    metrics.append(("brighten: " if ok else "brighten off: ") + m)
    img, ok, m = fix_blur(img)
    metrics.append(("deblur: " if ok else "deblur off: ") + m)
    img, ok, m = deskew(img)
    metrics.append(("deskew: " if ok else "deskew off: ") + m)
    img, up = upscale_small(img)
    if up:
        metrics.append(f"upscaled to {img.shape[1]}x{img.shape[0]} for OCR")
    return img, {"metrics": metrics}


def ocr_image(img, langs, gpu: bool):
    try:
        import easyocr
    except ImportError:
        sys.exit("easyocr not installed. Run:  uv sync")
    reader = ocr_image._reader
    if reader is None or ocr_image._langs != sorted(langs) \
            or getattr(reader, "gpu", None) != gpu:
        print(f"[ocr] loading EasyOCR {langs} (gpu={gpu}, first run downloads "
              "models ~100MB) ...", flush=True)
        reader = easyocr.Reader(langs, gpu=gpu)
        ocr_image._reader = reader
        ocr_image._langs = sorted(langs)
    import numpy as np
    import cv2
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = reader.readtext(rgb)
    lines = []
    for _, text, conf in results:
        t = str(text).strip()
        if t:
            lines.append((t, float(conf)))
    return lines


ocr_image._reader = None  # type: ignore[attr-defined]
ocr_image._langs: list[str] | None = None  # type: ignore[attr-defined]


# --------------------------------------------------------------------------
def collect_inputs(inp: Path):
    if inp.is_file():
        return [inp]
    files = sorted(p for p in inp.rglob("*") if p.suffix.lower() in IMG_EXTS)
    if not files:
        sys.exit(f"No images found in {inp}")
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", type=Path, required=True,
                    help="image file or directory of images")
    ap.add_argument("--output-dir", type=Path, default=Path("task_pipe_out"))
    ap.add_argument("--langs", default=",".join(DEFAULT_LANGS),
                    help="comma list, e.g. en,hi,ar,ch_sim (default: 12 langs)")
    ap.add_argument("--no-fix", action="store_true",
                    help="skip enhancement, OCR raw image (ablation)")
    ap.add_argument("--gpu", action="store_true", help="use GPU if available")
    ap.add_argument("--show", action="store_true", help="show fixed images")
    args = ap.parse_args()

    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    if len(langs) < 10:
        print(f"[warn] only {len(langs)} langs — lab asks for 10+. "
              f"Default is: {','.join(DEFAULT_LANGS)}", file=sys.stderr)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    files = collect_inputs(args.input)

    for f in files:
        print(f"\n=== {f} ===")
        try:
            fixed, info = run_pipe(f, langs, args.no_fix)
        except Exception as e:
            print(f"[error] pipe failed: {e}", file=sys.stderr)
            continue
        for m in info["metrics"]:
            print(f"  - {m}")

        try:
            lines = ocr_image(fixed, langs, args.gpu)
        except Exception as e:
            print(f"[error] OCR failed: {e}", file=sys.stderr)
            continue

        import cv2
        out_img = args.output_dir / f"fixed_{f.stem}.jpg"
        cv2.imwrite(str(out_img), fixed)
        out_txt = args.output_dir / f"{f.stem}.txt"
        with open(out_txt, "w", encoding="utf-8") as fh:
            for t, c in lines:
                fh.write(f"{t}\n")
        print(f"  - fixed image: {out_img}")
        print(f"  - text ({len(lines)} lines, "
              f"avg conf {sum(c for _, c in lines)/len(lines):.2f}): {out_txt}"
              if lines else f"  - no text detected. saved {out_txt}")
        for t, c in lines[:20]:
            print(f"    [{c:.2f}] {t}")
        if args.show:
            try:
                import cv2
                cv2.imshow(f"fixed - {f.name}", fixed)
                cv2.waitKey(0)
            except Exception as e:
                print(f"  - (--show unavailable headless: {e}; see {out_img})")
    try:
        import cv2
        cv2.destroyAllWindows()
    except Exception:
        pass


if __name__ == "__main__":
    main()