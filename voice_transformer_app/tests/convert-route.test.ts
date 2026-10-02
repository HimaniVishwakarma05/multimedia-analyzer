import assert from "node:assert/strict";
import { test } from "node:test";
import { POST } from "../app/api/convert/route";

function wavFile(): File {
  const rate = 8_000;
  const dataLength = rate * 2;
  const bytes = Buffer.alloc(44 + dataLength);
  bytes.write("RIFF", 0);
  bytes.writeUInt32LE(36 + dataLength, 4);
  bytes.write("WAVE", 8);
  bytes.write("fmt ", 12);
  bytes.writeUInt32LE(16, 16);
  bytes.writeUInt16LE(1, 20);
  bytes.writeUInt16LE(1, 22);
  bytes.writeUInt32LE(rate, 24);
  bytes.writeUInt32LE(rate * 2, 28);
  bytes.writeUInt16LE(2, 32);
  bytes.writeUInt16LE(16, 34);
  bytes.write("data", 36);
  bytes.writeUInt32LE(dataLength, 40);
  return new File([bytes], "sample.wav", { type: "audio/wav" });
}

function requestWith(audio = wavFile(), voiceSlug = "warm-narrator"): Request {
  const formData = new FormData();
  formData.append("audio", audio);
  formData.append("voiceSlug", voiceSlug);
  return new Request("http://localhost/api/convert", { method: "POST", body: formData });
}

test("returns a safe error when no API key is configured", async () => {
  const previousKey = process.env.ELEVENLABS_API_KEY;
  const previousVoice = process.env.ELEVENLABS_VOICE_WARM_ID;
  delete process.env.ELEVENLABS_API_KEY;
  delete process.env.ELEVENLABS_VOICE_WARM_ID;
  try {
    const response = await POST(requestWith());
    assert.equal(response.status, 503);
    assert.deepEqual(await response.json(), {
      error: "The ElevenLabs API key is invalid or unavailable.",
    });
  } finally {
    if (previousKey === undefined) delete process.env.ELEVENLABS_API_KEY;
    else process.env.ELEVENLABS_API_KEY = previousKey;
    if (previousVoice === undefined) delete process.env.ELEVENLABS_VOICE_WARM_ID;
    else process.env.ELEVENLABS_VOICE_WARM_ID = previousVoice;
  }
});

test("rejects a voice slug outside the allowlist", async () => {
  const response = await POST(requestWith(wavFile(), "unapproved-voice"));
  assert.equal(response.status, 400);
  assert.deepEqual(await response.json(), { error: "The selected voice is invalid." });
});

test("returns MPEG audio and sends the source recording directly to ElevenLabs", async () => {
  const previousKey = process.env.ELEVENLABS_API_KEY;
  const previousVoice = process.env.ELEVENLABS_VOICE_WARM_ID;
  const previousFetch = globalThis.fetch;
  process.env.ELEVENLABS_API_KEY = "test-server-key";
  process.env.ELEVENLABS_VOICE_WARM_ID = "synthetic-test-voice";
  let requestUrl = "";
  let requestOptions: RequestInit | undefined;
  globalThis.fetch = async (input, init) => {
    requestUrl = String(input);
    requestOptions = init;
    return new Response(new Uint8Array([73, 68, 51]), {
      status: 200,
      headers: { "Content-Type": "audio/mpeg" },
    });
  };

  try {
    const response = await POST(requestWith());
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("Content-Type"), "audio/mpeg");
    assert.equal(response.headers.get("Cache-Control"), "no-store, private");
    assert.deepEqual(Array.from(new Uint8Array(await response.arrayBuffer())), [73, 68, 51]);
    assert.equal(
      requestUrl,
      "https://api.elevenlabs.io/v1/speech-to-speech/synthetic-test-voice?output_format=mp3_44100_128",
    );
    assert.equal(new Headers(requestOptions?.headers).get("xi-api-key"), "test-server-key");
    const form = requestOptions?.body as FormData;
    assert.equal(form.get("model_id"), "eleven_multilingual_sts_v2");
    assert.ok(form.get("audio") instanceof File);
  } finally {
    globalThis.fetch = previousFetch;
    if (previousKey === undefined) delete process.env.ELEVENLABS_API_KEY;
    else process.env.ELEVENLABS_API_KEY = previousKey;
    if (previousVoice === undefined) delete process.env.ELEVENLABS_VOICE_WARM_ID;
    else process.env.ELEVENLABS_VOICE_WARM_ID = previousVoice;
  }
});
