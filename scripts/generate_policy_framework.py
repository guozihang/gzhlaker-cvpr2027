#!/usr/bin/env python3
"""Draw the proposed pair-level policy and two alternative localization pathways.

Vector schematic only: no experimental values or model outputs are generated.
Requires Python's standard library and rsvg-convert.
"""
from pathlib import Path
import html
import subprocess

OUT = Path(__file__).resolve().parents[1] / "figures"
W, H = 1800, 570
FONT = "Times New Roman, Times, serif"
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
    'markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
    'fill="#444"/></marker></defs>',
    f'<rect width="{W}" height="{H}" fill="white"/>',
]


def text(x, y, value, size=27, bold=False, anchor="middle", color="#222"):
    weight = ' font-weight="bold"' if bold else ""
    parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}"'
                 f'{weight} fill="{color}" text-anchor="{anchor}">{html.escape(value)}</text>')


def box(x, y, w, h, lines, fill="#f5f5f5", stroke="#666", size=26):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    first = y + h / 2 - (len(lines)-1) * size * 0.65 + size * 0.33
    for i, line in enumerate(lines):
        text(x+w/2, first+i*size*1.3, line, size)


def arrow(points):
    xy = " ".join(f"{x},{y}" for x, y in points)
    parts.append(f'<polyline points="{xy}" fill="none" stroke="#444" stroke-width="2.5" '
                 'marker-end="url(#arrow)"/>')


text(30, 42, "(a) Front-end policy", 31, True, "start")
text(820, 42, "(b) High-capacity main branch", 31, True, "start")
text(820, 345, "(c) Lightweight acceleration branch", 31, True, "start")

box(30, 220, 160, 112, ["Query A", "Reference B"])
box(235, 199, 225, 154, ["Compact preview", "Sample frames", "Encode + correlate"], "#edf4ee", "#53765a", 25)
box(510, 220, 210, 112, ["Policy network", "Choose a branch"], "#edf4ee", "#53765a", 26)
arrow([(190,276),(235,276)])
arrow([(460,276),(510,276)])

for x, w, lines in [
    (820,220,["Trainable", "frame encoder"]),
    (1090,230,["Learnable", "similarity matrix"]),
    (1370,190,["2D object", "detector"]),
]:
    box(x, 87, w, 112, lines, "#edf1f8", "#506c90")
arrow([(1040,143),(1090,143)])
arrow([(1320,143),(1370,143)])
text(1190, 236, "Jointly trained with localization supervision", 25, color="#506c90")

for x, w, lines in [
    (820,220,["Fixed descriptors", "Direct similarity"]),
    (1090,230,["Anchor", "candidates"]),
    (1370,190,["RANSAC", "Track intervals"]),
]:
    box(x, 380, w, 112, lines, "#faf1e8", "#97724e", 25)
arrow([(1040,436),(1090,436)])
arrow([(1320,436),(1370,436)])

arrow([(720,276),(770,276),(770,143),(820,143)])
arrow([(720,276),(770,276),(770,436),(820,436)])
text(770, 116, "Hard", 24)
text(770, 477, "Regular", 24)

box(1610, 220, 165, 112, ["Copied", "interval pairs"], size=25)
arrow([(1560,143),(1590,143),(1590,248),(1610,248)])
arrow([(1560,436),(1590,436),(1590,304),(1610,304)])
text(30, 414, "Inference: execute one branch per pair.", 26, anchor="start")
text(30, 452, "Training: compare both branches offline", 25, anchor="start")
text(30, 484, "to supervise the policy with error and cost.", 25, anchor="start")
text(900, 548, "All pathways are a proposed design; no benchmark results are depicted.", 24, color="#555")
parts.append("</svg>")
OUT.mkdir(exist_ok=True)
svg = OUT / "framework.svg"
svg.write_text("\n".join(parts) + "\n", encoding="utf-8")
for fmt in ("pdf", "png"):
    subprocess.run(["rsvg-convert", "-f", fmt, "-o", str(OUT / f"framework.{fmt}"), str(svg)], check=True)
print("Generated policy-guided framework.svg, framework.pdf, framework.png")
