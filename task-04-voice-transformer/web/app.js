const fileInput = document.querySelector("#audio-file");
const recordButton = document.querySelector("#record-button");
const stopButton = document.querySelector("#stop-button");
const transformButton = document.querySelector("#transform-button");
const permission = document.querySelector("#permission");
const voiceSelect = document.querySelector("#voice");
const statusText = document.querySelector("#status");
const originalPlayer = document.querySelector("#original-player");
const resultPanel = document.querySelector("#result-panel");
const resultPlayer = document.querySelector("#result-player");
const downloadLink = document.querySelector("#download-link");

let recorder;
let recordingChunks = [];
let recordedFile;
let originalUrl;
let resultUrl;
let recordingTimer;

function showStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
}

function selectedFile() {
  return recordedFile || fileInput.files?.[0] || null;
}

function setSourcePreview(file) {
  if (originalUrl) URL.revokeObjectURL(originalUrl);
  originalUrl = URL.createObjectURL(file);
  originalPlayer.src = originalUrl;
  originalPlayer.hidden = false;
  recordedFile = file;
  showStatus(`Ready: ${file.name}`);
}

fileInput.addEventListener("change", () => {
  recordedFile = null;
  const file = fileInput.files?.[0];
  if (file) setSourcePreview(file);
});

recordButton.addEventListener("click", async () => {
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    showStatus("Microphone recording is not supported in this browser.", true);
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    recordingChunks = [];
    recorder.addEventListener("dataavailable", (event) => {
      if (event.data.size) recordingChunks.push(event.data);
    });
    recorder.addEventListener("stop", () => {
      stream.getTracks().forEach((track) => track.stop());
      clearTimeout(recordingTimer);
      const blob = new Blob(recordingChunks, { type: recorder.mimeType || "audio/webm" });
      const extension = blob.type.includes("ogg") ? "ogg" : "webm";
      setSourcePreview(new File([blob], `recording.${extension}`, { type: blob.type }));
      recordButton.disabled = false;
      stopButton.disabled = true;
    }, { once: true });
    recorder.start();
    recordButton.disabled = true;
    stopButton.disabled = false;
    showStatus("Recording… it will stop automatically after 30 seconds.");
    recordingTimer = setTimeout(() => {
      if (recorder?.state === "recording") recorder.stop();
    }, 30_000);
  } catch {
    showStatus("Microphone access was denied or unavailable.", true);
  }
});

stopButton.addEventListener("click", () => {
  if (recorder?.state === "recording") recorder.stop();
});

transformButton.addEventListener("click", async () => {
  const file = selectedFile();
  if (!file) {
    showStatus("Choose a file or record audio first.", true);
    return;
  }
  if (!permission.checked) {
    showStatus("Confirm permission to use this recording before continuing.", true);
    return;
  }
  if (file.size === 0 || file.size > 15 * 1024 * 1024) {
    showStatus("Choose a non-empty audio file no larger than 15 MB.", true);
    return;
  }
  if (!voiceSelect.value || voiceSelect.selectedOptions[0].disabled) {
    showStatus("Choose a configured target voice. Add its voice ID to .env first.", true);
    return;
  }

  const formData = new FormData();
  formData.append("audio", file, file.name);
  formData.append("voice", voiceSelect.value);
  formData.append("permission", "yes");
  transformButton.disabled = true;
  showStatus("Transforming audio… this can take a minute.");
  try {
    const response = await fetch("/api/transform", { method: "POST", body: formData });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new Error(body.error || `Transformation failed (HTTP ${response.status}).`);
    }
    const blob = await response.blob();
    if (!blob.size) throw new Error("The voice service returned an empty audio file.");
    if (resultUrl) URL.revokeObjectURL(resultUrl);
    resultUrl = URL.createObjectURL(blob);
    resultPlayer.src = resultUrl;
    downloadLink.href = resultUrl;
    resultPanel.hidden = false;
    showStatus("Transformation complete.");
  } catch (error) {
    showStatus(error instanceof Error ? error.message : "Transformation failed.", true);
  } finally {
    transformButton.disabled = false;
  }
});

window.addEventListener("beforeunload", () => {
  if (originalUrl) URL.revokeObjectURL(originalUrl);
  if (resultUrl) URL.revokeObjectURL(resultUrl);
});
