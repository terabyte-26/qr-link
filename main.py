import io
import os

import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
IMAGES_DIR = os.path.join(app.static_folder, "images")


def list_images():
    if not os.path.isdir(IMAGES_DIR):
        return []
    files = [
        f for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith(IMAGE_EXTENSIONS)
    ]
    return sorted(files)


@app.route("/")
def index():
    return render_template("index.html", images=list_images())


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
