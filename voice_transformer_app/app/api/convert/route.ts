import { NextResponse } from "next/server";
import { AudioValidationError, validateAudioFile } from "@/lib/audio-validation";
import { isVoiceSlug } from "@/lib/config";
import { ElevenLabsError, transformAudio } from "@/lib/elevenlabs";

export const runtime = "nodejs";
export const maxDuration = 150;

const MAX_MULTIPART_BYTES = 16 * 1024 * 1024;

function errorResponse(message: string, status: number) {
  return NextResponse.json({ error: message }, { status });
}

export async function POST(request: Request): Promise<Response> {
  try {
    const contentType = request.headers.get("content-type") ?? "";
    if (!contentType.toLowerCase().startsWith("multipart/form-data")) {
      return errorResponse("Send audio and a target voice using multipart form data.", 400);
    }

    const contentLength = Number(request.headers.get("content-length"));
    if (Number.isFinite(contentLength) && contentLength > MAX_MULTIPART_BYTES) {
      return errorResponse("This file is too large.", 413);
    }

    let formData: FormData;
    try {
      formData = await request.formData();
    } catch {
      return errorResponse("The audio upload could not be read.", 400);
    }

    const audio = formData.get("audio");
    const voiceSlug = formData.get("voiceSlug");
    if (!(audio instanceof File)) {
      return errorResponse("Please record or upload an audio file.", 400);
    }
    if (typeof voiceSlug !== "string" || !isVoiceSlug(voiceSlug)) {
      return errorResponse("The selected voice is invalid.", 400);
    }
    if (audio.size > MAX_MULTIPART_BYTES) {
      return errorResponse("This file is too large.", 413);
    }

    await validateAudioFile(audio);

    const apiKey = process.env.ELEVENLABS_API_KEY;
    if (!apiKey) {
      return errorResponse("The ElevenLabs API key is invalid or unavailable.", 503);
    }

    let result: ArrayBuffer;
    try {
      result = await transformAudio(audio, voiceSlug, apiKey);
    } catch (error) {
      if (error instanceof ElevenLabsError) {
        return errorResponse(error.message, error.status);
      }
      console.error("Voice transformation failed.");
      return errorResponse("Something went wrong while transforming your voice.", 500);
    }

    return new Response(result, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Disposition": 'attachment; filename="transformed-voice.mp3"',
        "Cache-Control": "no-store, private",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch (error) {
    if (error instanceof AudioValidationError) {
      const status = error.code === "too_large" ? 413 : error.code === "too_long" ? 422 : 400;
      return errorResponse(error.message, status);
    }
    console.error("Unexpected error while handling voice transformation.");
    return errorResponse("Something went wrong while transforming your voice.", 500);
  }
}
