# Multimedia Analyzer

A command-line tool for reading metadata from image, audio, and video files.

## Setup

Create and activate the project virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Usage

Use the unified entry point for any supported file:

```powershell
.\.venv\Scripts\python.exe multimedia_analyzer.py samples/sample.jpg
.\.venv\Scripts\python.exe multimedia_analyzer.py samples/audio.mp3
.\.venv\Scripts\python.exe multimedia_analyzer.py samples/video.mp4
.\.venv\Scripts\python.exe multimedia_analyzer.py samples/video.mp4 --play
```

You can also run an individual analyzer:

```powershell
.\.venv\Scripts\python.exe image_analyzer.py samples/sample.jpg
.\.venv\Scripts\python.exe audio_analyzer.py samples/audio.mp3
.\.venv\Scripts\python.exe video_analyzer.py samples/video.mp4

# Analyze metadata and play the video in an HD-sized preview window
.\.venv\Scripts\python.exe video_analyzer.py samples/video.mp4 --play
```

## AI voice transformation web app

A consent-first Next.js Speech-to-Speech application is available in `voice_transformer_app`. It transforms recordings only into configured developer-controlled synthetic voices; it does not create cloned voices or support real-person impersonation.

```powershell
cd voice_transformer_app
npm install
Copy-Item .env.example .env.local
# Add the ElevenLabs API key and synthetic voice IDs to .env.local.
npm run dev
```

Open `http://localhost:3000`. See [voice_transformer_app/README.md](voice_transformer_app/README.md) for setup, privacy, testing and Vercel deployment details.

The app sends source audio directly to ElevenLabs Speech-to-Speech. Provider credentials are server-only, and uploaded/generated audio is not permanently stored by the app.

## Quick Windows launcher

From the project root, you can use the included batch file:

```powershell
run_multimedia_analyzer.bat image samples\sample.jpg
run_multimedia_analyzer.bat audio samples\audio.mp3
run_multimedia_analyzer.bat video samples\video.mp4
run_multimedia_analyzer.bat video samples\video.mp4 --play
```

This launcher automatically uses the project virtual environment in `.venv`.

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
