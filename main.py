import io

import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

VENUES = sorted([
    ("5TH AVENUE",         "https://drive.google.com/drive/folders/1BJ8QZPu-u0tpV2ArlWAOqyAdgn-MGFOH?usp=sharing"),
    ("ALHAMBRA",           "https://drive.google.com/drive/folders/1gD5cAlFrOX6_AonIYX7ltFfQu5GsG38r?usp=sharing"),
    ("CRYSTAL GARDEN",     "https://drive.google.com/drive/folders/1i471jjlEHHIrDl57PcvPTFcyk7d6DIl-?usp=sharing"),
    ("DA VINCI",           "https://drive.google.com/drive/folders/1G5f8EAF2VN505sLx4puzTCr6k4UUmVD0?usp=sharing"),
    ("JARDIN DE BALI",     "https://drive.google.com/drive/folders/1afnWP_A1DKAy7h5oXohdCYzXjRdljbnm?usp=sharing"),
    ("LES JARDINS BLANCS", "https://drive.google.com/drive/folders/1GqMgXyDjt3o1z8UG29mSHIH6heWuOji7?usp=sharing"),
    ("LITTLE MOUNTAIN",    "https://drive.google.com/drive/folders/1_eZ2eyvcFKyep8UDbJBdPi9orFnFLu4D?usp=sharing"),
    ("M ROAD PARK",        "https://drive.google.com/drive/folders/1SyVNcCwyMfMaWXJWD8FBomggVuwiNtbZ?usp=sharing"),
    ("TRIANGLE",           "https://drive.google.com/drive/folders/1GxFAEsGijb3Aa_shUiGpWAOWqvuVHpvV?usp=sharing"),
])


@app.route("/")
def index():
    return render_template("index.html", venues=VENUES)


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
