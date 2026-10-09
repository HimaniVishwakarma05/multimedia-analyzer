import io
import wave
import unittest

from vt.audio_validation import AudioValidationError, validate_audio


def wav_bytes(seconds: float = 1.0) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b"\0\0" * int(8000 * seconds))
    return buffer.getvalue()


class AudioValidationTests(unittest.TestCase):
    def test_accepts_short_readable_wav(self):
        self.assertAlmostEqual(validate_audio("clip.wav", wav_bytes(), "audio/wav"), 1.0)

    def test_rejects_empty_audio(self):
        with self.assertRaisesRegex(AudioValidationError, "empty"):
            validate_audio("clip.wav", b"", "audio/wav")

    def test_rejects_wrong_extension(self):
        with self.assertRaisesRegex(AudioValidationError, "Use an MP3"):
            validate_audio("clip.exe", wav_bytes(), "audio/wav")

    def test_rejects_unreadable_audio(self):
        with self.assertRaisesRegex(AudioValidationError, "corrupt or unreadable"):
            validate_audio("clip.wav", b"not a wave file", "audio/wav")

    def test_rejects_audio_longer_than_limit(self):
        with self.assertRaisesRegex(AudioValidationError, "30 seconds"):
            validate_audio("clip.wav", wav_bytes(30.1), "audio/wav")


if __name__ == "__main__":
    unittest.main()
