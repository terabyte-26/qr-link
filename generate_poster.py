#!/usr/bin/env python3
"""Generate a printable A4 poster PDF (logo + headline + QR + call-to-action + URL)."""
import io
from pathlib import Path

import fitz  # PyMuPDF
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
OUT_PATH = ROOT / "altarys-poster-a4.pdf"


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


def main():
    # A4 in points: 210mm × 297mm = 595.276 × 841.890
    page_w, page_h = 595.276, 841.890

    doc = fitz.open()
    page = doc.new_page(width=page_w, height=page_h)

    # Page background
    page.draw_rect(
        fitz.Rect(0, 0, page_w, page_h),
        color=None, fill=norm(PAGE_BG),
    )

    # --- Logo (top) ---
    logo_w = 115
    logo_h = logo_w * (452 / 465)
    logo_x = (page_w - logo_w) / 2
    logo_y = 60
    page.insert_image(
        fitz.Rect(logo_x, logo_y, logo_x + logo_w, logo_y + logo_h),
        filename=str(LOGO_PATH),
        keep_proportion=True,
    )

    # --- Headline ---
    headline_text = "DISCOVER OUR PROJECTS"
    headline_size = 22
    headline_y = logo_y + logo_h + 60
    # Measure text width to center manually
    headline_w = fitz.get_text_length(headline_text, fontname="hebo", fontsize=headline_size)
    page.insert_text(
        fitz.Point((page_w - headline_w) / 2, headline_y),
        headline_text,
        fontname="hebo",
        fontsize=headline_size,
        color=norm(BRAND_BURGUNDY),
    )

    # Decorative thin line under headline
    line_y = headline_y + 16
    page.draw_line(
        fitz.Point(page_w / 2 - 40, line_y),
        fitz.Point(page_w / 2 + 40, line_y),
        color=norm(BRAND_BURGUNDY), width=0.8,
    )

    # --- QR Code (center) ---
    qr_bytes = build_qr_png(SITE_URL)
    qr_size = 360
    qr_x = (page_w - qr_size) / 2
    qr_y = line_y + 30
    page.insert_image(
        fitz.Rect(qr_x, qr_y, qr_x + qr_size, qr_y + qr_size),
        stream=qr_bytes,
        keep_proportion=True,
    )

    # --- Call to action ---
    cta_text = "SCAN WITH YOUR PHONE"
    cta_size = 17
    cta_y = qr_y + qr_size + 42
    cta_w = fitz.get_text_length(cta_text, fontname="hebo", fontsize=cta_size)
    page.insert_text(
        fitz.Point((page_w - cta_w) / 2, cta_y),
        cta_text,
        fontname="hebo",
        fontsize=cta_size,
        color=norm(BRAND_BURGUNDY),
    )

    sub_text = "Open your camera and point it at the code"
    sub_size = 11
    sub_y = cta_y + 22
    sub_w = fitz.get_text_length(sub_text, fontname="heit", fontsize=sub_size)
    page.insert_text(
        fitz.Point((page_w - sub_w) / 2, sub_y),
        sub_text,
        fontname="heit",
        fontsize=sub_size,
        color=norm(BRAND_TAUPE),
    )

    # --- Fallback URL at bottom ---
    url_size = 10
    url_w = fitz.get_text_length(URL_DISPLAY, fontname="helv", fontsize=url_size)
    page.insert_text(
        fitz.Point((page_w - url_w) / 2, page_h - 40),
        URL_DISPLAY,
        fontname="helv",
        fontsize=url_size,
        color=norm(BRAND_TAUPE),
    )

    doc.save(str(OUT_PATH))
    doc.close()
    print(f"Saved: {OUT_PATH}")
    print(f"Size: {OUT_PATH.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
