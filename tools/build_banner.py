#!/usr/bin/env python3
"""Generates banner.svg — the isometric scene at the top of the profile README.

Composition follows three rules, in this order of priority:

  1. One ground plane. Every object is a voxel resting on a shared isometric
     lattice, so nothing floats free. Blocks shade top > left > right, which is
     what sells the third dimension. The floor is a ribbon (constant depth band
     gx+gy) so it reads as a level horizon spanning the full width.
  2. One leading line. A rail runs along that ribbon from the wizard's bench to
     the chest; the cast sends cards of code down it, so the eye is walked
     left-to-right instead of hopping between islands.
  3. One focal point, off-centre. The diamond sits on the upper-right rule-of-
     thirds intersection (0.70W, 0.30H) and is tied to the ground by a light
     shaft rising straight out of the open chest directly beneath it.

Run:  python3 tools/build_banner.py   (writes banner.svg next to README.md)
"""

import random
from pathlib import Path

import pixelfont as pf

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


def pixel_text(s, x, y, px, fill, opacity=1.0, anchor="start"):
    """Thin wrapper over the shared font so both generators stay in step."""
    if anchor == "middle":
        x -= pf.text_width(s, px) / 2
    add(f'<g opacity="{opacity}">{pf.emit(s, x, y, px, fill=fill)}</g>')


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
    f'raises a wand to conjure cards of code that fly along a rail across the middle, and on the right an '
    f'open chest sends a shaft of light up to a floating diamond">')

add("""<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="#050a1d"/>
    <stop offset="42%"  stop-color="#030713"/>
    <stop offset="100%" stop-color="#01030a"/>
  </linearGradient>
  <radialGradient id="nebA"><stop offset="0%" stop-color="#2b5bd0" stop-opacity=".22"/>
    <stop offset="100%" stop-color="#2b5bd0" stop-opacity="0"/></radialGradient>
  <radialGradient id="nebB"><stop offset="0%" stop-color="#7a3fd0" stop-opacity=".18"/>
    <stop offset="100%" stop-color="#7a3fd0" stop-opacity="0"/></radialGradient>
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
    /* One 6s spell, read left to right:
       0.00-0.42s  afterglow, chest open, diamond out
       0.42-0.72s  lid shuts, the diamond drops back inside
       0.84-1.80s  wizard raises the wand, focus stone flares
       1.68-3.36s  four cards of code fly the rail, 0.12s apart
       3.42-3.78s  lid springs open
       3.84-4.20s  diamond rises to the focal point and holds        */
    .bob     { animation: bob 2.8s ease-in-out infinite; }
    .flick   { animation: flick 1.2s steps(3) infinite; }
    .pulse   { animation: pulse 2.6s ease-in-out infinite; }
    .spark   { animation: spark 2.4s ease-in-out infinite; }
    .scan    { animation: scan 2s linear infinite; }
    .twinkle { animation: twinkle 3s ease-in-out infinite; }

    .wand    { animation: wand 6s ease-in-out infinite; }
    .runes   { animation: runes 6s ease-in-out infinite; }
    /* backwards fill matters: during animation-delay an element falls back to
       its own style, so a staggered packet would sit visible at the wand tip
       until its turn came round. */
    .pkt     { transform-origin: 0 0;
               animation: pkt 6s cubic-bezier(.35,0,.5,1) infinite backwards; }
    .lid     { transform-origin: -38px 0;
               animation: lid 6s cubic-bezier(.34,1.5,.5,1) infinite; }
    .reveal-fade { animation: revealFade 6s ease-in-out infinite; }
    .reveal-rise { animation: revealRise 6s cubic-bezier(.2,1.5,.4,1) infinite; }
    .payoff  { animation: payoff 6s ease-in-out infinite; }

    @keyframes bob     { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
    @keyframes flick   { 0%,100%{opacity:.82}             50%{opacity:1} }
    @keyframes pulse   { 0%,100%{opacity:.5}              50%{opacity:1} }
    @keyframes spark   { 0%,100%{opacity:0}               50%{opacity:1} }
    @keyframes scan    { 0%{transform:translateY(-16px)}  100%{transform:translateY(16px)} }
    @keyframes twinkle { 0%,100%{opacity:.18} 45%{opacity:1} 70%{opacity:.42} }

    /* the gesture */
    @keyframes wand {
      0%, 14%   { transform: rotate(0deg); }
      20%, 30%  { transform: rotate(24deg); }
      38%, 100% { transform: rotate(0deg); }
    }
    @keyframes runes {
      0%, 16%   { opacity: .45; }
      21%, 32%  { opacity: 1; }
      40%, 100% { opacity: .45; }
    }
    /* the code, arcing along the rail */
    @keyframes pkt {
      0%, 24%   { opacity: 0; transform: translate(0,0) scale(.45); }
      28%       { opacity: 1; transform: translate(0,0) scale(1); }
      42%       { opacity: 1; transform: translate(285px,-14px) scale(.95); }
      56%       { opacity: 1; transform: translate(550px,28px) scale(.8); }
      61%, 100% { opacity: 0; transform: translate(550px,28px) scale(.35); }
    }
    /* the payoff — resting state is the finished one, so a still frame reads
       as the reward rather than a half-played cycle */
    @keyframes lid {
      0%, 7%    { transform: rotate(-26deg); }
      12%, 57%  { transform: rotate(0deg); }
      63%, 100% { transform: rotate(-26deg); }
    }
    @keyframes revealFade {
      0%, 6%    { opacity: 1; }
      11%, 57%  { opacity: 0; }
      63%, 100% { opacity: 1; }
    }
    @keyframes revealRise {
      0%, 6%    { transform: translate(0,0) scale(1); }
      11%, 57%  { transform: translate(32px,72px) scale(.25); }
      64%       { transform: translate(0,-8px) scale(1.14); }
      70%, 100% { transform: translate(0,0) scale(1); }
    }
    @keyframes payoff {
      0%, 7%    { opacity: 1; }
      13%, 57%  { opacity: .25; }
      63%, 100% { opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
  </style>
</defs>""")

add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

# ----------------------------------------------------- background: the void
# The island now hangs in open space. A cave ceiling framed the scene but
# fought the story — the reward is dug out of the dark, so the dark should be
# endless rather than a roof three metres up.

# two nebulae, off the thirds, to keep the emptiness from reading as flat black
add(f'<ellipse cx="{W*0.22:.0f}" cy="{H*0.30:.0f}" rx="300" ry="150" fill="url(#nebA)"/>')
add(f'<ellipse cx="{W*0.78:.0f}" cy="{H*0.22:.0f}" rx="340" ry="170" fill="url(#nebB)"/>')

# Starfield. Seeded so the layout is identical on every rebuild — an unseeded
# shuffle would churn the diff on every run.
rng = random.Random(20260802)
STAR_TINT = [PAL["ink"], PAL["cyan_hi"], PAL["cyan_wh"], PAL["gold_hi"], PAL["ink"]]
for i in range(150):
    sx = rng.uniform(-10, W + 10)
    sy = rng.uniform(-6, H * 0.82)
    # thin out the stars where the scene needs to read clearly
    if 150 < sy < 320 and 180 < sx < 960 and rng.random() < 0.72:
        continue
    size = rng.choice([1, 1, 1, 2, 2, 2, 3, 3, 4])
    tint = rng.choice(STAR_TINT)
    base = rng.uniform(0.30, 0.85)
    dur = rng.uniform(1.8, 4.6)
    delay = rng.uniform(0, 4.6)
    add(f'<rect class="twinkle" x="{sx:.0f}" y="{sy:.0f}" width="{size}" height="{size}" '
        f'fill="{tint}" opacity="{base:.2f}" '
        f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>')

# a handful of brighter four-point stars for punctuation
for bx, by, r in [(126, 58, 5), (352, 96, 4), (742, 46, 6), (1046, 88, 5), (612, 132, 4)]:
    add(f'<g class="twinkle" style="animation-duration:3.4s;animation-delay:{bx % 5 * .6:.1f}s">'
        f'<path d="M{bx},{by-r*2} L{bx+r*0.5},{by-r*0.5} L{bx+r*2},{by} L{bx+r*0.5},{by+r*0.5} '
        f'L{bx},{by+r*2} L{bx-r*0.5},{by+r*0.5} L{bx-r*2},{by} L{bx-r*0.5},{by-r*0.5} Z" '
        f'fill="{PAL["cyan_wh"]}"/></g>')

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
# The wand pivots at the hand, so the cast reads as a deliberate gesture
# rather than the whole sprite tilting.
add(f'<g class="wand" style="transform-origin:{WIZ_X+38.5}px {GY+2}px">')
add(f'<rect x="{WIZ_X+36}" y="{GY-88}" width="5" height="90" fill="{PAL["plank_r"]}"/>')
add(f'<g class="runes"><rect x="{WIZ_X+30}" y="{GY-104}" width="17" height="17" fill="{PAL["cyan"]}"/>'
    f'<rect x="{WIZ_X+34}" y="{GY-100}" width="9" height="9" fill="{PAL["cyan_wh"]}"/></g>')
add("</g>")
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
# ore blocks flanking the path
for tx in (410, 640):
    gxo, gyo = at(tx, V1 - 1)
    block(gxo, gyo, 1, PAL["stone_t"], PAL["stone_l"], PAL["stone_r"])
    xo, yo = iso(gxo, gyo, 1)
    for dx, dy in [(-10, -6), (6, -12), (0, 2)]:
        add(f'<rect class="pulse" x="{xo+dx}" y="{yo-BH+U/2+dy}" width="6" height="6" '
            f'fill="{PAL["cyan"]}" style="animation-delay:{tx%4*.5:.1f}s"/>')

# The spell itself: cards of code conjured at the wand tip that ride the rail
# into the chest. Positioning is a static outer group so the CSS transform on
# .pkt has nothing to fight with — a transform attribute would be overridden.
WAND_TIP = (WIZ_X + 72, GY - 82)   # tip position with the wand raised
CHEST_MOUTH = (872, 178)
DX, DY = CHEST_MOUTH[0] - WAND_TIP[0], CHEST_MOUTH[1] - WAND_TIP[1]

for i, (delay, dy0) in enumerate([(0.0, 0), (0.12, -7), (0.24, 6), (0.36, -3)]):
    add(f'<g transform="translate({WAND_TIP[0]},{WAND_TIP[1]+dy0})">')
    add(f'<g class="pkt" style="animation-delay:{delay}s">')
    add('<g transform="translate(-15,-11)">')
    add(f'<rect width="30" height="22" fill="#02060e" stroke="{PAL["cyan"]}" '
        f'stroke-width="1.6" opacity=".96"/>')
    for r, (w, c) in enumerate([(17, PAL["cyan_hi"]), (23, PAL["cyan"]), (13, PAL["gold"])]):
        add(f'<rect x="4" y="{5 + r * 5}" width="{w}" height="2.6" fill="{c}"/>')
    add("</g></g></g>")

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
    f'fill="url(#beam)" class="payoff"/>')

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
add(f'<g transform="translate({KX},{KY-30})"><g class="lid">'
    f'<path d="M-38,0 l38,19 l38,-19 l0,-9 l-38,-19 l-38,19 Z" fill="{PAL["gold"]}"/>'
    f'<path d="M-38,0 l38,19 l0,-9 l-38,-19 Z" fill="{PAL["gold_hi"]}"/></g></g>')

# The diamond is the reward, so it stays inside the chest until the lid is up,
# then rises to the focal point. Glow and sparkles ride the same group or they
# would hang in empty air while the gem is hidden.
add('<g class="reveal-fade">')
add(f'<g class="reveal-rise" style="transform-origin:{GEM_X}px {GEM_Y}px">')
add(f'<ellipse cx="{GEM_X}" cy="{GEM_Y}" rx="86" ry="78" fill="url(#gemGlow)"/>')
add('<g class="bob">')
add(f'<path d="M{GEM_X},{GEM_Y-38} l28,28 l-28,42 l-28,-42 Z" fill="{PAL["cyan"]}"/>')
add(f'<path d="M{GEM_X},{GEM_Y-38} l28,28 l-28,12 Z" fill="{PAL["cyan_hi"]}"/>')
add(f'<path d="M{GEM_X},{GEM_Y-38} l-28,28 l28,12 Z" fill="{PAL["cyan_wh"]}"/>')
add(f'<path d="M{GEM_X-28},{GEM_Y-10} l28,12 l28,-12 l-28,42 Z" fill="{PAL["cyan"]}" opacity=".72"/>')
add("</g>")
for ddx, ddy, sz, d in [(-52, -40, 6, .0), (48, -26, 5, .42), (-40, 32, 5, .84),
                        (56, 22, 6, .24), (8, -62, 5, .66)]:
    add(f'<rect class="spark" x="{GEM_X+ddx}" y="{GEM_Y+ddy}" width="{sz}" height="{sz}" '
        f'fill="{PAL["cyan_hi"]}" style="animation-delay:{d}s"/>')
add("</g></g>")

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
