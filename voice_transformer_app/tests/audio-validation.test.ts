import assert from "node:assert/strict";
import { test } from "node:test";
import { AudioValidationError, validateAudioFile } from "../lib/audio-validation";

function wavFile(durationSeconds = 1, name = "sample.wav"): File {
  const sampleRate = 8_000;
  const dataBytes = sampleRate * durationSeconds * 2;
  const bytes = Buffer.alloc(44 + dataBytes);
  bytes.write("RIFF", 0);
  bytes.writeUInt32LE(36 + dataBytes, 4);
  bytes.write("WAVE", 8);
  bytes.write("fmt ", 12);
  bytes.writeUInt32LE(16, 16);
  bytes.writeUInt16LE(1, 20);
  bytes.writeUInt16LE(1, 22);
  bytes.writeUInt32LE(sampleRate, 24);
  bytes.writeUInt32LE(sampleRate * 2, 28);
  bytes.writeUInt16LE(2, 32);
  bytes.writeUInt16LE(16, 34);
  bytes.write("data", 36);
  bytes.writeUInt32LE(dataBytes, 40);
  return new File([bytes], name, { type: "audio/wav" });
}

test("accepts valid short WAV and reports parsed duration", async () => {
  const duration = await validateAudioFile(wavFile());
  assert.ok(duration > 0.99 && duration < 1.01);
});

test("rejects unsupported extensions", async () => {
  await assert.rejects(validateAudioFile(wavFile(1, "sample.exe")), (error: unknown) =>
    error instanceof AudioValidationError && error.code === "invalid_audio");
});

test("rejects corrupt audio bytes", async () => {
  const file = new File([Buffer.from("not audio")], "broken.wav", { type: "audio/wav" });
  await assert.rejects(validateAudioFile(file), (error: unknown) =>
    error instanceof AudioValidationError && error.code === "invalid_audio");
});

test("rejects audio whose parsed duration exceeds 30 seconds", async () => {
  await assert.rejects(validateAudioFile(wavFile(31)), (error: unknown) =>
    error instanceof AudioValidationError && error.code === "too_long");
});

test("rejects empty audio files", async () => {
  const file = new File([], "empty.wav", { type: "audio/wav" });
  await assert.rejects(validateAudioFile(file), (error: unknown) =>
    error instanceof AudioValidationError && error.code === "invalid_audio");
});
