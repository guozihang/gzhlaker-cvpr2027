#!/usr/bin/env python3
"""Generate the round-7 framework figure (SVG -> PDF/PNG) with no external deps.

Layout follows the frozen pipeline: strict and shadow-recovery branches produce segments,
boundary candidates are generated and revalidated per segment, and the refined union is
deduplicated on both axes afterwards. Styling is deliberately plain: serif labels, thin
strokes, light fills, no colour-coded headings.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"

W, H = 1800, 930
FONT = "DejaVu Serif, Times New Roman, Times, serif"

STRICT_STROKE = "#3d5a73"
STRICT_FILL = "#eef2f7"
REC_STROKE = "#4a6b52"
REC_FILL = "#eef4ee"
BND_STROKE = "#7a5c42"
BND_FILL = "#f7f1ea"
MERGE_STROKE = "#444444"
MERGE_FILL = "#f2f2f2"
INK = "#1a1a1a"
MUTED = "#555555"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, lines, *, stroke, fill, fs=25, rx=2, dashed=False):
    dash = ' stroke-dasharray="9 6"' if dashed else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="2"{dash}/>']
    lh = fs * 1.3
    cy = y + h / 2 - (len(lines) - 1) * lh / 2 + fs * 0.36
    for i, line in enumerate(lines):
        out.append(f'<text x="{x + w/2:.1f}" y="{cy + i*lh:.1f}" font-family="{FONT}" '
                   f'font-size="{fs}" fill="{INK}" text-anchor="middle">{esc(line)}</text>')
    return "\n".join(out)


def arrow(x1, y1, x2, y2, *, colour="#333333", width=2.2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" '
            f'stroke-width="{width}" marker-end="url(#arrow)"/>')


def poly(points, *, colour="#333333", width=2.2):
    pts = " ".join(f"{x},{y}" for x, y in points)
    return (f'<polyline points="{pts}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" marker-end="url(#arrow)"/>')


def dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="4.5" fill="#333333"/>'


def label(x, y, text, *, fs=28):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{fs}" '
            f'font-weight="bold" fill="{INK}" text-anchor="start">{esc(text)}</text>')


def note(x, y, text, *, fs=21):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{fs}" '
            f'fill="{MUTED}" text-anchor="start">{esc(text)}</text>')


parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" '
         f'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#333333"/>'
         '</marker></defs>',
         f'<rect width="{W}" height="{H}" fill="white"/>']

parts += [
    label(60, 44, "(a) Strict branch"),
    label(60, 474, "(b) Shadow recovery"),
    label(1390, 44, "(c) Boundary and merge"),
]

# ---- (a) strict ----------------------------------------------------------
ax, aw = 60, 1230
a_boxes = [
    (78, 78, ["frozen ISC features (d = 256); stride-4", "mutual top-1 anchors, cos \u2265 0.70"]),
    (172, 58, ["RANSAC tracks: \u2265 5 inliers, slope \u2208 [0.5, 2]"]),
    (244, 58, ["tube: \u00b112 frames around the fit"]),
    (316, 58, ["local dynamic program (\u2264 4 paths)"]),
]
for y, h, lines in a_boxes:
    parts.append(box(ax, y, aw, h, lines, stroke=STRICT_STROKE, fill=STRICT_FILL))
parts.append(box(ax, 388, aw, 52, ["S_main (strict segments)"], stroke=STRICT_STROKE, fill=STRICT_FILL))
for y, h, _ in a_boxes[1:] + [(388, 52, None)]:
    parts.append(arrow(ax + aw / 2, y - 14, ax + aw / 2, y + 2))

# ---- (b) recovery --------------------------------------------------------
b_boxes = [
    (500, 58, ["same anchors (no new matches)"]),
    (574, 58, ["shadow RANSAC: \u2265 3 inliers, \u2264 12 tracks"]),
    (646, 78, ["hard gate: slope, bounds, support,", "residuals \u2264 4, gaps \u2264 24"]),
    (740, 58, ["Noul p(copy) \u2265 0.75 \u2192 same tube and aligner"]),
]
for y, h, lines in b_boxes:
    parts.append(box(ax, y, aw, h, lines, stroke=REC_STROKE, fill=REC_FILL))
parts.append(box(ax, 814, aw, 52, ["S_rec (recovered segments)"], stroke=REC_STROKE, fill=REC_FILL))
for y, h, _ in b_boxes[1:] + [(814, 52, None)]:
    parts.append(arrow(ax + aw / 2, y - 14, ax + aw / 2, y + 2))

# ---- bus from both branches into (c) ------------------------------------
BUS = 1330
parts.append(f'<line x1="{BUS}" y1="212" x2="{BUS}" y2="840" stroke="#333333" stroke-width="2.2"/>')
parts.append(arrow(ax + aw, 414, BUS + 1, 414))
parts.append(arrow(ax + aw, 840, BUS + 1, 840))
parts.append(dot(BUS, 414))
parts.append(dot(BUS, 840))
parts.append(arrow(BUS, 212, 1388, 212))

# ---- (c) boundary and merge ---------------------------------------------
cx, cw = 1390, 350
c_boxes = [
    (170, 84, ["C0\u2013C4 boundary candidates", "per segment"], BND_STROKE, BND_FILL, 23),
    (278, 104, ["revalidate on local features:", "cos \u2265 0.6, support,", "\u2264 2 weak frames"], BND_STROKE, BND_FILL, 22),
    (406, 76, ["Choice min(conf, p) \u2265 0.65", "else keep C0"], BND_STROKE, BND_FILL, 23),
    (506, 56, ["refined segments"], BND_STROKE, BND_FILL, 23),
    (586, 88, ["union \u2192 dual-axis dedupe", "IoU_A \u2265 0.8 and IoU_B \u2265 0.8"], MERGE_STROKE, MERGE_FILL, 22),
    (698, 64, ["S: \u2264 64 segments per pair"], MERGE_STROKE, MERGE_FILL, 23),
]
for y, h, lines, stroke, fill, fs in c_boxes:
    parts.append(box(cx, y, cw, h, lines, stroke=stroke, fill=fill, fs=fs))
for y1, y2 in [(254, 276), (382, 404), (482, 504), (562, 584), (674, 696)]:
    parts.append(arrow(cx + cw / 2, y1 + 2, cx + cw / 2, y2 - 2))


parts.append("</svg>")

OUT.mkdir(exist_ok=True)
svg = OUT / "framework.svg"
svg.write_text("\n".join(parts), encoding="utf-8")
subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(OUT / "framework.pdf"), str(svg)], check=True)
subprocess.run(["rsvg-convert", "-f", "png", "-d", "150", "-p", "150",
                "-o", str(OUT / "framework.png"), str(svg)], check=True)
print("wrote", OUT / "framework.pdf")
