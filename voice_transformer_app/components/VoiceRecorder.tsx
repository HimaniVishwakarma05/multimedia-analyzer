"use client";

import { useEffect, useRef, useState } from "react";
import { MAX_AUDIO_SECONDS } from "@/lib/config";

type VoiceRecorderProps = {
  onRecording: (file: File | null) => void;
  disabled?: boolean;
};

type RecorderStatus = "idle" | "recording" | "paused";

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
  const remainder = (seconds % 60).toString().padStart(2, "0");
  return `${minutes}:${remainder}`;
}

export function VoiceRecorder({ onRecording, disabled }: VoiceRecorderProps) {
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startedAtRef = useRef(0);
  const elapsedBeforePauseRef = useRef(0);
  const discardRef = useRef(false);

  function stopVisuals() {
    if (animationRef.current !== null) cancelAnimationFrame(animationRef.current);
    if (timerRef.current) clearInterval(timerRef.current);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    animationRef.current = null;
    timerRef.current = null;
    timeoutRef.current = null;
  }

  function drawLevel(analyser: AnalyserNode, context: CanvasRenderingContext2D) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const values = new Uint8Array(analyser.frequencyBinCount);
    const render = () => {
      analyser.getByteFrequencyData(values);
      context.clearRect(0, 0, canvas.width, canvas.height);
      const bars = 34;
      const gap = 5;
      const width = (canvas.width - gap * (bars - 1)) / bars;
      for (let index = 0; index < bars; index += 1) {
        const sample = values[Math.floor((index * values.length) / bars)] ?? 0;
        const height = Math.max(3, (sample / 255) * canvas.height * 0.88);
        context.fillStyle = "#6d69f5";
        context.fillRect(index * (width + gap), (canvas.height - height) / 2, width, height);
      }
      animationRef.current = requestAnimationFrame(render);
    };
    render();
  }

  async function startRecording() {
    setError("");
    onRecording(null);
    setElapsed(0);
    elapsedBeforePauseRef.current = 0;
    discardRef.current = false;
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        throw new Error("Audio recording is not supported in this browser. Try a recent version of Chrome, Edge, or Safari.");
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 128;
      audioContext.createMediaStreamSource(stream).connect(analyser);
      const context = canvasRef.current?.getContext("2d");
      if (context) drawLevel(analyser, context);

      const mimeType = ["audio/webm;codecs=opus", "audio/mp4", "audio/webm", "audio/ogg;codecs=opus"]
        .find((candidate) => MediaRecorder.isTypeSupported(candidate));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        stopVisuals();
        stream.getTracks().forEach((track) => track.stop());
        void audioContext.close();
        audioContextRef.current = null;
        streamRef.current = null;
        setStatus("idle");
        if (discardRef.current) {
          chunksRef.current = [];
          discardRef.current = false;
          return;
        }
        const type = recorder.mimeType || "audio/webm";
        const extension = type.includes("mp4") ? "m4a" : type.includes("ogg") ? "ogg" : "webm";
        const file = new File(chunksRef.current, `voice-recording.${extension}`, { type });
        if (!file.size) {
          setError("No audio was captured. Please check your microphone and try again.");
          return;
        }
        onRecording(file);
        chunksRef.current = [];
      };

      startedAtRef.current = Date.now();
      recorder.start(250);
      setStatus("recording");
      timerRef.current = setInterval(() => {
        const duration = Math.min(
          MAX_AUDIO_SECONDS,
          elapsedBeforePauseRef.current + Math.floor((Date.now() - startedAtRef.current) / 1000),
        );
        setElapsed(duration);
      }, 200);
      timeoutRef.current = setTimeout(() => {
        if (recorder.state !== "inactive") recorder.stop();
      }, MAX_AUDIO_SECONDS * 1000);
    } catch (recordingError) {
      stopVisuals();
      streamRef.current?.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      const errorName = recordingError instanceof DOMException ? recordingError.name : "";
      if (audioContextRef.current) {
        void audioContextRef.current.close();
        audioContextRef.current = null;
      }
      const message = errorName === "NotAllowedError" || errorName === "SecurityError"
        ? "Microphone permission was denied. Allow microphone access in your browser settings and try again."
        : errorName === "NotFoundError"
          ? "No microphone was found. Connect a microphone or upload an audio file instead."
          : recordingError instanceof Error
            ? recordingError.message
            : "The microphone could not be started.";
      setError(message);
      setStatus("idle");
    }
  }

  function pauseRecording() {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state !== "recording") return;
    elapsedBeforePauseRef.current += (Date.now() - startedAtRef.current) / 1000;
    recorder.pause();
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setElapsed(Math.floor(elapsedBeforePauseRef.current));
    setStatus("paused");
  }

  function resumeRecording() {
    const recorder = recorderRef.current;
    if (!recorder || recorder.state !== "paused") return;
    startedAtRef.current = Date.now();
    recorder.resume();
    setStatus("recording");
    timerRef.current = setInterval(() => {
      setElapsed(Math.min(
        MAX_AUDIO_SECONDS,
        Math.floor(elapsedBeforePauseRef.current + (Date.now() - startedAtRef.current) / 1000),
      ));
    }, 200);
    timeoutRef.current = setTimeout(() => {
      if (recorder.state !== "inactive") recorder.stop();
    }, Math.max(0, MAX_AUDIO_SECONDS - elapsedBeforePauseRef.current) * 1000);
  }

  function stopRecording() {
    if (recorderRef.current?.state !== "inactive") recorderRef.current?.stop();
  }

  function discardRecording() {
    onRecording(null);
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      discardRef.current = true;
      recorderRef.current.stop();
    }
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (audioContextRef.current) {
      void audioContextRef.current.close();
      audioContextRef.current = null;
    }
    stopVisuals();
    setElapsed(0);
    setStatus("idle");
  }

  useEffect(() => () => {
    stopVisuals();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    if (audioContextRef.current) void audioContextRef.current.close();
  }, []);

  return (
    <div className="recorder">
      <div className="recorder-display">
        <span className={`record-indicator${status === "recording" ? " live" : ""}`} aria-hidden="true" />
        <span className="recorder-time" aria-live="off">{formatTime(elapsed)}</span>
        <span className="recorder-limit">/ 00:30</span>
      </div>
      <canvas aria-label="Microphone input level" className="level-meter" height="46" ref={canvasRef} width="340" />
      <p className="recorder-caption" aria-live="polite">
        {status === "recording" ? "Recording · speak naturally" : status === "paused" ? "Recording paused" : "Your recording is limited to 30 seconds"}
      </p>
      <div className="recorder-actions">
        {status === "idle" ? (
          <button className="button button-primary" disabled={disabled} onClick={() => void startRecording()} type="button">
            <span aria-hidden="true">●</span> Start recording
          </button>
        ) : (
          <>
            {status === "recording" ? (
              <button className="button button-quiet" onClick={pauseRecording} type="button">Pause</button>
            ) : (
              <button className="button button-quiet" onClick={resumeRecording} type="button">Resume</button>
            )}
            <button className="button button-primary" onClick={stopRecording} type="button">Stop</button>
            <button className="button button-quiet" onClick={discardRecording} type="button">Discard</button>
          </>
        )}
      </div>
      {error && <p className="field-error" role="alert">{error}</p>}
    </div>
  );
}
