from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from ai_models.image_engine import enhance_image, generate_image, remove_background
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def upload_file(field="image"):
    file = request.files.get(field)
    if not file or file.filename == "":
        return None, ("No image was uploaded.", 400)
    if not allowed_file(file.filename):
        return None, ("Supported files: PNG, JPG, JPEG, WEBP.", 400)
    filename = secure_filename(file.filename)
    path = Path(app.config["UPLOAD_FOLDER"]) / filename
    path = path.with_name(f"upload-{Path(filename).stem}-{Path(filename).suffix}")
    file.save(path)
    return path, None


@app.route("/")
def home():
    return render_template("index.html", site_url=app.config["SITE_URL"])


@app.route("/login")
def login():
    return render_template("auth.html", mode="login")


@app.route("/register")
def register():
    return render_template("auth.html", mode="register")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
    path, engine = generate_image(
        prompt=prompt,
        negative_prompt=data.get("negative_prompt", ""),
        style=data.get("style", "realistic"),
        ratio=data.get("ratio", "1:1"),
        output_dir=app.config["UPLOAD_FOLDER"],
        config=Config,
    )
    return jsonify({"url": url_for("static", filename=f"uploads/{path.name}"), "engine": engine})


@app.route("/api/enhance", methods=["POST"])
def api_enhance():
    input_path, error = upload_file()
    if error:
        return jsonify({"error": error[0]}), error[1]
    target = request.form.get("target", "2k")
    options = {
        "denoise": request.form.get("denoise") == "true",
        "faces": request.form.get("faces") == "true",
        "restore": request.form.get("restore") == "true",
    }
    result, engine = enhance_image(input_path, target, options, app.config["UPLOAD_FOLDER"])
    return jsonify({
        "original": url_for("static", filename=f"uploads/{input_path.name}"),
        "url": url_for("static", filename=f"uploads/{result.name}"),
        "engine": engine,
    })


@app.route("/api/remove-background", methods=["POST"])
def api_background():
    input_path, error = upload_file()
    if error:
        return jsonify({"error": error[0]}), error[1]
    result, engine = remove_background(input_path, app.config["UPLOAD_FOLDER"])
    return jsonify({
        "original": url_for("static", filename=f"uploads/{input_path.name}"),
        "url": url_for("static", filename=f"uploads/{result.name}"),
        "engine": engine,
    })


@app.route("/api/auth", methods=["POST"])
def api_auth():
    payload = request.get_json(force=True)
    return jsonify({
        "ok": True,
        "message": f"{payload.get('mode', 'login').title()} demo accepted. Connect OAuth/SMTP in production.",
        "user": {"name": payload.get("name") or "Studio User", "plan": "Pro Trial"},
    })


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(app.root_path, "sitemap.xml", mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.root_path, "robots.txt", mimetype="text/plain")


@app.errorhandler(404)
def not_found(_):
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
