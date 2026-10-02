import { MAX_AUDIO_BYTES, MAX_AUDIO_SECONDS } from "./config";

const ALLOWED_EXTENSIONS = new Set([".mp3", ".wav", ".m4a", ".ogg", ".oga", ".flac", ".webm"]);

export async function inspectAudioFile(file: File): Promise<number> {
  if (!file.size) throw new Error("The selected audio file is empty.");
  if (file.size > MAX_AUDIO_BYTES) throw new Error("This file is too large. Maximum size is 15 MB.");

  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0];
  if (!extension || !ALLOWED_EXTENSIONS.has(extension)) {
    throw new Error("Use an MP3, WAV, M4A, OGG/OGA, FLAC, or WebM audio file.");
  }

  const objectUrl = URL.createObjectURL(file);
  try {
    const duration = await new Promise<number>((resolve, reject) => {
      const audio = new Audio();
      audio.preload = "metadata";
      audio.onloadedmetadata = () => resolve(audio.duration);
      audio.onerror = () => reject(new Error("The audio file is corrupt or unreadable."));
      audio.src = objectUrl;
    });

    if (!Number.isFinite(duration) || duration <= 0) {
      throw new Error("The audio file is corrupt or unreadable.");
    }
    if (duration > MAX_AUDIO_SECONDS) {
      throw new Error("Your audio must be 30 seconds or shorter.");
    }
    return duration;
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}
