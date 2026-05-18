import io
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

LOGO_PATH = Path(__file__).parent / "altaris_logo.png"

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
    code = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    code.add_data(target)
    code.make(fit=True)
    kwargs = {
        "image_factory": StyledPilImage,
        "module_drawer": RoundedModuleDrawer(),
    }
    if LOGO_PATH.exists():
        kwargs["embeded_image_path"] = str(LOGO_PATH)
    img = code.make_image(**kwargs)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", download_name="invite-qr.png")


if __name__ == "__main__":
    app.run(debug=True)
