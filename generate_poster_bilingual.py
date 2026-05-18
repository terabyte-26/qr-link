#!/usr/bin/env python3
"""Generate a bilingual (FR primary / EN secondary) A4 poster PDF."""
import io
from pathlib import Path

import fitz
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from PIL import Image, ImageDraw

SITE_URL = "https://altarys-projects.vercel.app/"
URL_DISPLAY = "altarys-projects.vercel.app"

BRAND_BURGUNDY = (112, 32, 16)
BRAND_CREAM = (240, 224, 192)
PAGE_BG = (243, 230, 203)
BRAND_TAUPE = (138, 110, 84)

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT / "static" / "altaris_logo.png"
OUT_PATH = ROOT / "altarys-poster-a4-fr-en.pdf"


def _logo_with_padding() -> Image.Image:
    logo = Image.open(LOGO_PATH).convert("RGBA")
    radius = int(min(logo.size) * 0.14)
    mask = Image.new("L", logo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, logo.size[0], logo.size[1]), radius=radius, fill=255
    )
    logo.putalpha(mask)
    pad = int(max(logo.size) * 0.35)
    canvas = Image.new("RGBA", (logo.width + 2 * pad, logo.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(logo, (pad, pad), logo)
    return canvas


def build_qr_png(url: str) -> bytes:
    code = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    code.add_data(url)
    code.make(fit=True)
    img = code.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=BRAND_CREAM, front_color=BRAND_BURGUNDY),
        embeded_image=_logo_with_padding(),
    )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def norm(rgb):
    return tuple(c / 255 for c in rgb)


def draw_centered_text(page, text, y, fontname, fontsize, color, page_w):
    w = fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)
    page.insert_text(
        fitz.Point((page_w - w) / 2, y),
        text,
        fontname=fontname, fontsize=fontsize, color=color,
    )


def main():
    page_w, page_h = 595.276, 841.890

    doc = fitz.open()
    page = doc.new_page(width=page_w, height=page_h)

    page.draw_rect(
        fitz.Rect(0, 0, page_w, page_h),
        color=None, fill=norm(PAGE_BG),
    )

    # --- Logo ---
    logo_w = 110
    logo_h = logo_w * (452 / 465)
    logo_x = (page_w - logo_w) / 2
    logo_y = 55
    page.insert_image(
        fitz.Rect(logo_x, logo_y, logo_x + logo_w, logo_y + logo_h),
        filename=str(LOGO_PATH),
        keep_proportion=True,
    )

    # --- Headlines (FR primary, EN secondary) ---
    fr_headline_y = logo_y + logo_h + 50
    draw_centered_text(page, "DÉCOUVREZ NOS PROJETS",
                       fr_headline_y, "hebo", 22, norm(BRAND_BURGUNDY), page_w)

    en_headline_y = fr_headline_y + 19
    draw_centered_text(page, "Discover our projects",
                       en_headline_y, "helv", 12, norm(BRAND_TAUPE), page_w)

    # Decorative line
    line_y = en_headline_y + 12
    page.draw_line(
        fitz.Point(page_w / 2 - 40, line_y),
        fitz.Point(page_w / 2 + 40, line_y),
        color=norm(BRAND_BURGUNDY), width=0.8,
    )

    # --- QR Code ---
    qr_bytes = build_qr_png(SITE_URL)
    qr_size = 340
    qr_x = (page_w - qr_size) / 2
    qr_y = line_y + 25
    page.insert_image(
        fitz.Rect(qr_x, qr_y, qr_x + qr_size, qr_y + qr_size),
        stream=qr_bytes, keep_proportion=True,
    )

    # --- Call to action (FR primary, EN secondary) ---
    fr_cta_y = qr_y + qr_size + 38
    draw_centered_text(page, "SCANNEZ AVEC VOTRE TÉLÉPHONE",
                       fr_cta_y, "hebo", 16, norm(BRAND_BURGUNDY), page_w)

    en_cta_y = fr_cta_y + 18
    draw_centered_text(page, "Scan with your phone",
                       en_cta_y, "helv", 12, norm(BRAND_TAUPE), page_w)

    # FR sub-line (italic) + EN sub
    fr_sub_y = en_cta_y + 22
    draw_centered_text(page, "Ouvrez votre appareil photo et pointez-le sur le code",
                       fr_sub_y, "heit", 11, norm(BRAND_TAUPE), page_w)

    en_sub_y = fr_sub_y + 14
    draw_centered_text(page, "Open your camera and point it at the code",
                       en_sub_y, "heit", 10, norm(BRAND_TAUPE), page_w)

    # --- Fallback URL ---
    draw_centered_text(page, URL_DISPLAY,
                       page_h - 40, "helv", 10, norm(BRAND_TAUPE), page_w)

    doc.save(str(OUT_PATH))
    doc.close()
    print(f"Saved: {OUT_PATH}")
    print(f"Size: {OUT_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
