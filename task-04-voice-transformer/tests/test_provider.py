import unittest
from unittest.mock import Mock, patch

from vt.providers import ProviderError, transform_audio


class ProviderTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "ELEVENLABS_VOICE_WARM_ID": "synthetic-voice-id",
        },
        clear=False,
    )
    @patch("vt.providers.requests.post")
    def test_sends_speech_to_speech_request(self, post):
        response = Mock(status_code=200, content=b"mp3 bytes")
        post.return_value = response

        result = transform_audio(
            b"input audio",
            "clip.wav",
            "audio/wav",
            "warm-narrator",
            "test-api-key",
        )

        self.assertEqual(result, b"mp3 bytes")
        call = post.call_args
        self.assertIn("/speech-to-speech/synthetic-voice-id", call.args[0])
        self.assertIn("output_format=mp3_44100_128", call.args[0])
        self.assertEqual(call.kwargs["headers"]["xi-api-key"], "test-api-key")
        self.assertEqual(call.kwargs["data"]["model_id"], "eleven_multilingual_sts_v2")
        self.assertEqual(call.kwargs["files"]["audio"][0], "clip.wav")

    @patch.dict(
        "os.environ",
        {
            "ELEVENLABS_VOICE_WARM_ID": "synthetic-voice-id",
        },
        clear=False,
    )
    @patch("vt.providers.requests.post")
    def test_reports_rejected_api_key_without_leaking_provider_body(self, post):
        response = Mock(status_code=401)
        post.return_value = response
        with self.assertRaisesRegex(ProviderError, "rejected the API key"):
            transform_audio(b"audio", "clip.wav", "audio/wav", "warm-narrator", "secret")

    @patch.dict(
        "os.environ",
        {
            "ELEVENLABS_VOICE_WARM_ID": "synthetic-voice-id",
        },
        clear=False,
    )
    @patch("vt.providers.requests.post")
    def test_reports_quota_response(self, post):
        response = Mock(status_code=429)
        post.return_value = response
        with self.assertRaisesRegex(ProviderError, "quota"):
            transform_audio(b"audio", "clip.wav", "audio/wav", "warm-narrator", "secret")


if __name__ == "__main__":
    unittest.main()
