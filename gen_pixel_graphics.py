"""
Generate pixel-art PNGs for the Monopong GBC-mode webpage,
derived directly from the actual Game Boy Color game data.

Produces:
    - assets/images/ring-pixel.png   : arena circle with AA, matching gen_arena.py logic
    - assets/images/balls-pixel.png  : ball + 2 ghost trails, matching render_playing.c

All coordinates and radii match the real GBC game constants.
"""

import math
from pathlib import Path
from PIL import Image

# ================================================================
# Game constants (from src/constants.h)
# ================================================================
ARENA_RADIUS = 52
RING_WIDTH = 2
CENTER_X = 80
CENTER_Y = 72
SCREEN_W = 160
SCREEN_H = 144

# Ball sprite (from src/generated/tiles.h) — 2bpp Game Boy format
# Each row = 2 bytes (plane0, plane1). Pixel value = bit from each plane.
SPR_BALL_RAW = [
    0x3C,
    0x3C,
    0x42,
    0x7E,
    0x81,
    0xFF,
    0x81,
    0xFF,
    0x81,
    0xFF,
    0x81,
    0xFF,
    0x42,
    0x7E,
    0x3C,
    0x3C,
]

# Ghost trail offsets from render_playing.c:
#   ghost1 = 10px behind ball, ghost2 = 20px behind ball
GHOST1_DIST = 10
GHOST2_DIST = 20

# Palette (from tools/gen_palette.py, converted to 8-bit RGB)
# BGR555 -> RGB8: component = (val5 / 31) * 255
COL_BLACK = (0, 0, 0, 255)
COL_WHITE = (255, 255, 255, 255)
COL_DARK = (33, 33, 49, 255)  # background dark
COL_LIGHT = (181, 181, 181, 255)  # AA midtone
TRANSPARENT = (0, 0, 0, 0)

# Ghost opacities (palette 1 = dim)
GHOST1_ALPHA = 128  # ~50%
GHOST2_ALPHA = 64  # ~25%

# Supersampling for ring AA (matching gen_arena.py)
SS = 4


def decode_ball_sprite():
    """Decode the 8x8 2bpp Game Boy sprite into an 8x8 pixel grid.
    Returns list of 8 rows, each a list of 8 palette indices (0-3)."""
    rows = []
    for y in range(8):
        plane0 = SPR_BALL_RAW[y * 2]
        plane1 = SPR_BALL_RAW[y * 2 + 1]
        row = []
        for bit in range(7, -1, -1):
            p0 = (plane0 >> bit) & 1
            p1 = (plane1 >> bit) & 1
            row.append(p0 + p1 * 2)
        rows.append(row)
    return rows


def ball_to_image(ball_grid, alpha=255):
    """Convert 8x8 palette-indexed ball to RGBA pixel list.
    Index 0 = transparent, 1 = white, 2 = white, 3 = white (all lit)."""
    pixels = []
    for row in ball_grid:
        for idx in row:
            if idx == 0:
                pixels.append(TRANSPARENT)
            else:
                pixels.append((255, 255, 255, alpha))
    return pixels


# ================================================================
# Generate assets/images/ring-pixel.png
# ================================================================
# Output a square PNG where the ring fills the full width.
# Same thickness and AA algorithm as gen_arena.py, just a larger radius.
RING_IMG_SIZE = 128  # native pixel resolution (scaled up on the page)
RING_IMG_CX = RING_IMG_SIZE // 2
RING_IMG_CY = RING_IMG_SIZE // 2
RING_IMG_RADIUS = RING_IMG_SIZE // 2 - 2  # leave 2px margin so AA pixels aren't clipped


OUTPUT_DIR = Path("assets/images")


def gen_ring():
    """Generate the arena ring using the same supersampled AA as gen_arena.py,
    but sized so the circle fills the full output image."""
    r_inner = float(RING_IMG_RADIUS)
    r_outer = float(RING_IMG_RADIUS + RING_WIDTH)

    img = Image.new("RGBA", (RING_IMG_SIZE, RING_IMG_SIZE), TRANSPARENT)

    for py in range(RING_IMG_SIZE):
        for px in range(RING_IMG_SIZE):
            dx = px - RING_IMG_CX
            dy = py - RING_IMG_CY
            r2 = dx * dx + dy * dy

            # Quick reject: far inside or far outside
            if (
                r2 < (RING_IMG_RADIUS - 2) ** 2
                or r2 > (RING_IMG_RADIUS + RING_WIDTH + 2) ** 2
            ):
                continue

            # Supersample for AA (4×4, same as gen_arena.py)
            ring_hits = 0
            for sy in range(SS):
                for sx in range(SS):
                    spx = px + (sx + 0.5) / SS
                    spy = py + (sy + 0.5) / SS
                    sdx = spx - RING_IMG_CX
                    sdy = spy - RING_IMG_CY
                    r = math.sqrt(sdx * sdx + sdy * sdy)
                    if r_inner <= r <= r_outer:
                        ring_hits += 1

            total = SS * SS
            if ring_hits == total:
                img.putpixel((px, py), COL_WHITE)
            elif ring_hits > 0:
                # AA midtone — partial coverage
                img.putpixel((px, py), COL_LIGHT)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "ring-pixel.png"
    img.save(output_path)
    print(
        f"Wrote {output_path} ({RING_IMG_SIZE}x{RING_IMG_SIZE}, radius={RING_IMG_RADIUS}, ring_width={RING_WIDTH})"
    )


# ================================================================
# Generate assets/images/balls-pixel.png
# ================================================================
def gen_balls():
    """Generate ball + 2 ghost trails on a transparent canvas.
    Ball at centre, ghosts offset diagonally (matching a ~45° angle)."""
    ball_grid = decode_ball_sprite()

    # We render on the game-resolution canvas.
    # Place main ball near top-right of a region, ghosts trailing bottom-left.
    # Use a canvas sized to fit all 3 balls with the actual game offsets.
    # At 45°, dx and dy components are equal: dist * cos(45°) ≈ dist * 0.707

    diag1 = round(GHOST1_DIST * 0.707)
    diag2 = round(GHOST2_DIST * 0.707)

    # Canvas: big enough to hold all 3 balls with padding
    pad = 2
    # Ball positions relative to canvas origin
    # Main ball at top-right, ghosts down-left
    main_x = diag2 + pad
    main_y = pad
    g1_x = main_x - diag1
    g1_y = main_y + diag1
    g2_x = main_x - diag2
    g2_y = main_y + diag2

    canvas_w = main_x + 8 + pad
    canvas_h = g2_y + 8 + pad

    img = Image.new("RGBA", (canvas_w, canvas_h), TRANSPARENT)

    # Draw ghost 2 first (behind everything)
    ball_pixels_g2 = ball_to_image(ball_grid, GHOST2_ALPHA)
    g2_img = Image.new("RGBA", (8, 8))
    g2_img.putdata(ball_pixels_g2)
    img.paste(g2_img, (g2_x, g2_y), g2_img)

    # Draw ghost 1
    ball_pixels_g1 = ball_to_image(ball_grid, GHOST1_ALPHA)
    g1_img = Image.new("RGBA", (8, 8))
    g1_img.putdata(ball_pixels_g1)
    img.paste(g1_img, (g1_x, g1_y), g1_img)

    # Draw main ball
    ball_pixels = ball_to_image(ball_grid, 255)
    ball_img = Image.new("RGBA", (8, 8))
    ball_img.putdata(ball_pixels)
    img.paste(ball_img, (main_x, main_y), ball_img)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "balls-pixel.png"
    img.save(output_path)
    print(f"Wrote {output_path} ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    gen_ring()
    gen_balls()
