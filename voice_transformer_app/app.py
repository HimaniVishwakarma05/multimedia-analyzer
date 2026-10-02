import os
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile

from voice_cloning import clone_voice, synthesize_text

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/convert", methods=["POST"])
def convert_voice():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided."}), 400

    uploaded = request.files["audio"]
    if uploaded.filename == "":
        return jsonify({"error": "No selected file."}), 400

    voice_slug = request.form.get("voiceSlug") or "warm-narrator"
    voice_id = {
        "warm-narrator": "EXAVITQu4vr4xnSDxMaL",
        "deep-studio": "JBFqnCBsd6RMkjVDRZzb",
        "bright-conversational": "EXAVITQu4vr4xnSDxMaL",
    }.get(voice_slug, "EXAVITQu4vr4xnSDxMaL")

    original_name = secure_filename(uploaded.filename)
    temp_dir = tempfile.mkdtemp(prefix="voice_transformer_")
    temp_audio_path = os.path.join(temp_dir, original_name)
    uploaded.save(temp_audio_path)

    try:
        result = synthesize_text(
            text="Converted voice preview",
            voice_id=voice_id,
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            output_path=os.path.join(temp_dir, "converted_output.mp3"),
        )
        return send_file(result["output_path"], mimetype="audio/mpeg", as_attachment=False)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
