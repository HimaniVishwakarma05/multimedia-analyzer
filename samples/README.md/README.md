# Multimedia Analyzer

A Python-based multimedia metadata analyzer that extracts useful information from image, video, and audio files.

## Features

### Image Analyzer

The image analyzer extracts:

* File name
* File size
* File format
* Width
* Height
* Resolution
* Color mode
* EXIF metadata
* Camera information
* Date taken
* Orientation

Supported formats include:

* JPG
* JPEG
* PNG
* TIFF
* WEBP
* BMP

### Video Analyzer

The video analyzer extracts:

* File name
* File size
* Video dimensions
* FPS
* Frame count
* Duration
* Codec

### Audio Analyzer

The audio analyzer extracts:

* File name
* File size
* Duration
* Bitrate
* Sample rate
* Number of channels
* Title
* Artist
* Album
* Genre

## Technologies Used

* Python
* Pillow
* OpenCV
* Mutagen

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

Move into the project:

```bash
cd multimedia-analyzer
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

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

## Project Structure

```text
multimedia-analyzer/
│
├── image_analyzer.py
├── video_analyzer.py
├── audio_analyzer.py
├── requirements.txt
├── README.md
└── samples/
```

## Author

Himani Vishwakarma
