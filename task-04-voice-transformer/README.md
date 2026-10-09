# Task 04 — Speech-to-Speech Voice Transformer

Local Python CLI and Flask interface for transforming a recording into an
authorized, configured synthetic voice using ElevenLabs Speech-to-Speech. This
project does not clone a voice from the uploaded recording.

## Setup (Windows PowerShell)

From the repository root:

```powershell
cd .\task-04-voice-transformer
..\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
Copy-Item .\.env.example .\.env
notepad .\.env
```

Replace the API key and all voice-ID placeholders in `.env`. Use voices you
control or are authorized to use. `.env` is ignored by Git; never commit or
share it.

## Run the web interface

```powershell
..\.venv\Scripts\python.exe .\voice_transformer.py --serve
```

Open <http://127.0.0.1:5000>. Record up to 30 seconds in the browser or upload
MP3, WAV, M4A, OGG/OGA, FLAC, or WebM (maximum 15 MB). The server validates the
audio again before sending it to ElevenLabs. Browser audio access works on
localhost; microphone permission is required to record.

## Run from the command line

```powershell
..\.venv\Scripts\python.exe .\voice_transformer.py `
  --input .\short-recording.mp3 `
  --voice warm-narrator `
  --output .\outputs\transformed.mp3 `
  --confirm-permission
```

Use a source recording no longer than 30 seconds. The repository's
`..\samples\audio.mp3` sample is about 70 seconds, so it exceeds this limit.

CLI output is written only to the path explicitly supplied with `--output`.
Web uploads and results are held in memory and are not saved to disk.

## Configuration

`ELEVENLABS_API_KEY` is sent only from the server to ElevenLabs. Configure three
voice IDs in `.env`:

- `ELEVENLABS_VOICE_WARM_ID`
- `ELEVENLABS_VOICE_DEEP_ID`
- `ELEVENLABS_VOICE_BRIGHT_ID`

The application calls `eleven_multilingual_sts_v2` and requests
`mp3_44100_128` output. API usage can incur charges or consume account quota.

## Tests

```powershell
..\.venv\Scripts\python.exe -m unittest discover -s .\tests -v
```

Only use recordings you own or have permission to transform. Do not use the
result to impersonate a real person.
