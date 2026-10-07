"""
generate_app_icons.py
---------------------
Generates crisp PWA app icons for HazWaste Sorter using Pillow:
- static/icon-512.png (512x512)
- static/icon-192.png (192x192)
- static/apple-touch-icon.png (180x180)
- static/favicon.ico (64x64)

Features:
- Dark aeronautical navy base (#0f172a)
- Modern aircraft silhouette with delta wings and tail
- 4 Singapore hangar bin color indicator dots (Red, Yellow, Blue, Dark Slate)
- Antialiased using 4x supersampling (supersampled rendering scaled with Lanczos)
"""

import os
from PIL import Image, ImageDraw

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

def render_master_icon(size=2048):
    """Renders a high-resolution 2048x2048 master icon."""
    img = Image.new("RGBA", (size, size), (15, 23, 42, 255)) # #0f172a dark navy
    draw = ImageDraw.Draw(img)

    # 1. Subtle glowing outer ring
    ring_margin = int(size * 0.05)
    ring_bbox = [ring_margin, ring_margin, size - ring_margin, size - ring_margin]
    draw.rounded_rectangle(ring_bbox, radius=int(size * 0.22), outline=(30, 41, 59, 255), width=int(size * 0.02))

    # Inner badge background
    inner_margin = int(size * 0.08)
    inner_bbox = [inner_margin, inner_margin, size - inner_margin, size - inner_margin]
    draw.rounded_rectangle(inner_bbox, radius=int(size * 0.18), fill=(24, 34, 58, 255))

    # 2. Cyan accent circle in the center
    cx, cy = size // 2, int(size * 0.44)
    r = int(size * 0.28)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 116, 144, 255)) # teal/cyan accent
    draw.ellipse([cx - r + int(size*0.015), cy - r + int(size*0.015), cx + r - int(size*0.015), cy + r - int(size*0.015)], fill=(2, 132, 199, 255)) # sky blue

    # 3. Airplane silhouette in white
    # Triangle nose, sweeping delta wings, horizontal stabilizers, fuselage
    # Coordinates relative to center (cx, cy)
    nose = (cx, cy - int(size * 0.22))
    fuselage_left = (cx - int(size * 0.035), cy - int(size * 0.08))
    fuselage_right = (cx + int(size * 0.035), cy - int(size * 0.08))
    
    wing_left_tip = (cx - int(size * 0.25), cy + int(size * 0.06))
    wing_left_inner = (cx - int(size * 0.045), cy + int(size * 0.08))
    
    wing_right_tip = (cx + int(size * 0.25), cy + int(size * 0.06))
    wing_right_inner = (cx + int(size * 0.045), cy + int(size * 0.08))
    
    tail_fin_left = (cx - int(size * 0.10), cy + int(size * 0.22))
    tail_bottom = (cx, cy + int(size * 0.19))
    tail_fin_right = (cx + int(size * 0.10), cy + int(size * 0.22))

    # Airplane polygon
    plane_poly = [
        nose,
        (cx + int(size * 0.035), cy - int(size * 0.05)),
        wing_right_tip,
        (cx + int(size * 0.18), cy + int(size * 0.09)),
        wing_right_inner,
        (cx + int(size * 0.045), cy + int(size * 0.16)),
        tail_fin_right,
        (cx + int(size * 0.03), cy + int(size * 0.23)),
        tail_bottom,
        (cx - int(size * 0.03), cy + int(size * 0.23)),
        tail_fin_left,
        (cx - int(size * 0.045), cy + int(size * 0.16)),
        wing_left_inner,
        (cx - int(size * 0.18), cy + int(size * 0.09)),
        wing_left_tip,
        (cx - int(size * 0.035), cy - int(size * 0.05)),
    ]
    draw.polygon(plane_poly, fill=(255, 255, 255, 255))

    # 4. Hangar 4-Bin Colour dots (Red, Yellow, Blue, Black/Dark Slate)
    dot_y = int(size * 0.80)
    dot_radius = int(size * 0.05)
    dot_gap = int(size * 0.16)
    dots_start_x = cx - int(dot_gap * 1.5)

    colors = [
        (220, 38, 38, 255),   # Red: Flammable / Solvents
        (234, 179, 8, 255),   # Yellow: Chemical Contaminants
        (37, 99, 235, 255),   # Blue: Recyclables / Metals
        (100, 116, 139, 255), # Black/Slate: General Waste
    ]

    for i, color in enumerate(colors):
        dx = dots_start_x + i * dot_gap
        # Subtle glow ring around dot
        draw.ellipse([dx - dot_radius - int(size*0.01), dot_y - dot_radius - int(size*0.01),
                      dx + dot_radius + int(size*0.01), dot_y + dot_radius + int(size*0.01)],
                     fill=(30, 41, 59, 255))
        draw.ellipse([dx - dot_radius, dot_y - dot_radius, dx + dot_radius, dot_y + dot_radius], fill=color)

    return img

def main():
    print("[*] Generating master icon at 2048x2048...")
    master = render_master_icon(2048)

    targets = [
        ("icon-512.png", 512),
        ("icon-192.png", 192),
        ("apple-touch-icon.png", 180),
        ("favicon.png", 64),
    ]

    for fname, target_size in targets:
        resized = master.resize((target_size, target_size), Image.Resampling.LANCZOS)
        out_path = os.path.join(STATIC_DIR, fname)
        resized.save(out_path, "PNG", optimize=True)
        print(f"  [CREATED] {out_path} ({target_size}x{target_size})")

    # Generate favicon.ico (multi-resolution)
    ico_path = os.path.join(STATIC_DIR, "favicon.ico")
    master.resize((64, 64), Image.Resampling.LANCZOS).save(
        ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)]
    )
    print(f"  [CREATED] {ico_path} (Multi-res ICO)")

if __name__ == "__main__":
    main()
