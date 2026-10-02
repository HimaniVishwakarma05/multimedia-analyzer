"use client";

import { useEffect, useRef } from "react";

type AudioResultProps = {
  originalUrl: string;
  originalName: string;
  transformedUrl: string;
  downloadName: string;
};

export function AudioResult({ originalUrl, originalName, transformedUrl, downloadName }: AudioResultProps) {
  const originalPlayer = useRef<HTMLAudioElement>(null);
  const transformedPlayer = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const original = originalPlayer.current;
    const transformed = transformedPlayer.current;
    if (!original || !transformed) return;
    const pauseTransformed = () => transformed.pause();
    const pauseOriginal = () => original.pause();
    original.addEventListener("play", pauseTransformed);
    transformed.addEventListener("play", pauseOriginal);
    return () => {
      original.removeEventListener("play", pauseTransformed);
      transformed.removeEventListener("play", pauseOriginal);
    };
  }, []);

  return (
    <div className="result-card">
      <div className="result-heading">
        <div>
          <span className="eyebrow">YOUR TRANSFORMATION</span>
          <h3>Listen & compare</h3>
        </div>
        <span className="result-badge"><span aria-hidden="true">✓</span> Ready</span>
      </div>
      <div className="audio-comparison">
        <div className="audio-track">
          <div className="track-label">
            <span className="track-icon original-icon" aria-hidden="true">↗</span>
            <div><strong>Original audio</strong><span>{originalName}</span></div>
          </div>
          <audio controls preload="metadata" ref={originalPlayer} src={originalUrl}>Your browser does not support audio playback.</audio>
        </div>
        <div className="audio-track transformed-track">
          <div className="track-label">
            <span className="track-icon transformed-icon" aria-hidden="true">✦</span>
            <div><strong>Transformed audio</strong><span>MP3 · 44.1 kHz · 128 kbps</span></div>
          </div>
          <audio controls preload="metadata" ref={transformedPlayer} src={transformedUrl}>Your browser does not support audio playback.</audio>
        </div>
      </div>
      <a className="button button-primary download-button" download={downloadName} href={transformedUrl}>
        <span aria-hidden="true">↓</span> Download MP3
      </a>
      <p className="result-note">Play one track at a time to compare the performance. Your audio is not saved after this page is closed.</p>
    </div>
  );
}
