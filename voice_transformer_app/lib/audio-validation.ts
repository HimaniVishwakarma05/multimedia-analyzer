import { parseBuffer } from "music-metadata";
import { MAX_AUDIO_BYTES, MAX_AUDIO_SECONDS } from "./config";

const MIME_TYPES_BY_EXTENSION: Record<string, readonly string[]> = {
  ".mp3": ["audio/mpeg", "audio/mp3"],
  ".wav": ["audio/wav", "audio/x-wav", "audio/wave"],
  ".m4a": ["audio/mp4", "audio/x-m4a"],
  ".ogg": ["audio/ogg", "audio/x-ogg", "application/ogg"],
  ".oga": ["audio/ogg", "audio/x-ogg", "application/ogg"],
  ".flac": ["audio/flac", "audio/x-flac"],
  ".webm": ["audio/webm"],
};

export type AudioValidationErrorCode = "too_large" | "invalid_audio" | "too_long";

export class AudioValidationError extends Error {
  constructor(
    public readonly code: AudioValidationErrorCode,
    message: string,
  ) {
    super(message);
    this.name = "AudioValidationError";
  }
}

function getWavDurationFromHeader(bytes: Uint8Array): number | null {
  if (bytes.length < 12 || bytes[0] !== 0x52 || bytes[1] !== 0x49 || bytes[2] !== 0x46 || bytes[3] !== 0x46) {
    return null;
  }

  const riffSize = bytes.readUInt32LE(4);
  const minimumExpectedSize = 8 + riffSize;
  if (riffSize < 4 || bytes.length < minimumExpectedSize) {
    return null;
  }

  if (bytes[8] !== 0x57 || bytes[9] !== 0x41 || bytes[10] !== 0x56 || bytes[11] !== 0x45) {
    return null;
  }

  let offset = 12;
  let sampleRate: number | undefined;
  let blockAlign: number | undefined;
  let dataSize: number | undefined;

  while (offset + 8 <= bytes.length) {
    const chunkId = bytes.slice(offset, offset + 4).toString("ascii");
    const chunkSize = bytes.readUInt32LE(offset + 4);
    const payloadOffset = offset + 8;
    const payloadEnd = payloadOffset + chunkSize;

    if (chunkId === "fmt ") {
      if (payloadEnd > bytes.length) {
        return null;
      }
      sampleRate = bytes.readUInt32LE(payloadOffset + 4);
      blockAlign = bytes.readUInt16LE(payloadOffset + 12);
    } else if (chunkId === "data") {
      if (payloadEnd > bytes.length) {
        return null;
      }
      dataSize = chunkSize;
    }

    offset += 8 + chunkSize + (chunkSize % 2);
  }

  if (!sampleRate || !blockAlign || !dataSize || dataSize <= 0) {
    return null;
  }

  return dataSize / (sampleRate * blockAlign);
}

export async function validateAudioFile(file: File): Promise<number> {
  if (file.size === 0) {
    throw new AudioValidationError("invalid_audio", "The audio file is empty or invalid.");
  }

  if (file.size > MAX_AUDIO_BYTES) {
    throw new AudioValidationError("too_large", "This file is too large.");
  }

  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0];
  const allowedMimeTypes = extension ? MIME_TYPES_BY_EXTENSION[extension] : undefined;
  const declaredMimeType = file.type.toLowerCase().split(";")[0].trim();

  if (!allowedMimeTypes) {
    throw new AudioValidationError(
      "invalid_audio",
      "Use an MP3, WAV, M4A, OGG/OGA, FLAC, or WebM audio file.",
    );
  }

  const declaredMimeIsRecognized =
    !declaredMimeType ||
    allowedMimeTypes.includes(declaredMimeType) ||
    declaredMimeType === "application/octet-stream";

  if (declaredMimeType && !declaredMimeIsRecognized) {
    throw new AudioValidationError(
      "invalid_audio",
      "Use an MP3, WAV, M4A, OGG/OGA, FLAC, or WebM audio file.",
    );
  }

  const buffer = Buffer.from(await file.arrayBuffer());

  let duration: number | undefined;
  try {
    const metadata = await parseBuffer(
      buffer,
      declaredMimeType && declaredMimeType !== "application/octet-stream" ? declaredMimeType : undefined,
      { duration: true },
    );
    duration = metadata.format.duration ?? Number.NaN;
  } catch {
    duration = undefined;
  }

  if (!Number.isFinite(duration)) {
    const wavFallbackDuration = getWavDurationFromHeader(buffer);
    if (wavFallbackDuration !== null && Number.isFinite(wavFallbackDuration)) {
      duration = wavFallbackDuration;
    }
  }

  if (!Number.isFinite(duration) || duration <= 0) {
    throw new AudioValidationError("invalid_audio", "The audio file is corrupt or unreadable.");
  }

  if (duration > MAX_AUDIO_SECONDS) {
    throw new AudioValidationError("too_long", "Your audio must be 30 seconds or shorter.");
  }

  return duration;
}
