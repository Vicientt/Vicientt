#!/usr/bin/env python3
"""Generates banner.svg — the isometric scene at the top of the profile README.

Composition follows three rules, in this order of priority:

  1. One ground plane. Every object is a voxel resting on a shared isometric
     lattice, so nothing floats free. Blocks shade top > left > right, which is
     what sells the third dimension. The floor is a ribbon (constant depth band
     gx+gy) so it reads as a level horizon spanning the full width.
  2. One leading line. A minecart rail runs along that ribbon from the wizard's
     bench to the chest, carrying a data crate, so the eye is walked
     left-to-right instead of hopping between islands.
  3. One focal point, off-centre. The diamond sits on the upper-right rule-of-
     thirds intersection (0.70W, 0.30H) and is tied to the ground by a light
     shaft rising straight out of the open chest directly beneath it.

Run:  python3 tools/build_banner.py   (writes banner.svg next to README.md)
"""

from pathlib import Path

W, H = 1200, 400
U = 34                      # half-width of a tile; tiles are 2U wide, U tall (2:1)
BH = 34                     # block height in screen pixels
OX, OY = 600, 232           # lattice origin (screen centre)
V0, V1 = 0, 6               # depth band of the floor ribbon

PAL = {
    "wall":    "#0e2544",
    "stone_t": "#2c5182", "stone_l": "#1c4472", "stone_r": "#12325a",
    "dark_t":  "#1d3c66", "dark_l":  "#152f52", "dark_r":  "#0e2240",
    "moss_t":  "#2f5f7d", "moss_l":  "#1e4a63", "moss_r":  "#143548",
    "plank_t": "#8a5a2b", "plank_l": "#6d4621", "plank_r": "#4a2f16",
    "cyan":    "#43c9ff", "cyan_hi": "#a9e8ff", "cyan_wh": "#eafcff",
    "gold":    "#f6b23a", "gold_hi": "#ffcb5b", "gold_dk": "#a86f1a",
    "ink":     "#e6f0fb", "ink_lo":  "#6f8fb5",
    "robe":    "#2f6fd0", "robe_dk": "#1b3f80", "robe_hi": "#5b9bea",
    "skin":    "#e8b98c", "beard":   "#dbe7f5",
}

out = []
def add(s): out.append(s)


def iso(gx, gy, gz=0.0):
    """Lattice coords -> screen. Constant gx+gy is a horizontal line on screen."""
    return (OX + (gx - gy) * U, OY + (gx + gy) * (U / 2) - gz * BH)


def at(x, v):
    """Inverse helper: lattice tile whose screen x is nearest `x`, on depth row v."""
    d = round((x - OX) / U)
    if (d + v) % 2:
        d += 1
    return ((v + d) // 2, (v - d) // 2)


def block(gx, gy, gz, top, left, right):
    x, y = iso(gx, gy, gz)
    add(f'<path d="M{x},{y-BH} l{U},{U/2} l{-U},{U/2} l{-U},{-U/2} Z" fill="{top}"/>')
    add(f'<path d="M{x-U},{y-BH+U/2} l{U},{U/2} l0,{BH} l{-U},{-U/2} Z" fill="{left}"/>')
    add(f'<path d="M{x+U},{y-BH+U/2} l{-U},{U/2} l0,{BH} l{U},{-U/2} Z" fill="{right}"/>')


def shadow(x, y, rx, o=.45):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*0.42}" fill="#02060c" opacity="{o}"/>')


# 5x7 bitmap font, drawn as rects so the pixel look survives without a webfont.
FONT = {
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "M": ["10001","11011","10101","10001","10001","10001","10001"],
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "C": ["01110","10001","10000","10000","10000","10001","01110"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "&": ["01100","10010","10010","01100","10101","10010","01101"],
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
}


def pixel_text(s, x, y, px, fill, opacity=1.0, anchor="start"):
    w = len(s) * 6 * px
    if anchor == "middle":
        x -= w / 2
    add(f'<g fill="{fill}" opacity="{opacity}">')
    cx = x
    for ch in s.upper():
        rows = FONT.get(ch)
        if rows:
            for r, row in enumerate(rows):
                run = 0
                for c in range(6):
                    on = c < 5 and row[c] == "1"
                    if on:
                        run += 1
                    elif run:
                        add(f'<rect x="{cx+(c-run)*px:.1f}" y="{y+r*px:.1f}" '
                            f'width="{run*px:.1f}" height="{px}"/>')
                        run = 0
        cx += 6 * px
    add("</g>")


def sprite(grid, x, y, px, cols):
    """Run-length a bitmap into rects."""
    for r, row in enumerate(grid):
        run_c, run_n = None, 0
        for c in range(len(row) + 1):
            ch = row[c] if c < len(row) else "."
            if ch == run_c and ch != ".":
                run_n += 1
            else:
                if run_c and run_n:
                    add(f'<rect x="{x+(c-run_n)*px:.1f}" y="{y+r*px:.1f}" '
                        f'width="{run_n*px:.1f}" height="{px}" fill="{cols[run_c]}"/>')
                run_c, run_n = (ch, 1) if ch != "." else (None, 0)


# ================================================================= document
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'role="img" aria-label="Isometric pixel scene: a wizard codes at a lit bench on the left, '
    f'a minecart carries a glowing data crate along a rail across the middle, and on the right an '
    f'open chest sends a shaft of light up to a floating diamond">')

add("""<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#0a1730"/>
    <stop offset="48%"  stop-color="#050d1c"/>
    <stop offset="100%" stop-color="#02060e"/>
  </linearGradient>
  <radialGradient id="chestGlow"><stop offset="0%" stop-color="#f6b23a" stop-opacity=".5"/>
    <stop offset="55%" stop-color="#f6b23a" stop-opacity=".12"/>
    <stop offset="100%" stop-color="#f6b23a" stop-opacity="0"/></radialGradient>
  <radialGradient id="torchGlow"><stop offset="0%" stop-color="#ffcb5b" stop-opacity=".42"/>
    <stop offset="100%" stop-color="#ffcb5b" stop-opacity="0"/></radialGradient>
  <radialGradient id="screenGlow"><stop offset="0%" stop-color="#43c9ff" stop-opacity=".40"/>
    <stop offset="100%" stop-color="#43c9ff" stop-opacity="0"/></radialGradient>
  <radialGradient id="gemGlow"><stop offset="0%" stop-color="#a9e8ff" stop-opacity=".55"/>
    <stop offset="100%" stop-color="#a9e8ff" stop-opacity="0"/></radialGradient>
  <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0%"   stop-color="#8fdcff" stop-opacity=".72"/>
    <stop offset="45%"  stop-color="#a9e8ff" stop-opacity=".34"/>
    <stop offset="100%" stop-color="#eafcff" stop-opacity=".05"/></linearGradient>
  <linearGradient id="vign" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="#02060e" stop-opacity=".95"/>
    <stop offset="10%"  stop-color="#02060e" stop-opacity="0"/>
    <stop offset="90%"  stop-color="#02060e" stop-opacity="0"/>
    <stop offset="100%" stop-color="#02060e" stop-opacity=".95"/></linearGradient>
  <linearGradient id="floorFade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#02060e" stop-opacity="0"/>
    <stop offset="100%" stop-color="#02060e" stop-opacity=".85"/></linearGradient>
  <style>
    .bob   { animation: bob 3.4s ease-in-out infinite; }
    .flick { animation: flick 1.4s steps(3) infinite; }
    .pulse { animation: pulse 3.2s ease-in-out infinite; }
    .spark { animation: spark 3s ease-in-out infinite; }
    .cart  { animation: ride 11s ease-in-out infinite; }
    .scan  { animation: scan 2.4s linear infinite; }
    @keyframes bob   { 0%,100%{transform:translateY(0)}    50%{transform:translateY(-8px)} }
    @keyframes flick { 0%,100%{opacity:.82}                50%{opacity:1} }
    @keyframes pulse { 0%,100%{opacity:.5}                 50%{opacity:1} }
    @keyframes spark { 0%,100%{opacity:0}                  50%{opacity:1} }
    @keyframes scan  { 0%{transform:translateY(-16px)}     100%{transform:translateY(16px)} }
    @keyframes ride  { 0%,4%{transform:translate(0,0)}     46%,54%{transform:translate(418px,0)}
                       96%,100%{transform:translate(0,0)} }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
  </style>
</defs>""")

add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

# ------------------------------------------------------- background: cavern
# A single jagged rock ceiling reads as one mass; loose rectangles read as
# debris and were the main reason the old banner felt scattered.
ceil = "M0,0 L{},0 L{},58".format(W, W)
for cx0, cy0 in [(1120, 92), (1040, 46), (952, 78), (860, 38), (760, 84),
                 (668, 44), (566, 90), (470, 40), (372, 72), (268, 34),
                 (170, 80), (78, 42), (0, 66)]:
    ceil += f" L{cx0},{cy0}"
ceil += " L0,0 Z"
add(f'<path d="{ceil}" fill="{PAL["wall"]}"/>')
add(f'<path d="{ceil}" fill="none" stroke="#153059" stroke-width="3" opacity=".8"/>')

add('<g opacity=".85">')
for sx, sw, sh in [(118, 20, 62), (262, 14, 40), (392, 12, 34), (508, 22, 74),
                   (652, 14, 38), (784, 18, 52), (918, 14, 36), (1064, 20, 58)]:
    add(f'<path d="M{sx},{max(0,0)} l{sw},0 l{-sw/2},{sh} Z" fill="{PAL["dark_r"]}"/>')
add("</g>")

# distant arches, receding — depth without clutter
for ax, aw, ah, op in [(180, 104, 84, .16), (600, 128, 100, .14), (1010, 100, 80, .16)]:
    add(f'<g opacity="{op}"><rect x="{ax-aw/2}" y="{230-ah}" width="14" height="{ah}" fill="{PAL["dark_l"]}"/>'
        f'<rect x="{ax+aw/2-14}" y="{230-ah}" width="14" height="{ah}" fill="{PAL["dark_l"]}"/>'
        f'<rect x="{ax-aw/2}" y="{230-ah-14}" width="{aw}" height="16" fill="{PAL["dark_t"]}"/></g>')

for x, y, r, d in [(150, 128, 1.7, .0), (420, 96, 1.4, .6), (700, 74, 1.9, 1.2),
                   (980, 112, 1.5, .3), (1105, 82, 1.6, .9), (300, 62, 1.3, 1.5)]:
    add(f'<circle class="spark" cx="{x}" cy="{y}" r="{r}" fill="{PAL["cyan_hi"]}" '
        f'style="animation-delay:{d}s"/>')

# ------------------------------------------------------------- floor ribbon
# Top faces only, so the surface reads flat. Side faces belong to the front
# row alone — drawing them on every row is what turns a floor into sawteeth.
add("<g>")
tiles = []
for gx in range(-18, 19):
    for gy in range(-18, 19):
        v = gx + gy
        if not (V0 <= v <= V1):
            continue
        sx, sy = iso(gx, gy, 0)
        if -180 < sx < W + 180:
            tiles.append((v, gx, gy))
for v, gx, gy in sorted(tiles):
    x, y = iso(gx, gy, 0)
    top = PAL["moss_t"] if v == V0 else PAL["stone_t"]
    add(f'<path d="M{x},{y-BH} l{U},{U/2} l{-U},{U/2} l{-U},{-U/2} Z" fill="{top}"/>')
    add(f'<path d="M{x},{y-BH} l{U},{U/2} l{-U},{U/2} l{-U},{-U/2} Z" fill="none" '
        f'stroke="#0e2240" stroke-width=".8" opacity=".5"/>')
add("</g>")

# One continuous skirt under the front row, carried down past the canvas edge.
add("<g>")
front = sorted([(gx, gy) for v, gx, gy in tiles if v == V1], key=lambda t: t[0] - t[1])
for gx, gy in front:
    x, y = iso(gx, gy, 0)
    ty = y - BH + U / 2
    add(f'<path d="M{x-U},{ty} l{U},{U/2} l0,{H} l{-U},{-U/2} Z" fill="{PAL["dark_l"]}"/>')
    add(f'<path d="M{x+U},{ty} l{-U},{U/2} l0,{H} l{U},{-U/2} Z" fill="{PAL["dark_l"]}"/>')
if front:
    fx, fy = iso(front[0][0], front[0][1], 0)
    base = fy - BH + U
    add(f'<rect x="0" y="{base}" width="{W}" height="{H-base}" fill="{PAL["dark_l"]}"/>')
    add(f'<rect x="0" y="{base}" width="{W}" height="3" fill="{PAL["dark_r"]}" opacity=".7"/>')
add("</g>")

# diamond ore glinting in the floor — texture, and foreshadowing
for tx, v in [(180, 1), (330, 4), (620, 1), (760, 4), (1010, 2), (455, 2)]:
    gx, gy = at(tx, v)
    x, y = iso(gx, gy, 0)
    for dx, dy in [(-9, -2), (4, 4), (-2, 8)]:
        add(f'<rect class="pulse" x="{x+dx}" y="{y-BH+U/2+dy}" width="5" height="5" '
            f'fill="{PAL["cyan"]}" style="animation-delay:{(tx%5)*.4:.1f}s"/>')

# ------------------------------------------------------------- the rail line
RAIL_V = 3
add('<g id="rail">')
rail_pts = []
for tx in range(120, 940, 2 * U):
    gx, gy = at(tx, RAIL_V)
    x, y = iso(gx, gy, 0)
    rail_pts.append((x, y - BH + U / 2))
for x, ty in rail_pts:
    add(f'<path d="M{x-U},{ty+U/2} l{U},{-U/2} l{U},{U/2}" stroke="{PAL["plank_r"]}" '
        f'stroke-width="4" fill="none"/>')
if rail_pts:
    x0, y0 = rail_pts[0]; x1, y1 = rail_pts[-1]
    for off in (-7, 7):
        add(f'<line x1="{x0-U}" y1="{y0+U/2+off*0.5}" x2="{x1+U}" y2="{y1+U/2+off*0.5}" '
            f'stroke="{PAL["ink_lo"]}" stroke-width="2.5" opacity=".6"/>')
add("</g>")

RAIL_Y = rail_pts[0][1] + U / 2 if rail_pts else OY

# ============================================================ LEFT: the work
WIZ_X = 250
gx, gy = at(WIZ_X, RAIL_V - 1)
GX, GY = iso(gx, gy, 1)

# torch post — warm key light, and a vertical to frame the left edge
tx = WIZ_X - 116
add(f'<ellipse cx="{tx}" cy="{GY-78}" rx="86" ry="76" fill="url(#torchGlow)"/>')
add(f'<rect x="{tx-4}" y="{GY-72}" width="8" height="74" fill="{PAL["plank_r"]}"/>')
add(f'<g class="flick"><rect x="{tx-8}" y="{GY-88}" width="16" height="18" fill="{PAL["gold"]}"/>'
    f'<rect x="{tx-4}" y="{GY-98}" width="8" height="12" fill="{PAL["gold_hi"]}"/></g>')

# bench + code screen
bx = WIZ_X + 96
shadow(bx, GY + 8, 38, .34)
add(f'<ellipse cx="{bx}" cy="{GY-52}" rx="86" ry="72" fill="url(#screenGlow)"/>')
add(f'<path d="M{bx},{GY-26} l40,20 l0,22 l-40,20 l-40,-20 l0,-22 Z" fill="{PAL["plank_l"]}"/>')
add(f'<path d="M{bx},{GY-26} l40,20 l-40,20 l-40,-20 Z" fill="{PAL["plank_t"]}"/>')
add(f'<g class="flick">')
add(f'<rect x="{bx-34}" y="{GY-98}" width="68" height="46" fill="#02060e" '
    f'stroke="{PAL["cyan"]}" stroke-width="2.5"/>')
add(f'<clipPath id="scr"><rect x="{bx-31}" y="{GY-95}" width="62" height="40"/></clipPath>')
add('<g clip-path="url(#scr)"><g class="scan">')
for i, w in enumerate([44, 30, 50, 24, 40, 34, 46, 28, 42]):
    add(f'<rect x="{bx-27}" y="{GY-104+i*8}" width="{w}" height="3.5" '
        f'fill="{PAL["gold"] if i % 3 == 0 else PAL["cyan_hi"]}" opacity=".9"/>')
add("</g></g></g>")
add(f'<rect x="{bx-5}" y="{GY-56}" width="10" height="32" fill="{PAL["plank_r"]}"/>')
add(f'<rect x="{bx-16}" y="{GY-58}" width="32" height="6" fill="{PAL["plank_l"]}"/>')

# the wizard
WIZ = [
    "......111.......", ".....11111......", "....1111111.....", "...111111111....",
    "..11111111111...", ".2222222222222..", "....33333.......", "...3344333......",
    "...3344333......", "....33333.......", "....66666.......", "...4444444......",
    "..444444444.....", ".44444444444....", ".44444444444....", ".444444444444...",
    ".4444...4444....", ".4444...4444....", ".444.....444....", ".555.....555....",
]
COLS = {"1": PAL["robe_dk"], "2": PAL["robe"], "3": PAL["skin"], "4": PAL["robe"],
        "5": PAL["plank_r"], "6": PAL["beard"]}
px = 5.4
shadow(WIZ_X, GY + 10, 34, .38)
add('<g class="bob">')
sprite(WIZ, WIZ_X - 8 * px, GY - 20 * px + 6, px, COLS)
# hat brim + robe trim catch the torch light
add(f'<rect x="{WIZ_X-8*px}" y="{GY-15*px+6}" width="{16*px}" height="{px}" fill="{PAL["robe_hi"]}"/>')
# staff, angled toward the rail
add(f'<rect x="{WIZ_X+36}" y="{GY-88}" width="5" height="90" fill="{PAL["plank_r"]}"/>')
add(f'<g class="pulse"><rect x="{WIZ_X+30}" y="{GY-104}" width="17" height="17" fill="{PAL["cyan"]}"/>'
    f'<rect x="{WIZ_X+34}" y="{GY-100}" width="9" height="9" fill="{PAL["cyan_wh"]}"/></g>')
add("</g>")

# hanging sign — puts the name inside the world instead of on top of it
sgx = WIZ_X - 34
add(f'<rect x="{sgx-3}" y="{GY-158}" width="6" height="52" fill="{PAL["plank_r"]}"/>')
add(f'<rect x="{sgx-84}" y="{GY-214}" width="168" height="58" fill="{PAL["plank_l"]}" '
    f'stroke="{PAL["plank_r"]}" stroke-width="4"/>')
add(f'<rect x="{sgx-76}" y="{GY-206}" width="152" height="42" fill="{PAL["plank_t"]}" opacity=".25"/>')
pixel_text("HENRY", sgx, GY - 200, 4.4, PAL["gold_hi"], 1, "middle")
pixel_text("MATH & CS", sgx, GY - 172, 2.0, PAL["ink"], .85, "middle")

# ==================================================== MIDDLE: the throughline
# support arches receding behind the rail, to add depth without clutter
for ax in (470, 700):
    gxa, gya = at(ax, V0)
    xa, ya = iso(gxa, gya, 1)
    add(f'<g opacity=".5"><rect x="{xa-46}" y="{ya-96}" width="10" height="96" fill="{PAL["dark_l"]}"/>'
        f'<rect x="{xa+36}" y="{ya-96}" width="10" height="96" fill="{PAL["dark_l"]}"/>'
        f'<rect x="{xa-46}" y="{ya-104}" width="92" height="12" fill="{PAL["dark_t"]}"/></g>')

# ore blocks flanking the path
for tx in (410, 640):
    gxo, gyo = at(tx, V1 - 1)
    block(gxo, gyo, 1, PAL["stone_t"], PAL["stone_l"], PAL["stone_r"])
    xo, yo = iso(gxo, gyo, 1)
    for dx, dy in [(-10, -6), (6, -12), (0, 2)]:
        add(f'<rect class="pulse" x="{xo+dx}" y="{yo-BH+U/2+dy}" width="6" height="6" '
            f'fill="{PAL["cyan"]}" style="animation-delay:{tx%4*.5:.1f}s"/>')

# the minecart — the moving link between work and payoff
add('<g class="cart">')
cx = 392
add(f'<g transform="translate({cx},{RAIL_Y-6})">')
shadow(0, 16, 30, .42)
add(f'<path d="M0,-4 l32,16 l0,14 l-32,16 l-32,-16 l0,-14 Z" fill="{PAL["dark_r"]}"/>')
add(f'<path d="M-32,-4 l32,16 l0,14 l-32,-16 Z" fill="{PAL["stone_l"]}"/>')
add(f'<path d="M32,-4 l-32,16 l0,14 l32,-16 Z" fill="{PAL["dark_l"]}"/>')
add(f'<path d="M0,-4 l32,16 l-32,16 l-32,-16 Z" fill="{PAL["stone_t"]}"/>')
add(f'<g class="bob"><path d="M0,-30 l17,9 l0,13 l-17,9 l-17,-9 l0,-13 Z" fill="{PAL["cyan"]}"/>'
    f'<path d="M0,-30 l17,9 l-17,9 l-17,-9 Z" fill="{PAL["cyan_wh"]}"/></g>')
for wdx in (-17, 17):
    add(f'<circle cx="{wdx}" cy="{28}" r="5" fill="{PAL["plank_r"]}"/>')
add("</g></g>")

# =========================================================== RIGHT: the payoff
CHEST_X = W * 0.70                              # 840 — right rule-of-thirds line
gxc, gyc = at(CHEST_X, RAIL_V - 1)
PX, PY = iso(gxc, gyc, 1)

# plinth: three blocks lifting the chest clear of the rail
for ddx, ddy in [(0, 0), (1, 0), (0, 1)]:
    block(gxc + ddx, gyc + ddy, 0, PAL["stone_t"], PAL["stone_l"], PAL["stone_r"])
block(gxc, gyc, 1, PAL["stone_t"], PAL["stone_l"], PAL["stone_r"])

KX, KY = iso(gxc, gyc, 2)
add(f'<ellipse cx="{KX}" cy="{KY-20}" rx="120" ry="92" fill="url(#chestGlow)"/>')

GEM_X, GEM_Y = W * 0.70, H * 0.30               # focal point
# light shaft ties the diamond to the chest so neither floats
add(f'<path d="M{KX-34},{KY-24} L{KX+34},{KY-24} L{GEM_X+62},{GEM_Y+22} L{GEM_X-62},{GEM_Y+22} Z" '
    f'fill="url(#beam)" class="pulse"/>')

# chest: isometric box, open lid hinged back, loot spilling
add(f'<path d="M{KX-40},{KY-18} l40,20 l40,-20 l0,30 l-40,20 l-40,-20 Z" fill="{PAL["gold_dk"]}"/>')
add(f'<path d="M{KX-40},{KY-18} l40,20 l0,30 l-40,-20 Z" fill="{PAL["gold"]}"/>')
add(f'<path d="M{KX+40},{KY-18} l-40,20 l0,30 l40,-20 Z" fill="{PAL["gold_dk"]}"/>')
add(f'<path d="M{KX},{KY+2} l40,-20 l0,6 l-40,20 l-40,-20 l0,-6 Z" fill="#3a2408"/>')
for dx, dy, c in [(-16, -6, PAL["gold_hi"]), (-2, -12, PAL["cyan_hi"]), (14, -7, PAL["gold_hi"]),
                  (-8, -2, PAL["gold"]), (7, -3, PAL["gold"])]:
    add(f'<rect class="pulse" x="{KX+dx}" y="{KY-14+dy}" width="8" height="8" fill="{c}" '
        f'style="animation-delay:{abs(dx)*.05:.2f}s"/>')
# lid, tilted open behind the box
add(f'<g transform="translate({KX},{KY-30}) rotate(-24)">'
    f'<path d="M-38,0 l38,19 l38,-19 l0,-9 l-38,-19 l-38,19 Z" fill="{PAL["gold"]}"/>'
    f'<path d="M-38,0 l38,19 l0,-9 l-38,-19 Z" fill="{PAL["gold_hi"]}"/></g>')

# the diamond
add(f'<ellipse cx="{GEM_X}" cy="{GEM_Y}" rx="86" ry="78" fill="url(#gemGlow)"/>')
add('<g class="bob">')
add(f'<path d="M{GEM_X},{GEM_Y-38} l28,28 l-28,42 l-28,-42 Z" fill="{PAL["cyan"]}"/>')
add(f'<path d="M{GEM_X},{GEM_Y-38} l28,28 l-28,12 Z" fill="{PAL["cyan_hi"]}"/>')
add(f'<path d="M{GEM_X},{GEM_Y-38} l-28,28 l28,12 Z" fill="{PAL["cyan_wh"]}"/>')
add(f'<path d="M{GEM_X-28},{GEM_Y-10} l28,12 l28,-12 l-28,42 Z" fill="{PAL["cyan"]}" opacity=".72"/>')
add("</g>")
for ddx, ddy, s, d in [(-52, -40, 6, .0), (48, -26, 5, .7), (-40, 32, 5, 1.4),
                       (56, 22, 6, .4), (8, -62, 5, 1.1)]:
    add(f'<rect class="spark" x="{GEM_X+ddx}" y="{GEM_Y+ddy}" width="{s}" height="{s}" '
        f'fill="{PAL["cyan_hi"]}" style="animation-delay:{d}s"/>')

# clusters of crystal on the open floor, filling the dead space low and wide
for tx, v, n in [(120, 5, 3), (540, 5, 4), (1030, 5, 3), (300, 6, 2), (760, 6, 3)]:
    gxk, gyk = at(tx, v)
    xk, yk = iso(gxk, gyk, 0)
    yk = yk - BH + U / 2
    for i in range(n):
        h = 12 + (i * 7) % 18
        ox = (i - n / 2) * 11
        add(f'<path d="M{xk+ox},{yk-h} l6,{h*0.55} l-6,{h*0.45} l-6,{-h*0.45} Z" '
            f'fill="{PAL["cyan"]}" opacity=".8"/>')
        add(f'<path d="M{xk+ox},{yk-h} l6,{h*0.55} l-6,{h*0.1} Z" fill="{PAL["cyan_hi"]}" opacity=".9"/>')

# foreground rock, near-black, framing the bottom corners and adding a depth plane
add(f'<path d="M0,{H} L0,{H-76} L58,{H-96} L126,{H-58} L188,{H-82} L232,{H} Z" fill="#02060e"/>')
add(f'<path d="M{W},{H} L{W},{H-88} L{W-64},{H-104} L{W-140},{H-62} L{W-196},{H-90} L{W-244},{H} Z" '
    f'fill="#02060e"/>')

# ------------------------------------------------------------------ finishing
add(f'<rect width="{W}" height="{H}" fill="url(#vign)"/>')
add("</svg>")

svg = "\n".join(out)
dest = Path(__file__).resolve().parent.parent / "banner.svg"
dest.write_text(svg)
print(f"wrote {dest} ({len(svg):,} bytes)")
