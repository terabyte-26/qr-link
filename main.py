import io
import json
from pathlib import Path

import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

MANIFEST_PATH = Path(__file__).parent / "manifest.json"


def load_manifest():
    if not MANIFEST_PATH.exists():
        return {"venues": []}
    return json.loads(MANIFEST_PATH.read_text())


@app.route("/")
def index():
    manifest = load_manifest()
    return render_template("index.html", venues=manifest["venues"])


@app.route("/qr")
def qr():
    target = request.host_url
    img = qrcode.make(target)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name="invite-qr.png")


if __name__ == "__main__":
    app.run(debug=True)
