import {
  ELEVENLABS_MODEL_ID,
  ELEVENLABS_OUTPUT_FORMAT,
  getVoiceId,
  type VoiceSlug,
} from "./config";

const ELEVENLABS_STS_URL = "https://api.elevenlabs.io/v1/speech-to-speech";

export type ProviderErrorCode = "invalid_key" | "quota" | "voice_unavailable" | "provider_failure";

export class ElevenLabsError extends Error {
  constructor(
    public readonly code: ProviderErrorCode,
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ElevenLabsError";
  }
}

export async function transformAudio(
  audio: File,
  voiceSlug: VoiceSlug,
  apiKey: string,
  fetchImplementation: typeof fetch = fetch,
): Promise<ArrayBuffer> {
  const voiceId = getVoiceId(voiceSlug);
  if (!voiceId) {
    throw new ElevenLabsError("voice_unavailable", "The selected voice is currently unavailable.", 503);
  }

  const body = new FormData();
  body.append("audio", audio, audio.name);
  body.append("model_id", ELEVENLABS_MODEL_ID);

  let response: Response;
  try {
    response = await fetchImplementation(
      `${ELEVENLABS_STS_URL}/${encodeURIComponent(voiceId)}?output_format=${ELEVENLABS_OUTPUT_FORMAT}`,
      {
        method: "POST",
        headers: { "xi-api-key": apiKey, Accept: "audio/mpeg" },
        body,
        signal: AbortSignal.timeout(120_000),
      },
    );
  } catch {
    throw new ElevenLabsError("provider_failure", "The AI voice service could not be reached.", 502);
  }

  if (response.status === 401 || response.status === 403) {
    throw new ElevenLabsError(
      "invalid_key",
      "The ElevenLabs API key is invalid or unavailable.",
      502,
    );
  }
  if (response.status === 429) {
    throw new ElevenLabsError("quota", "The AI voice service quota has been reached.", 429);
  }
  if (response.status >= 400) {
    throw new ElevenLabsError(
      "provider_failure",
      "Something went wrong while transforming your voice.",
      502,
    );
  }

  const audioBytes = await response.arrayBuffer();
  if (!audioBytes.byteLength) {
    throw new ElevenLabsError(
      "provider_failure",
      "The AI voice service returned an empty audio file.",
      502,
    );
  }
  return audioBytes;
}
