# Multimedia Analyzer

A command-line tool for reading metadata from image, audio, and video files.

## Setup

```bash
python -m pip install -r requirements.txt
```

## Usage

Use the unified entry point for any supported file:

```bash
python multimedia_analyzer.py samples/sample.jpg
python multimedia_analyzer.py samples/audio.mp3
python multimedia_analyzer.py path/to/video.mp4
```

You can also run an individual analyzer:

```bash
python image_analyzer.py path/to/image.jpg
python audio_analyzer.py path/to/audio.mp3
python video_analyzer.py path/to/video.mp4

# Analyze metadata and play the video in an HD-sized preview window
python video_analyzer.py path/to/video.mp4 --play
```

Supported image formats: JPG, JPEG, PNG, TIFF, WEBP, BMP.

Supported audio formats: MP3, WAV, FLAC, M4A, OGG.

Supported video formats: MP4, AVI, MOV, MKV, WEBM.

## Project Structure

```text
multimedia-analyzer/
├── image_analyzer.py
├── audio_analyzer.py
├── video_analyzer.py
├── multimedia_analyzer.py
├── requirements.txt
├── README.md
├── samples/
└── legacy/
```