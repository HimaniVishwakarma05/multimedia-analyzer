"use client";

import { useEffect, useRef, useState } from "react";
import { AudioResult } from "@/components/AudioResult";
import { AudioUploader } from "@/components/AudioUploader";
import { ProcessingState } from "@/components/ProcessingState";
import { VoiceRecorder } from "@/components/VoiceRecorder";
import { inspectAudioFile } from "@/lib/client-audio-validation";
import { VoiceSelector } from "@/components/VoiceSelector";
import type { VoiceSlug } from "@/lib/config";

type InputMode = "record" | "upload";

export default function Home() {
  const [inputMode, setInputMode] = useState<InputMode>("record");
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [duration, setDuration] = useState<number | null>(null);
  const [selectedVoice, setSelectedVoice] = useState<VoiceSlug | null>(null);
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [transformedUrl, setTransformedUrl] = useState("");
  const originalUrlRef = useRef("");
  const transformedUrlRef = useRef("");
  const [originalUrl, setOriginalUrl] = useState("");

  function clearResult() {
    if (transformedUrlRef.current) URL.revokeObjectURL(transformedUrlRef.current);
    transformedUrlRef.current = "";
    setTransformedUrl("");
  }

  function resetInput() {
    setAudioFile(null);
    setDuration(null);
    setError("");
    setConsent(false);
    clearResult();
  }

  function setSource(file: File | null, actualDuration?: number) {
    if (originalUrlRef.current) URL.revokeObjectURL(originalUrlRef.current);
    originalUrlRef.current = file ? URL.createObjectURL(file) : "";
    setOriginalUrl(originalUrlRef.current);
    setAudioFile(file);
    setDuration(actualDuration ?? null);
    setError("");
    clearResult();
  }

  async function setRecording(file: File | null) {
    if (!file) {
      setSource(null);
      return;
    }
    try {
      const length = await inspectAudioFile(file);
      setSource(file, length);
    } catch (validationError) {
      setSource(null);
      setError(validationError instanceof Error ? validationError.message : "The recording could not be validated.");
    }
  }

  useEffect(() => () => {
    if (originalUrlRef.current) URL.revokeObjectURL(originalUrlRef.current);
    if (transformedUrlRef.current) URL.revokeObjectURL(transformedUrlRef.current);
  }, []);

  async function transformVoice() {
    if (!audioFile) {
      setError("Please record or upload an audio file.");
      return;
    }
    if (!selectedVoice) {
      setError("Choose one of the available synthetic voices.");
      return;
    }
    if (!consent) {
      setError("Confirm you have permission to use this recording.");
      return;
    }

    setBusy(true);
    setError("");
    clearResult();

    const formData = new FormData();
    formData.append("audio", audioFile, audioFile.name);
    formData.append("voiceSlug", selectedVoice);

    try {
      const response = await fetch("/api/convert", { method: "POST", body: formData });
      if (!response.ok) {
        const result: unknown = await response.json().catch(() => null);
        const message = typeof result === "object" && result !== null && "error" in result &&
          typeof result.error === "string"
          ? result.error
          : "Something went wrong while transforming your voice.";
        throw new Error(message);
      }
      const audio = await response.blob();
      if (!audio.size) throw new Error("The AI voice service returned an empty audio file.");
      const url = URL.createObjectURL(audio);
      transformedUrlRef.current = url;
      setTransformedUrl(url);
    } catch (conversionError) {
      setError(conversionError instanceof Error
        ? conversionError.message
        : "Something went wrong while transforming your voice.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="site-shell">
      <header className="topbar">
        <a aria-label="Voiceform home" className="brand" href="#">
          <span className="brand-mark" aria-hidden="true"><span /><span /><span /><span /><span /></span>
          <span>voiceform<span className="brand-period">.</span></span>
        </a>
        <div className="topbar-tag"><span /> PRIVATE BY DESIGN</div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow hero-eyebrow">SPEECH-TO-SPEECH STUDIO</span>
          <h1>Your voice.<br /><span>A new perspective.</span></h1>
          <p>Transform your voice into a different AI-generated voice while preserving your speech performance.</p>
          <div className="hero-footnote"><span aria-hidden="true">✳</span> English · Hindi · Hinglish</div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="hero-orbit orbit-one" />
          <div className="hero-orbit orbit-two" />
          <div className="hero-sun"><span>V</span></div>
          <span className="hero-spark spark-one">✳</span>
          <span className="hero-spark spark-two">✦</span>
          <span className="hero-caption">VOICE<br />IN MOTION</span>
        </div>
      </section>

      <div className="studio-layout">
        <div className="workflow-column">
          <section aria-labelledby="audio-step-title" className="step-card">
            <div className="step-heading">
              <span className="step-number">01</span>
              <div><h2 id="audio-step-title">Bring your voice</h2><p>Start with a recording or upload a clip.</p></div>
            </div>
            <div className="mode-tabs" role="tablist" aria-label="Audio input method">
              <button
                aria-selected={inputMode === "record"}
                className={`mode-tab${inputMode === "record" ? " active" : ""}`}
                disabled={busy}
                onClick={() => { setInputMode("record"); resetInput(); }}
                role="tab"
                type="button"
              >
                <span aria-hidden="true">◉</span> Record voice
              </button>
              <button
                aria-selected={inputMode === "upload"}
                className={`mode-tab${inputMode === "upload" ? " active" : ""}`}
                disabled={busy}
                onClick={() => { setInputMode("upload"); resetInput(); }}
                role="tab"
                type="button"
              >
                <span aria-hidden="true">↥</span> Upload audio
              </button>
            </div>
            <div className="input-panel" role="tabpanel">
              {inputMode === "record"
                ? <VoiceRecorder disabled={busy} onRecording={(file) => void setRecording(file)} />
                : <AudioUploader disabled={busy} onFileSelected={(file, length) => setSource(file, length)} />}
            </div>
            {audioFile && originalUrl && (
              <div className="source-preview">
                <div className="preview-heading"><span className="preview-dot" /><div><strong>{audioFile.name}</strong><span>{duration !== null ? `${duration.toFixed(1)} sec · ` : ""}{(audioFile.size / (1024 * 1024)).toFixed(2)} MB</span></div></div>
                <audio aria-label="Preview original audio" controls preload="metadata" src={originalUrl}>Audio preview is not supported in this browser.</audio>
                <button className="text-button" disabled={busy} onClick={() => setSource(null)} type="button">Remove recording</button>
              </div>
            )}
          </section>

          <section aria-labelledby="voice-step-title" className="step-card">
            <div className="step-heading">
              <span className="step-number">02</span>
              <div><h2 id="voice-step-title">Choose your new voice</h2><p>Pick a developer-controlled synthetic style.</p></div>
            </div>
            <VoiceSelector disabled={busy} onSelect={(slug) => { setSelectedVoice(slug); setError(""); clearResult(); }} selectedVoice={selectedVoice} />
          </section>
        </div>

        <aside className="transform-panel">
          <div className="panel-topline"><span className="eyebrow">READY WHEN YOU ARE</span><span className="panel-dot" /></div>
          <div className="transform-illustration" aria-hidden="true">
            <div className="transform-ring ring-back" />
            <div className="transform-ring ring-front" />
            <span className="transform-symbol">↝</span>
            <span className="transform-glint">✦</span>
          </div>
          <h2>Keep the feeling.<br />Change the voice.</h2>
          <p className="transform-copy">Your words, timing, pauses, and delivery stay yours. Only the perceived voice changes.</p>
          <label className="consent-row">
            <input checked={consent} disabled={busy} onChange={(event) => { setConsent(event.target.checked); setError(""); }} type="checkbox" />
            <span>I have permission to use this recording and am not impersonating someone without their consent.</span>
          </label>
          <button className="button button-transform" disabled={busy || !audioFile || !selectedVoice || !consent} onClick={() => void transformVoice()} type="button">
            {busy ? <><span className="button-spinner" /> Transforming...</> : <>Transform voice <span aria-hidden="true">↗</span></>}
          </button>
          {error && <p className="form-error" role="alert">{error}</p>}
          <div className="privacy-note"><span aria-hidden="true">◈</span><p><strong>Your audio stays yours.</strong><br />Processed by ElevenLabs for this request only. Never stored by this app.</p></div>
        </aside>
      </div>

      {busy && <ProcessingState />}
      {transformedUrl && originalUrl && (
        <section aria-label="Transformation result" className="result-section">
          <AudioResult
            downloadName={`transformed-${audioFile?.name.replace(/\.[^.]+$/, "") || "voice"}.mp3`}
            originalName={audioFile?.name ?? "Original recording"}
            originalUrl={originalUrl}
            transformedUrl={transformedUrl}
          />
        </section>
      )}

      <section className="privacy-banner">
        <span className="privacy-shield" aria-hidden="true">◈</span>
        <div><strong>Built with consent. Designed for privacy.</strong><p>Only transform audio you have permission to use. We do not support unauthorized voice cloning or real-person impersonation. Audio is sent directly to ElevenLabs and is not permanently stored by this app.</p></div>
        <span className="language-pill">EN · HI · HINGLISH</span>
      </section>

      <footer className="site-footer">
        <span>VOICEFORM<span className="brand-period">.</span> <span className="footer-muted">MCA Multimedia Project</span></span>
        <span>Speech-to-speech · Powered by ElevenLabs</span>
      </footer>
    </main>
  );
}
