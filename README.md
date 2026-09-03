# Multimedia Analyzer

A Python-based multimedia analyzer project that extracts and displays metadata from **images, videos, and audio files**.

## 📌 Project Overview

This project contains three analyzers:

1. **Image Analyzer** – extracts image properties and EXIF metadata.
2. **Video Analyzer** – extracts video properties such as resolution, FPS, duration, and codec.
3. **Audio Analyzer** – extracts audio properties such as duration, bitrate, sample rate, and metadata.

---

## 📂 Project Structure

```text
multimedia-analyzer/
│
├── image_analyzer.py
├── video_analyzer.py
├── audio_analyzer.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── samples/
    ├── sample.jpg
    ├── sample.mp4
    └── sample.mp3
```

---

# 🖼️ Task 1: Image Analyzer

The Image Analyzer accepts an image path and displays important image information.

### Information Extracted

* File Name
* File Size
* File Format
* Width
* Height
* Resolution
* Color Mode
* Camera Information
* Date Taken
* Orientation
* EXIF Metadata

### Supported Formats

* JPG
* JPEG
* PNG
* TIFF
* WEBP
* BMP

### Run

```bash
python image_analyzer.py samples/sample.jpg
```

### Example Output

```text
================================
IMAGE METADATA REPORT
================================

File Name       : sample.jpg
File Size       : 245.67 KB
File Format     : JPEG
Width           : 1920 pixels
Height          : 1080 pixels
Resolution      : 72 x 72 DPI
Color Mode      : RGB

EXIF Metadata
-------------------------------
Camera          : Canon
Date Taken      : 2026:09:02 10:30:21
Orientation     : 1
```

---

# 🎥 Task 2: Video Analyzer

The Video Analyzer extracts basic technical information from a video file.

### Information Extracted

* File Name
* File Size
* Width
* Height
* FPS (Frames Per Second)
* Frame Count
* Duration
* Codec

### Run

```bash
python video_analyzer.py samples/sample.mp4
```

### Example Output

```text
================================
VIDEO METADATA REPORT
================================

File Name       : sample.mp4
File Size       : 12.45 MB
Width           : 1920 pixels
Height          : 1080 pixels
FPS             : 30.00
Frame Count     : 900
Duration        : 30.00 seconds
Codec           : mp4v
```

---

# 🎵 Task 3: Audio Analyzer

The Audio Analyzer extracts technical information and metadata from an audio file.

### Information Extracted

* File Name
* File Size
* Duration
* Bitrate
* Sample Rate
* Number of Channels
* Title
* Artist
* Album
* Genre

### Run

```bash
python audio_analyzer.py samples/sample.mp3
```

### Example Output

```text
================================
AUDIO METADATA REPORT
================================

File Name       : sample.mp3
File Size       : 4.25 MB
Duration        : 210.50 seconds
Bitrate         : 320 kbps
Sample Rate     : 44100 Hz
Channels        : 2

Audio Metadata
-------------------------------
Title           : Sample Song
Artist          : Sample Artist
Album           : Sample Album
Genre           : Pop
```

---

# 🛠️ Technologies Used

* Python
* Pillow
* OpenCV
* Mutagen
* Git
* GitHub
* VS Code

---

# 📦 Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Go to the project folder:

```bash
cd multimedia-analyzer
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

---

# ▶️ Usage

### Image

```bash
python image_analyzer.py samples/sample.jpg
```

### Video

```bash
python video_analyzer.py samples/sample.mp4
```

### Audio

```bash
python audio_analyzer.py samples/sample.mp3
```

---

# 🎯 Objective

The objective of this project is to understand how Python can be used to analyze different types of multimedia files and extract useful metadata from them.

---

# 👩‍💻 Author

**Himani Vishwakarma**

MCA Student
