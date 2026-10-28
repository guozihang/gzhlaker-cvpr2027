#!/usr/bin/env python3
"""Generate the round-7 framework figure (SVG -> PDF/PNG) with no external deps.

Order matches the frozen pipeline: strict/recovered tracks are refined into segments,
boundary choice runs per segment before merging, and the union is deduplicated on
both axes afterwards.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"

W, H = 1760, 1080
FONT = "DejaVu Sans, Helvetica, Arial, sans-serif"

BLUE = "#2b6cb0"
BLUE_FILL = "#ebf4ff"
GREEN = "#2f855a"
GREEN_FILL = "#e6fffa"
ORANGE = "#c05621"
ORANGE_FILL = "#fffaf0"
GRAY = "#4a5568"
LIGHT = "#f7fafc"
DARK = "#1a202c"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, lines, *, stroke=BLUE, fill=BLUE_FILL, dashed=False, fs=23, rx=10):
    dash = ' stroke-dasharray="10 7"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="3"{dash}/>']
    lh = fs * 1.28
    cy = y + h / 2 - (len(lines) - 1) * lh / 2 + fs * 0.35
    for i, line in enumerate(lines):
        out.append(f'<text x="{x + w/2:.1f}" y="{cy + i*lh:.1f}" font-family="{FONT}" '
                   f'font-size="{fs}" fill="{GRAY}" text-anchor="middle">{esc(line)}</text>')
    return "\n".join(out)


def arrow(x1, y1, x2, y2, colour=GRAY, width=3):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" '
            f'stroke-width="{width}" marker-end="url(#arrow)"/>')


def label(x, y, text, *, fs=26, colour=DARK, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{fs}" '
            f'font-weight="700" fill="{colour}" text-anchor="{anchor}">{esc(text)}</text>')


parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
         f'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/>'
         '</marker></defs>',
         f'<rect width="{W}" height="{H}" fill="white"/>']

parts += [
    label(60, 52, "(a) Strict sparse-to-tube branch", colour=BLUE),
    label(670, 52, "(b) Shadow recovery", colour=GREEN),
    label(1250, 52, "(c) Boundary choice (per segment)", colour=ORANGE),
]

# ---- (a) strict ----------------------------------------------------------
ax, aw = 60, 520
parts.append(box(ax, 85, aw, 62, ["Frozen ISC features, d = 256"], fs=23))
parts.append(box(ax, 175, aw, 62, ["stride-4 mutual top-1 anchors", "cos \u2265 0.70"], fs=22))
parts.append(box(ax, 265, aw, 62, ["RANSAC tracks: inlier \u2265 5", "slope \u2208 [0.5, 2]"], fs=22))
parts.append(box(ax, 355, aw, 62, ["tube: \u00b112 frames around the fit"], fs=22))
parts.append(box(ax, 445, aw, 70, ["local DP on band", "steps (1,1), (1,2), (2,1); \u22644 paths"], fs=21))
parts.append(box(ax, 545, aw, 54, ["S_main  (source = main)"], fs=21))
for y, h in [(85, 62), (175, 62), (265, 62), (355, 62), (445, 70)]:
    parts.append(arrow(ax + aw / 2, y + h, ax + aw / 2, y + h + 26))

# ---- (b) recovery --------------------------------------------------------
bx, bw = 670, 500
parts.append(box(bx, 85, bw, 54, ["same anchors (no new matches)"], fs=22, stroke=GREEN, fill=GREEN_FILL))
parts.append(box(bx, 168, bw, 66, ["shadow RANSAC: inlier \u2265 3, \u226412 tracks"], fs=21, stroke=GREEN, fill=GREEN_FILL))
parts.append(box(bx, 263, bw, 88, ["hard geometric gate: slope, bounds,", "support, order, residuals \u2264 4, gaps \u2264 24"],
                 fs=20, stroke=GREEN, fill=GREEN_FILL))
parts.append(box(bx, 380, bw, 66, ["Noul question: p(copy)"], fs=22, stroke=GREEN, fill=GREEN_FILL))
parts.append(box(bx, 475, bw, 66, ["p \u2265 0.75 \u2192 tube  (same aligner)"], fs=21, stroke=GREEN, fill=GREEN_FILL))
parts.append(box(bx, 570, bw, 54, ["S_rec  (source = recovered)"], fs=21, stroke=GREEN, fill=GREEN_FILL))
for y1, y2 in [(139, 165), (234, 260), (351, 377), (446, 472), (541, 567)]:
    parts.append(arrow(bx + bw / 2, y1, bx + bw / 2, y2))
parts.append(f'<text x="{bx + bw + 12}" y="415" font-family="{FONT}" font-size="18" fill="{GRAY}">p &lt; 0.75: drop</text>')

# ---- (c) boundary --------------------------------------------------------
cx, cw = 1250, 450
parts.append(box(cx, 85, cw, 54, ["candidate segments from (a) and (b)"], fs=20, stroke=ORANGE, fill=ORANGE_FILL))
parts.append(box(cx, 168, cw, 84, ["C0 keep | C1 left | C2 right", "C3 both | C4 shrink"], fs=21,
                 stroke=ORANGE, fill=ORANGE_FILL))
parts.append(box(cx, 281, cw, 96, ["revalidate every candidate:", "added frames cos \u2265 0.6, duration,",
                                   "support, \u22642 weak frames"], fs=19, stroke=ORANGE, fill=ORANGE_FILL))
parts.append(box(cx, 406, cw, 66, ["Choice: min(conf, p) \u2265 0.65, else C0"], fs=19,
                 stroke=ORANGE, fill=ORANGE_FILL))
parts.append(box(cx, 501, cw, 54, ["boundary-selected segments"], fs=20, stroke=ORANGE, fill=ORANGE_FILL))
for y1, y2 in [(139, 165), (252, 278), (377, 403), (472, 498)]:
    parts.append(arrow(cx + cw / 2, y1, cx + cw / 2, y2))

# ---- merge and output ----------------------------------------------------
parts.append(box(60, 700, 1640, 84, ["merge S_main \u222a S_rec and boundary-selected segments  \u2192  dual-axis dedupe:",
                                    "duplicate iff IoU_A \u2265 0.8  AND  IoU_B \u2265 0.8"],
                 fs=22, stroke=GRAY, fill=LIGHT))
parts.append(arrow(ax + aw / 2, 599, ax + aw / 2, 697))
parts.append(arrow(bx + bw / 2, 624, bx + bw / 2, 697))
parts.append(arrow(cx + cw / 2, 555, cx + cw / 2, 697))
parts.append(box(700, 860, 360, 60, ["S  (\u226464 segments per pair)"], fs=20, stroke=GRAY, fill=LIGHT))
parts.append(arrow(880, 784, 880, 857))

parts += [
    f'<text x="60" y="1006" font-family="{FONT}" font-size="18" fill="{GRAY}">'
    'Model never writes coordinates or scores; every output carries its source and a fallback flag; '
    'disabling the interface reproduces the strict branch.</text>',
    f'<text x="60" y="1038" font-family="{FONT}" font-size="18" fill="{GRAY}">'
    'Boundary choice runs per segment before merging; the independent loose sparse branch is disabled in this version.</text>',
    "</svg>",
]

OUT.mkdir(exist_ok=True)
svg = OUT / "framework.svg"
svg.write_text("\n".join(parts), encoding="utf-8")
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(OUT / "framework.pdf"), str(svg)], check=True)
subprocess.run(["rsvg-convert", "-f", "png", "-d", "150", "-p", "150",
                "-o", str(OUT / "framework.png"), str(svg)], check=True)
print("wrote", OUT / "framework.pdf")
