import io
import unittest
from unittest.mock import patch

from vt.server import create_app


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Voice Transformer", response.data)

    def test_transform_requires_permission_confirmation(self):
        response = self.client.post(
            "/api/transform",
            data={"voice": "warm-narrator"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("permission", response.json["error"])

    @patch("vt.server.transform_upload", return_value=b"generated mp3")
    @patch.dict(
        "os.environ",
        {"ELEVENLABS_VOICE_WARM_ID": "synthetic-voice-id"},
        clear=False,
    )
    def test_transform_returns_audio_without_saving_it(self, transform):
        response = self.client.post(
            "/api/transform",
            data={
                "permission": "yes",
                "voice": "warm-narrator",
                "audio": (io.BytesIO(b"short audio"), "clip.wav", "audio/wav"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "audio/mpeg")
        self.assertEqual(response.data, b"generated mp3")
        transform.assert_called_once()


if __name__ == "__main__":
    unittest.main()
