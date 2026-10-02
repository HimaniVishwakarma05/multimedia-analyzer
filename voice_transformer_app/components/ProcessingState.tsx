export function ProcessingState() {
  return (
    <div aria-live="polite" className="processing-state" role="status">
      <span className="processing-orbit" aria-hidden="true"><span /></span>
      <div>
        <strong>Processing your audio with AI...</strong>
        <p>Your audio is being securely sent to ElevenLabs for transformation.</p>
      </div>
    </div>
  );
}
