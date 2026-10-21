import sys
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def main():
    if len(sys.argv) < 5:
        print("Usage: composite_panel.py <input_img> <output_img> <title> <sector> [caption]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    title = sys.argv[3].strip()
    sector = sys.argv[4].strip()
    caption = sys.argv[5].strip() if len(sys.argv) > 5 and sys.argv[5].strip() else None

    im = Image.open(input_path).convert("RGB")
    w, h = im.size

    # Fit / Crop to pristine 16:9
    target_ratio = 16.0 / 9.0
    current_ratio = w / float(h)

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))

    # Resize to pristine 1920x1080 master
    panel = im.resize((1920, 1080), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(panel)

    # Resolve fonts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(script_dir, "../fonts")
    
    font_title_path = os.path.join(fonts_dir, "Bangers-Regular.ttf")
    font_sector_path = os.path.join(fonts_dir, "SpecialElite-Regular.ttf")
    font_caption_path = os.path.join(fonts_dir, "ComicNeue-Bold.ttf")

    # Fallback if missing
    sys_font = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    if not os.path.exists(font_title_path): font_title_path = os.path.join(fonts_dir, "BebasNeue-Regular.ttf")
    if not os.path.exists(font_sector_path): font_sector_path = os.path.join(fonts_dir, "ShareTechMono-Regular.ttf")
    if not os.path.exists(font_caption_path): font_caption_path = os.path.join(fonts_dir, "BarlowCondensed-Bold.ttf")

    font_sector = ImageFont.truetype(font_sector_path, 20)
    font_title = ImageFont.truetype(font_title_path, 42)
    font_caption = ImageFont.truetype(font_caption_path, 26)

    # -------------------------------------------------------------
    # 1. TACTICAL BADGE (Top-Left Dynamic Box)
    # -------------------------------------------------------------
    bx, by = 60, 60
    
    # Calculate text bounds
    bb_sector = font_sector.getbbox(sector)
    sector_w = bb_sector[2] - bb_sector[0]
    
    bb_title = font_title.getbbox(title)
    title_w = bb_title[2] - bb_title[0]
    title_h = bb_title[3] - bb_title[1]

    content_w = max(sector_w, title_w)
    badge_w = max(content_w + 64, 380)
    badge_h = 104

    # Outer solid frame (antiqued bronze)
    bronze = (212, 155, 66)
    dark_obsidian = (10, 11, 15)
    inner_rule = (38, 42, 54)

    draw.rectangle([bx, by, bx + badge_w, by + badge_h], fill=dark_obsidian, outline=bronze, width=3)
    # Subtle inner pinstripe
    draw.rectangle([bx + 4, by + 4, bx + badge_w - 4, by + badge_h - 4], fill=None, outline=inner_rule, width=1)
    # Solid 6px vertical bronze accent bar on left edge
    draw.rectangle([bx, by, bx + 6, by + badge_h], fill=bronze)

    # Text positioning
    draw.text((bx + 26, by + 16), sector, font=font_sector, fill=bronze)
    # Thin divider line
    draw.line([(bx + 26, by + 45), (bx + badge_w - 24, by + 45)], fill=inner_rule, width=1)
    draw.text((bx + 26, by + 48), title, font=font_title, fill=(245, 242, 235))

    # -------------------------------------------------------------
    # 2. NARRATIVE CAPTION PLATE (Bottom Dynamic Box with Text Wrap)
    # -------------------------------------------------------------
    if caption:
        # Wrap text into lines fitting max width ~1550px
        avg_char_w = 14
        wrap_width = max(len(caption), 80)
        # Check text length and wrap
        lines = []
        words = caption.upper().split()
        cur_line = ""
        max_line_w = 0

        for w_word in words:
            test_line = f"{cur_line} {w_word}".strip()
            bb = font_caption.getbbox(test_line)
            w_px = bb[2] - bb[0]
            if w_px > 1500 and cur_line:
                lines.append(cur_line)
                cur_line = w_word
            else:
                cur_line = test_line
        if cur_line:
            lines.append(cur_line)

        # Measure dimensions
        line_height = 36
        text_total_h = len(lines) * line_height
        for l in lines:
            bb = font_caption.getbbox(l)
            max_line_w = max(max_line_w, bb[2] - bb[0])

        cap_pad_x = 36
        cap_pad_y = 20
        cap_w = max_line_w + (cap_pad_x * 2) + 12
        cap_h = text_total_h + (cap_pad_y * 2)

        # Bottom margins: 60px from bottom, centered or left-aligned
        cqx = 60
        cqy = 1080 - cap_h - 60

        # Draw caption card
        draw.rectangle([cqx, cqy, cqx + cap_w, cqy + cap_h], fill=dark_obsidian, outline=(180, 132, 54), width=3)
        draw.rectangle([cqx + 4, cqy + 4, cqx + cap_w - 4, cqy + cap_h - 4], fill=None, outline=inner_rule, width=1)
        # Left 6px bronze bar
        draw.rectangle([cqx, cqy, cqx + 6, cqy + cap_h], fill=bronze)

        # Draw each line of caption text
        for i, line in enumerate(lines):
            line_y = cqy + cap_pad_y + (i * line_height)
            draw.text((cqx + cap_pad_x, line_y), line.upper(), font=font_caption, fill=(245, 240, 230))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    panel.save(output_path, quality=95)
    print(f"Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    main()
