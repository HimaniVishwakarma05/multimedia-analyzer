export const MAX_AUDIO_BYTES = 15 * 1024 * 1024;
export const MAX_AUDIO_SECONDS = 30;
export const ELEVENLABS_MODEL_ID = "eleven_multilingual_sts_v2";
export const ELEVENLABS_OUTPUT_FORMAT = "mp3_44100_128";

export const VOICES = [
  {
    slug: "warm-narrator",
    name: "Warm Narrator",
    description: "A composed, welcoming voice for stories and presentations.",
    style: "WARM · CLEAR",
    envName: "ELEVENLABS_VOICE_WARM_ID",
  },
  {
    slug: "deep-studio",
    name: "Deep Studio",
    description: "A resonant studio tone with a confident, measured delivery.",
    style: "RICH · STEADY",
    envName: "ELEVENLABS_VOICE_DEEP_ID",
  },
  {
    slug: "bright-conversational",
    name: "Bright Conversational",
    description: "An upbeat, natural-sounding voice for everyday conversation.",
    style: "BRIGHT · NATURAL",
    envName: "ELEVENLABS_VOICE_BRIGHT_ID",
  },
] as const;

export type VoiceSlug = (typeof VOICES)[number]["slug"];

export function isVoiceSlug(value: string): value is VoiceSlug {
  return VOICES.some((voice) => voice.slug === value);
}

export function getVoiceId(slug: VoiceSlug): string | undefined {
  const voice = VOICES.find((option) => option.slug === slug);
  return voice ? process.env[voice.envName] : undefined;
}
