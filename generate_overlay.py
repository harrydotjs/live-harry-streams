import os
import sys
from PIL import Image, ImageDraw, ImageFont

def get_font(size, bold=False):
    # Try finding system fonts on Ubuntu / Linux / Windows
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\seguiemj.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_stream_overlay(output_path="overlay.png", width=1080, height=1920):
    """
    Creates a crystal-clear 1080x1920 transparent PNG overlay containing the
    LIVE indicator badge and LIKE/SUBSCRIBE badges in the top margin (y=0 to y=420),
    leaving the center 1080x1080 square completely transparent for the video.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        # Fonts
        font_live = get_font(26, bold=True)
        font_cta = get_font(24, bold=True)

        # ── 1. Top-Left: "LIVE" Badge ─────────────────────────────────────
        live_box = [50, 75, 210, 135]
        draw.rounded_rectangle(live_box, radius=12, fill=(255, 0, 68, 255), outline=(255, 255, 255, 140), width=1)
        
        # White pulsing live dot: center (85, 105), radius 7
        draw.ellipse([78, 98, 92, 112], fill=(255, 255, 255, 255))
        
        # "LIVE" text
        draw.text((105, 88), "LIVE", fill=(255, 255, 255, 255), font=font_live)

        # ── 2. Top-Right: "LIKE • SUBSCRIBE" Pill ─────────────────────────
        cta_box = [630, 75, 1030, 135]
        draw.rounded_rectangle(cta_box, radius=30, fill=(14, 18, 34, 245), outline=(255, 51, 102, 230), width=2)

        # Text: "LIKE • SUBSCRIBE"
        draw.text((660, 90), "LIKE", fill=(255, 60, 110, 255), font=font_cta)
        draw.text((740, 90), "•", fill=(255, 255, 255, 180), font=font_cta)
        draw.text((775, 90), "SUBSCRIBE", fill=(255, 204, 0, 255), font=font_cta)
    except Exception as e:
        print(f"[Notice] Text rendering notice (fallback to basic overlay): {e}")

    img.save(output_path, "PNG")
    print(f"[OK] Transparent broadcast overlay generated: {output_path} ({width}x{height})")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "overlay.png"
    create_stream_overlay(out)
