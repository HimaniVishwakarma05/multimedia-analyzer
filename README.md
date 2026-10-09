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
.\.venv\Scripts\python.exe .\multimedia_analyzer.py .\samples\sample.jpg
.\.venv\Scripts\python.exe .\multimedia_analyzer.py .\samples\audio.mp3
.\.venv\Scripts\python.exe .\multimedia_analyzer.py .\samples\video.mp4
.\.venv\Scripts\python.exe .\multimedia_analyzer.py .\samples\video.mp4 --play
```

Run a script with Python; do not type `image` or the image path by itself as a PowerShell command.

You can also run an individual analyzer:

```powershell
.\.venv\Scripts\python.exe .\image_analyzer.py .\samples\sample.jpg
.\.venv\Scripts\python.exe .\audio_analyzer.py .\samples\audio.mp3
.\.venv\Scripts\python.exe .\video_analyzer.py .\samples\video.mp4

# Analyze metadata and play the video in an HD-sized preview window
.\.venv\Scripts\python.exe .\video_analyzer.py .\samples\video.mp4 --play
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

## Python speech-to-speech voice transformer

The `task-04-voice-transformer` folder also contains a local Python CLI and Flask
interface for transforming short, authorized recordings into configured
synthetic voices. It uses ElevenLabs Speech-to-Speech and does not clone a voice
from the uploaded recording. See
[task-04-voice-transformer/README.md](./task-04-voice-transformer/README.md) for
setup, CLI usage, supported formats, and tests.

```powershell
cd .\task-04-voice-transformer
..\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
Copy-Item .\.env.example .\.env
notepad .\.env
..\.venv\Scripts\python.exe .\voice_transformer.py --serve
```

Fill in the ElevenLabs API key and authorized target voice IDs in `.env`, then
open `http://127.0.0.1:5000`. The `.env` file is private and Git-ignored.

## Quick Windows launcher

From the project root, you can use the included batch file:

```powershell
.\run_multimedia_analyzer.bat image .\samples\sample.jpg
.\run_multimedia_analyzer.bat audio .\samples\audio.mp3
.\run_multimedia_analyzer.bat video .\samples\video.mp4
.\run_multimedia_analyzer.bat video .\samples\video.mp4 --play
```

This launcher automatically uses the project virtual environment in `.venv`.

## Voice cloning (ElevenLabs)

Install the project dependencies and create a private local environment file:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
if (-not (Test-Path .\.env)) { Copy-Item .\.env.example .\.env }
notepad .\.env
```

In `.env`, replace `your_elevenlabs_api_key_here` with your ElevenLabs API key.
Keep `.env` private; it is excluded from Git. Do not paste the key into source
code or commit it.

Create a voice from an audio sample:

```powershell
.\.venv\Scripts\python.exe .\voice_cloning.py `
  --source .\samples\audio.mp3 `
  --voice-name "My Test Voice"
```

To also synthesize a short test and save it as an MP3:

```powershell
.\.venv\Scripts\python.exe .\voice_cloning.py `
  --source .\samples\audio.mp3 `
  --voice-name "My Test Voice" `
  --text "This is a short test of my voice." `
  --output .\voice_test.mp3
```

Only use recordings you own or have permission to use. The source audio is sent
to ElevenLabs, and cloning or synthesis may use account quota.

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
