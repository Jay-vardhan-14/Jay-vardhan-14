"""Generate a retro pixel-art banner SVG for a GitHub profile README.

    python make_banner.py "HI, I'M JAY" "A DEVELOPER IN MAKING" > banner.svg

Everything is drawn on an 8px grid with crispEdges so it reads as pixel art
at any zoom. Tweak PALETTE / HORIZON / SUN below to restyle.
"""
import math
import sys

CELL = 8
W, H = 1280, 400
COLS, ROWS = W // CELL, H // CELL
HORIZON = 34          # cell row where sky meets ground
SUN = (134, 17, 11)   # cell x, cell y, radius in cells (kept clear of the text)

PALETTE = {
    "sky": ["#160d2e", "#241442", "#3a1b55", "#552367", "#7b2d6b",
            "#a63c72", "#c94f7c", "#e06a7a", "#f08a5d", "#ffb56b"],
    "star": "#fff3c4",
    "sun_hi": "#ffe6a0",
    "sun_lo": "#ff7f5c",
    "range_far": "#5b3273",
    "range_mid": "#3b2054",
    "range_near": "#241338",
    "ground": "#160c26",
    "tree": "#0c0618",
    "deer": "#0c0618",
    "text": "#ffe9a8",
    "text_shadow": "#b02a6b",
}

# 5x7 bitmap font, uppercase + the punctuation a tagline actually needs.
GW, GH = 5, 7
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#...#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ",": (".....", ".....", ".....", ".....", "..##.", "..#..", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", "..##.", "..##."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
}
assert all(len(g) == GH and all(len(r) == GW for r in g) for g in FONT.values())


def glyph(ch):
    return FONT.get(ch.upper(), FONT[" "])


def rect(x, y, w, h, fill):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>'


def draw_bitmap(rows, x0, y0, scale, fill):
    """Emit rects for a bitmap, merging horizontal runs to keep the file small."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] != "#":
                c += 1
                continue
            run = 0
            while c + run < len(row) and row[c + run] == "#":
                run += 1
            out.append(rect(x0 + c * scale, y0 + r * scale, run * scale, scale, fill))
            c += run
    return out


def text_width(s, scale):
    return (len(s) * (GW + 1) - 1) * scale


def draw_text(s, x0, y0, scale, fill):
    out = []
    for i, ch in enumerate(s):
        out += draw_bitmap(glyph(ch), x0 + i * (GW + 1) * scale, y0, scale, fill)
    return out


def pine(cx, base_row, height):
    """Stepped pine silhouette: cell coords of every filled cell."""
    cells = []
    for i in range(height):
        half = i // 2
        for dx in range(-half, half + 1):
            cells.append((cx + dx, base_row - height + i))
    cells.append((cx, base_row - 1))
    return cells


DEER = [
    "........#.#.#.",
    ".........###..",
    "..........##..",
    "..........###.",
    "..........####",
    "..#########.##",
    ".###########..",
    ".##########...",
    "..#########...",
    "..#..###..#...",
    "..#...#...#...",
    "..#...#...#...",
]


def build(title, subtitle):
    p, out = PALETTE, []
    out.append(rect(0, 0, W, H, p["sky"][0]))

    # sky: banded gradient down to the horizon
    bands = len(p["sky"])
    band_h = (HORIZON * CELL) / bands
    for i, col in enumerate(p["sky"]):
        out.append(rect(0, round(i * band_h), W, math.ceil(band_h) + 1, col))

    # stars, thinned out as the sky brightens
    for i in range(120):
        x = (i * 97) % COLS
        y = (i * 37) % (HORIZON - 14)
        if (x + y) % 3 == 0 and y < 14:
            out.append(rect(x * CELL, y * CELL, CELL // 2, CELL // 2, p["star"]))

    # sun: solid on top, sliced into bars below the midline
    scx, scy, sr = SUN
    for ry in range(scy - sr, scy + sr + 1):
        dy = ry - scy
        half = int(math.sqrt(max(sr * sr - dy * dy, 0)))
        if half == 0:
            continue
        if dy > 2 and (ry - scy) % 3 == 0:
            continue
        col = p["sun_hi"] if dy < 0 else p["sun_lo"]
        out.append(rect((scx - half) * CELL, ry * CELL, (half * 2 + 1) * CELL, CELL, col))

    # three ridgelines, far to near
    for idx, (col, amp, base, freq) in enumerate([
        (p["range_far"], 7, HORIZON - 3, 0.055),
        (p["range_mid"], 5, HORIZON - 1, 0.09),
        (p["range_near"], 4, HORIZON + 1, 0.15),
    ]):
        for cx in range(COLS):
            h = amp * (math.sin(cx * freq + idx * 2.1) * 0.6
                       + math.sin(cx * freq * 2.3 + idx) * 0.4)
            top = int(base - abs(h) - 1)
            out.append(rect(cx * CELL, top * CELL, CELL, (ROWS - top) * CELL, col))

    out.append(rect(0, HORIZON * CELL + 24, W, H, p["ground"]))

    # treeline
    for i, cx in enumerate(range(2, COLS, 7)):
        h = 6 + (i * 5) % 5
        base = HORIZON + 5 + (i % 3)
        for (tx, ty) in pine(cx, base, h):
            out.append(rect(tx * CELL, ty * CELL, CELL, CELL, p["tree"]))

    out += draw_bitmap(DEER, 108 * CELL, (HORIZON + 6) * CELL, CELL // 2, p["deer"])

    # title + subtitle, centred, with a hard pixel shadow
    ts, ss = 9, 4
    tx = (W - text_width(title, ts)) // 2
    sx = (W - text_width(subtitle, ss)) // 2
    out += draw_text(title, tx + ts, 96 + ts, ts, p["text_shadow"])
    out += draw_text(title, tx, 96, ts, p["text"])
    out += draw_text(subtitle, sx + ss, 184 + ss, ss, p["text_shadow"])
    out += draw_text(subtitle, sx, 184, ss, p["text"])

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" shape-rendering="crispEdges">'
            + "".join(out) + "</svg>")


if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "HI, I'M JAY"
    sub = sys.argv[2] if len(sys.argv) > 2 else "A DEVELOPER IN MAKING"
    svg = build(title, sub)
    assert svg.count("<rect") > 500 and svg.endswith("</svg>")
    with open("banner.svg", "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print("wrote banner.svg")
