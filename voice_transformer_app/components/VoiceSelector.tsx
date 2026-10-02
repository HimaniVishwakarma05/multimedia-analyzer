"use client";

import { VOICES, type VoiceSlug } from "@/lib/config";

type VoiceSelectorProps = {
  selectedVoice: VoiceSlug | null;
  onSelect: (slug: VoiceSlug) => void;
  disabled?: boolean;
};

const voiceArt = ["✳", "◒", "✦"];

export function VoiceSelector({ selectedVoice, onSelect, disabled }: VoiceSelectorProps) {
  return (
    <div className="voice-grid">
      {VOICES.map((voice, index) => {
        const selected = selectedVoice === voice.slug;
        return (
          <article className={`voice-card${selected ? " selected" : ""}`} key={voice.slug}>
            <div className={`voice-art voice-art-${index + 1}`} aria-hidden="true">
              {voiceArt[index]}
            </div>
            <div className="voice-card-copy">
              <span className="eyebrow">{voice.style}</span>
              <h3>{voice.name}</h3>
              <p>{voice.description}</p>
              <button
                aria-pressed={selected}
                className={selected ? "button button-selected" : "button button-quiet"}
                disabled={disabled}
                onClick={() => onSelect(voice.slug)}
                type="button"
              >
                {selected ? "Selected ✓" : "Select voice"}
              </button>
            </div>
          </article>
        );
      })}
    </div>
  );
}
