#!/usr/bin/env python3
"""Generates the pixel-lettered SVGs the README uses in place of plain headings.

Why images: GitHub sanitises README markdown, so CSS, <style>, <font> and style
attributes are all stripped. There is no way to set a typeface or a size on
ordinary markdown text. Rendering the words as SVG is the only route to real
pixel lettering, and it stays crisp at any zoom because every glyph is a rect.

Run:  python3 tools/build_text.py     (writes assets/*.svg)
"""

from html import escape
from pathlib import Path

import pixelfont as pf

GOLD, GOLD_HI = "#f6b23a", "#ffcb5b"
INK, SHADOW = "#e6f0fb", "#02060e"

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def heading(text, px=7, pad=10):
    """A section title: gold pixel caps with a hard drop shadow, one row tall."""
    w = int(pf.text_width(text, px) + pad * 2)
    h = int(pf.CELL_H * px + pad * 2)
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{escape(text, quote=True)}">'
    ]
    # offset copy first, so the shadow sits behind without needing a filter
    body.append(pf.emit(text, pad + px, pad + px, px, fill=SHADOW))
    body.append(pf.emit(text, pad, pad, px, fill=GOLD))
    # a lit top edge on every glyph, the way beveled pixel type reads in-game
    body.append(f'<g opacity=".55">{pf.emit(text, pad, pad, px, fill=GOLD_HI)}</g>'
                .replace('height="%s"' % px, 'height="%s"' % (px / 2), 1))
    body.append("</svg>")
    return "".join(body), w, h


def glossy_quote(lines, px=6, pad=16, lead=1.7):
    """The quote, lit by a specular band that travels across the letters.

    The band is a userSpaceOnUse gradient whose x1/x2 slide together, so its
    width stays fixed while it sweeps — a moving highlight rather than a colour
    wash. SMIL is used rather than CSS because GitHub serves the file straight
    to an <img>, where a stylesheet would be inert anyway.
    """
    w = int(max(pf.text_width(l, px) for l in lines) + pad * 2)
    h = int(len(lines) * pf.CELL_H * px * lead + pad * 2)
    band = int(w * 0.26)   # tight band = a glint, not a colour wash
    dur = "5s"

    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" '
        f'aria-label="{escape(" ".join(lines), quote=True)}">',
        "<defs>",
        f'<linearGradient id="gloss" gradientUnits="userSpaceOnUse" '
        f'x1="{-band}" y1="0" x2="0" y2="0">',
        '<stop offset="0" stop-color="#2f9fe0"/>',
        '<stop offset=".38" stop-color="#43c9ff"/>',
        '<stop offset=".46" stop-color="#c9f2ff"/>',
        '<stop offset=".5" stop-color="#ffffff"/>',
        '<stop offset=".54" stop-color="#c9f2ff"/>',
        '<stop offset=".62" stop-color="#43c9ff"/>',
        '<stop offset="1" stop-color="#2f9fe0"/>',
        f'<animate attributeName="x1" from="{-band}" to="{w}" dur="{dur}" '
        f'repeatCount="indefinite"/>',
        f'<animate attributeName="x2" from="0" to="{w + band}" dur="{dur}" '
        f'repeatCount="indefinite"/>',
        "</linearGradient>",
        '<filter id="soft" x="-20%" y="-40%" width="140%" height="180%">',
        '<feGaussianBlur stdDeviation="2.2" result="b"/>',
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>',
        "</filter>",
        "</defs>",
    ]
    for i, line in enumerate(lines):
        y = pad + i * pf.CELL_H * px * lead
        x = (w - pf.text_width(line, px)) / 2
        body.append(pf.emit(line, x + 2, y + 2, px, fill=SHADOW))
    body.append('<g filter="url(#soft)" fill="url(#gloss)">')
    for i, line in enumerate(lines):
        y = pad + i * pf.CELL_H * px * lead
        x = (w - pf.text_width(line, px)) / 2
        body.append(pf.emit(line, x, y, px))
    body.append("</g></svg>")
    return "".join(body), w, h


HEADINGS = {
    "about": "ABOUT",
    "stack": "TECH STACK",
    "experience": "EXPERIENCE",
    "builds": "FEATURED BUILDS",
    "contributions": "CONTRIBUTIONS",
    "connect": "CONNECT",
}

QUOTE = [
    "\"SUCCESS ISN'T THE TREASURE YOU FIND -",
    "IT'S THE WIZARD YOU BECOME CHASING IT.\"",
]

if __name__ == "__main__":
    for slug, text in HEADINGS.items():
        svg, w, h = heading(text)
        (ASSETS / f"h-{slug}.svg").write_text(svg)
        print(f"  assets/h-{slug}.svg  {w}x{h}  {len(svg):,}b")

    svg, w, h = glossy_quote(QUOTE)
    (ASSETS / "quote.svg").write_text(svg)
    print(f"  assets/quote.svg  {w}x{h}  {len(svg):,}b")
