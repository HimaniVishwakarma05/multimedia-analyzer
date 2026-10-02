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

## Voice cloning

This project also includes a command-line voice cloning helper for ElevenLabs-based voice generation.

```powershell
# Create a cloned voice from a sample recording
.\.venv\Scripts\python.exe voice_cloning.py --source .\samples\voice_sample.wav --voice-name "My Cloned Voice" --api-key "YOUR_ELEVENLABS_API_KEY"

# Generate speech from an existing voice ID
.\.venv\Scripts\python.exe voice_cloning.py --voice-id "EXAVITQu4vr4xnSDxMaL" --text "Hello from the multimedia analyzer" --api-key "YOUR_ELEVENLABS_API_KEY" --output .\output\speech.mp3

# Clone then synthesize in one command
.\.venv\Scripts\python.exe voice_cloning.py --source .\samples\voice_sample.wav --voice-name "My Cloned Voice" --text "This audio was generated from a cloned voice" --api-key "YOUR_ELEVENLABS_API_KEY" --output .\output\result.mp3
```

Set the API key in the environment instead of passing it each time:

```powershell
$env:ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
```

### Simple web app

A minimal Flask-based voice-transformer UI is available in `voice_transformer_app`.

```powershell
.\.venv\Scripts\python.exe voice_transformer_app\app.py
```

Then open:

```text
http://localhost:5000
```

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
