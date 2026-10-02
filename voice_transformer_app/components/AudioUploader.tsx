"use client";

import { useRef, useState } from "react";
import { inspectAudioFile } from "@/lib/client-audio-validation";

type AudioUploaderProps = {
  onFileSelected: (file: File, duration: number) => void;
  disabled?: boolean;
};

export function AudioUploader({ onFileSelected, disabled }: AudioUploaderProps) {
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file?: File) {
    if (!file) return;
    setError("");
    try {
      const duration = await inspectAudioFile(file);
      onFileSelected(file, duration);
    } catch (validationError) {
      setError(validationError instanceof Error ? validationError.message : "Could not read this audio file.");
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div>
      <button
        className="upload-dropzone"
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          void handleFile(event.dataTransfer.files[0]);
        }}
        type="button"
      >
        <span className="upload-icon" aria-hidden="true">↥</span>
        <span className="upload-title">Drop an audio file here, or browse</span>
        <span className="upload-subtitle">MP3, WAV, M4A, OGG, FLAC or WebM · up to 15 MB · 30 seconds max</span>
      </button>
      <input
        accept=".mp3,.wav,.m4a,.ogg,.oga,.flac,.webm,audio/mpeg,audio/wav,audio/mp4,audio/ogg,audio/flac,audio/webm"
        className="visually-hidden"
        disabled={disabled}
        onChange={(event) => void handleFile(event.target.files?.[0])}
        ref={inputRef}
        type="file"
      />
      {error && <p className="field-error" role="alert">{error}</p>}
    </div>
  );
}
