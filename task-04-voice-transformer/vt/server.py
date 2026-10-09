from io import BytesIO

from flask import Flask, render_template, request, send_file

from vt.audio_validation import AudioValidationError
from vt.config import MAX_MULTIPART_BYTES
from vt.providers import ProviderError
from vt.service import transform_upload
from vt.voices import available_voices


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../web",
        static_folder="../web",
        static_url_path="/static",
    )
    app.config["MAX_CONTENT_LENGTH"] = MAX_MULTIPART_BYTES

    @app.get("/")
    def index():
        return render_template("index.html", voices=available_voices())

    @app.post("/api/transform")
    def transform():
        if request.form.get("permission") != "yes":
            return {"error": "Confirm that you have permission to use this recording."}, 400

        audio = request.files.get("audio")
        voice_slug = request.form.get("voice", "")
        if audio is None or not audio.filename:
            return {"error": "Choose or record an audio file."}, 400
        voices = available_voices()
        if not any(voice["slug"] == voice_slug for voice in voices):
            return {"error": "Choose a valid target voice."}, 400

        try:
            audio_bytes = audio.read()
            result = transform_upload(
                audio.filename,
                audio_bytes,
                audio.mimetype or "",
                voice_slug,
            )
        except AudioValidationError as error:
            return {"error": str(error)}, 400
        except ValueError as error:
            return {"error": str(error)}, 503
        except ProviderError as error:
            return {"error": str(error)}, 502

        return send_file(
            BytesIO(result),
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="transformed-voice.mp3",
            max_age=0,
        )

    @app.errorhandler(413)
    def request_too_large(_):
        return {"error": "Upload size exceeds the 15 MB audio limit."}, 413

    return app
