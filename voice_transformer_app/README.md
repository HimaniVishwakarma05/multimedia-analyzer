# AI Voice Cloning & Voice Transformation

A consent-first MCA Multimedia project that transforms a user's recording into one of three developer-controlled synthetic voices. It uses ElevenLabs Speech-to-Speech directly on audio: it does not transcribe and resynthesize speech, create cloned voice identities, or offer real-person impersonation.

## Project objective

Build a responsive web application for recording or uploading short speech clips, choosing a synthetic target voice, and comparing/downloading the resulting MP3. The speech-to-speech model is intended to retain the speaker's words, timing, pauses, emphasis, and emotional performance while changing the perceived voice.

## Features

- Record from the microphone, pause/resume, preview, discard/re-record, and automatically stop at 30 seconds.
- Upload MP3, WAV, M4A, OGG/OGA, FLAC, or WebM files, up to 15 MB.
- Validate audio format, readability, duration, and size in the browser and again on the server.
- Select Warm Narrator, Deep Studio, or Bright Conversational from a fixed allowlist.
- Send audio directly to `eleven_multilingual_sts_v2`; no transcription step.
- Compare original and transformed audio, with single-player-at-a-time behavior and MP3 download.
- Require a recording-permission and non-impersonation confirmation before conversion.
- Keep provider credentials on the server and avoid persistent audio storage.

## Technology stack

Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 4, Node.js, ElevenLabs Speech-to-Speech API, MediaRecorder, Web Audio API, and Vercel.

## System architecture

```text
Browser (MediaRecorder / file picker / audio preview)
    │  multipart/form-data: audio + voiceSlug
    ▼
Next.js POST /api/convert
    ├─ checks voice allowlist, format, size, and parsed duration
    ├─ resolves the selected voice slug to a server environment variable
    ├─ forwards the audio to ElevenLabs Speech-to-Speech
    └─ returns no-store audio/mpeg bytes
    ▼
Browser (compare original/result and download MP3)
```

Audio is kept in memory for request processing. The application does not write uploaded or transformed audio to disk or a database. The selected provider, ElevenLabs, processes the source audio to perform transformation.

## How it works

1. Record or select an audio file. The interface checks size, supported extension, and browser-readable duration.
2. Confirm permission to use the recording and select a synthetic voice.
3. The server revalidates the uploaded bytes and parses their audio metadata to reject unreadable, unsupported, empty, oversized, or longer-than-30-second files.
4. The server sends the source audio, voice ID, and `eleven_multilingual_sts_v2` model ID to ElevenLabs with `mp3_44100_128` output.
5. The response is returned as an uncached MP3. The browser provides playback, comparison, and a download link.

## ElevenLabs API setup

Create an ElevenLabs API key and configure three voice IDs for synthetic/developer-controlled voices you are authorized to use. The application does not create or clone a voice from the user's recording. Keep the key and voice IDs in server environment variables only.

Copy `.env.example` to `.env.local` and replace the placeholders:

```dotenv
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_VOICE_WARM_ID=your_synthetic_voice_id
ELEVENLABS_VOICE_DEEP_ID=your_synthetic_voice_id
ELEVENLABS_VOICE_BRIGHT_ID=your_synthetic_voice_id
```

Never prefix `ELEVENLABS_API_KEY` with `NEXT_PUBLIC_`. Do not commit `.env.local`. API credentials are read only by the Node.js route handler.

## Local installation

From this directory (`voice_transformer_app`):

```powershell
npm install
Copy-Item .env.example .env.local
# Edit .env.local and provide the key and three voice IDs.
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Microphone access requires HTTPS or localhost and the browser's permission.

## Running checks

```powershell
npm run lint
npm run typecheck
npm test
npm run build
```

The test suite covers audio parsing/validation and the `POST /api/convert` route, including allowlisting, secret handling, provider request shape, and response headers. The provider call is mocked by automated tests. For a real provider smoke test, configure valid credentials and voice IDs in `.env.local`, run the app, record/upload a short consented sample, and submit it. Provider usage/quota may incur charges.

Manual browser checks:

- Test microphone permission allow/deny, recording, pause/resume, stop, discard, timer and level meter.
- Upload each supported format and verify empty/corrupt, >15 MB, and >30-second clips are rejected.
- Confirm conversion, original/result playback, player comparison and downloaded MP3.
- Check the browser network panel: the ElevenLabs key must not appear in any client request or bundle.

## Deployment on Vercel

1. Import this project directory into Vercel, or configure the repository root as `voice_transformer_app`.
2. Add `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_WARM_ID`, `ELEVENLABS_VOICE_DEEP_ID`, and `ELEVENLABS_VOICE_BRIGHT_ID` as server-only environment variables for each deployment environment.
3. Deploy with the Next.js framework preset. The Node.js route has a 150-second maximum duration and performs no persistent file writes.
4. Confirm account plan/runtime limits permit the 15 MB multipart request and provider processing time. Use HTTPS for microphone access.
5. Run a short test with a consented recording and verify provider quota, playback, and download.

## Privacy and safety

Audio is sent directly to ElevenLabs, which processes it under its service terms and privacy policy. This app does not retain audio after the request or store it in a database. The browser temporarily holds preview/result object URLs until they are removed or the page is closed. Users must confirm they have permission to use each recording. Use only synthetic/developer-controlled voices; unauthorized cloning or impersonation of real people is not supported. Do not upload sensitive or confidential audio.

## Limitations

- Speech-to-speech transformation may not perfectly preserve every word, pause, accent, or expressive detail; results depend on the input and provider.
- Hindi and Hinglish are sent as audio without transcription, but output quality and language/accent fidelity depend on ElevenLabs model and voice support.
- A configured ElevenLabs account, API key, voice IDs, and sufficient quota are required.
- This demonstration does not provide user authentication, permanent history, or a database.
- The 15 MB limit applies to the local app and may also need to be adjusted to deployment platform request limits.
- Web Audio microphone visualization requires a modern browser and a secure context (localhost or HTTPS).

## Future enhancements

- Real-time voice transformation.
- User authentication.
- Voice history.
- Database integration.
- More synthetic voices.
- Advanced audio controls.
- Background-noise removal.
- Voice cloning with explicit consent and an appropriate paid provider plan.
- Analytics dashboard.
- Multi-user support.
