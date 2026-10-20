#!/usr/bin/env python3
"""Editable Fig. 2 drawn from sec/3_method.tex, not from benchmark outputs.

The diagram uses illustrative coordinates and matrices. It depicts the proposed
zero-floored local DP and a proposed JEV extension named "seltive model" by the user.
The extension consumes selected candidate evidence and original video frames;
its selection policy, model backend and score fusion are not implemented here.
Python standard library + rsvg-convert; run from any directory.
"""
from html import escape
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
INK = '#17283C'
MUTED = '#526477'
BORDER = '#C6D1DD'
BLUE = '#2D69AD'
TEAL = '#16847A'
ORANGE = '#C37827'
PURPLE = '#7962A6'
BG = '#F7F9FC'


class Canvas:
    def __init__(self):
        self.parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1760" height="1220" viewBox="0 0 1760 1220">',
                      '<title>FastVCL: sparse-to-tube video copy localization framework</title>',
                      '<desc>Proposed sparse-to-tube method with two budgeted insertions of one shared selective visual-decision model named seltive model: anchor filtering before RANSAC (A0 to A1) and fragment fusion after candidate extraction (C0 to Y). Both call sites share one pair budget, cache and model revision, and abstain on uncertainty or failure; unselected, uncertain and failed items keep their core evidence. Matrices and trajectories are schematic, not empirical outputs.</desc>',
                      '<defs>',
                      '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#526477"/></marker>',
                      '<marker id="blueArrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="#2D69AD"/></marker>',
                      '</defs>']
        self.rect(0, 0, 1760, 1220, '#FFFFFF', radius=0)

    def rect(self, x, y, w, h, fill='#FFFFFF', stroke='none', radius=9, width=1.5):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def text(self, x, y, value, size=25, color=INK, weight=400, anchor='start', italic=False):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" font-style="{"italic" if italic else "normal"}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')

    def line(self, x1, y1, x2, y2, color=BORDER, width=2, dash='', arrow=False):
        self.path([(x1, y1), (x2, y2)], color, width, dash, arrow)

    def path(self, points, color=MUTED, width=2.5, dash='', arrow=False):
        coords = ' '.join(f'{x},{y}' for x, y in points)
        marker = 'blueArrow' if color == BLUE else 'arrow'
        extra = (f' stroke-dasharray="{dash}"' if dash else '') + (f' marker-end="url(#{marker})"' if arrow else '')
        self.parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{extra}/>')

    def circle(self, x, y, r, color, stroke='none', width=1.5):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="{width}"/>')

    def poly(self, points, fill, opacity=1):
        coords=' '.join(f'{x},{y}' for x,y in points)
        self.parts.append(f'<polygon points="{coords}" fill="{fill}" opacity="{opacity}"/>')

    def cross(self, x, y, color='#A5B1BE', r=4):
        self.line(x-r,y-r,x+r,y+r,color,2)
        self.line(x-r,y+r,x+r,y-r,color,2)

    def panel(self, x, w, number, title, subtitle, accent):
        self.rect(x,76,w,672,BG,BORDER,12)
        self.rect(x,76,w,7,accent,radius=3)
        self.circle(x+29,115,16,accent)
        self.text(x+29,122,str(number),23,'#FFFFFF',700,'middle')
        self.text(x+53,124,title,28,INK,700)
        self.text(x+20,156,subtitle,24,MUTED)

    def save(self):
        svg = OUT / 'fig_2_framework.svg'
        svg.write_text('\n'.join(self.parts + ['</svg>'])+'\n',encoding='utf-8')
        for fmt in ('pdf','png'):
            subprocess.run(['rsvg-convert','--format',fmt,'--output',str(svg.with_suffix('.'+fmt)),str(svg)],check=True)
        print('fig_2_framework: editable SVG, vector PDF, PNG')


def coord(x,y,w,h,a,b):
    return x+a*w,y+(1-b)*h


def plot_axes(c,x,y,w,h):
    c.line(x,y+h,x+w+9,y+h,MUTED,1.8,arrow=True)
    c.line(x,y+h,x,y-5,MUTED,1.8,arrow=True)
    c.text(x+w+12,y+h+9,'i',23,MUTED,italic=True)
    c.text(x-15,y,'j',23,MUTED,italic=True)


ANCHORS = [(.13,.19),(.21,.26),(.29,.35),(.37,.42),(.64,.71),(.73,.79),(.83,.89)]
NOISE = [(.15,.77),(.48,.18),(.55,.87),(.85,.29),(.46,.58)]


def anchors(c,x,y,w,h,noise=False):
    for a,b in ANCHORS:
        c.circle(*coord(x,y,w,h,a,b),5.5,BLUE,'#FFFFFF',1)
    if noise:
        for a,b in NOISE:
            c.cross(*coord(x,y,w,h,a,b))


def feature_matrix(c,x,y,label,dim,color):
    c.text(x,y,label,26,INK,600)
    # Stylized descriptor rows: fixed illustrative colors, not feature values.
    palette = ['#E7EFF8','#CCDDF0','#A5C4E7','#78A4D5',color] if color == BLUE else ['#F0EDF7','#DBD4EC','#C2B6DC','#A18BC6',color]
    for row in range(7):
        for col in range(8):
            c.rect(x+col*23,y+18+row*16,20,13,palette[(row*3+col*2+row*col)%5],radius=1)
    c.text(x+91,y+157,dim,25,color,anchor='middle')


def build_framework():
    c=Canvas()
    c.text(20,43,'FastVCL',34,INK,700)
    c.text(186,42,'Sparse-to-tube video copy localization',28,INK)
    c.text(1740,40,'PROPOSED METHOD · SCHEMATIC',23,MUTED,600,'end')
    c.panel(20,278,1,'Fixed features','Query A / reference B',BLUE)
    c.panel(336,404,2,'Sparse matching','Sample → compare → retain',BLUE)
    c.panel(778,440,3,'Temporal proposals','Fit → validate → split',TEAL)
    c.panel(1256,484,4,'Local refinement','Align → recover → candidates',PURPLE)

    # 1. Inputs and a shared normalized-descriptor view.
    feature_matrix(c,66,213,'Query A','F_A: M × 256',BLUE)
    feature_matrix(c,66,423,'Reference B','F_B: N × 256',PURPLE)
    c.path([(252,290),(266,290),(266,610),(159,610),(159,626)],MUTED,2.2,arrow=True)
    c.line(252,501,266,501,MUTED,2.2)
    c.rect(43,635,232,69,'#FFFFFF',BORDER)
    c.text(159,663,'L2 normalization',25,INK,600,'middle')
    c.text(159,691,'+ validity masks',24,MUTED,anchor='middle')
    c.path([(298,668),(317,668),(317,208),(336,208)],MUTED,2.8,arrow=True)

    # 2. Sampling strips, a tiled score computation, and sparse retained output.
    for row,base_y,offset,color in [('A',205,0,BLUE),('B',242,1,PURPLE)]:
        c.text(358,base_y+6,row,25,color,600)
        for k in range(15):
            selected=(k-offset)%3==0
            c.rect(394+k*21,base_y-12,15,18,color if selected else '#E1E7EF',radius=2)
    c.text(538,283,'Sampling plans g ∈ G',25,INK,anchor='middle')
    gx,gy=375,306
    for row in range(6):
        for col in range(10):
            selected=(col == (row+1)%10 or (row==3 and col==8))
            c.rect(gx+col*20,gy+row*19,17,16,BLUE if selected else '#DBE5F0',radius=1)
    c.rect(gx-4,gy-4,105,62,'none',TEAL,2,2)
    c.text(603,331,'Row Top-K',23,MUTED)
    c.text(650,366,'∩',33,INK,anchor='middle')
    c.text(603,401,'Col. Top-K',23,MUTED)
    c.text(538,452,'Tiled cosine · mutual Top-K',25,INK,600,'middle')
    c.line(538,468,538,491,MUTED,2.3,arrow=True)
    plot_axes(c,389,505,287,147)
    anchors(c,389,505,287,147,noise=True)
    c.text(538,695,'Deduplicate coordinates; cap',24,MUTED,anchor='middle')
    c.text(538,730,'Anchor set {(i, j, Sᵢⱼ)}',25,BLUE,600,'middle')

    # 3. Geometric support and finite, split tube domains.
    c.text(998,201,'RANSAC: j ≈ αᵣ i + βᵣ',26,INK,600,'middle')
    x,y,w,h=835,229,308,139
    plot_axes(c,x,y,w,h)
    c.line(*coord(x,y,w,h,.10,.16),*coord(x,y,w,h,.87,.93),MUTED,2,'6 5')
    for lo,hi,color in [(.13,.37,TEAL),(.64,.83,ORANGE)]:
        c.line(*coord(x,y,w,h,lo,lo+.06),*coord(x,y,w,h,hi,hi+.06),color,4)
    anchors(c,x,y,w,h,noise=True)
    c.text(998,408,'Distinct-time support on A and B',24,MUTED,anchor='middle')
    c.rect(807,427,382,51,'#FFFFFF',BORDER)
    c.text(998,461,'Split long gaps → refit / validate',24,INK,600,'middle')
    c.line(998,483,998,503,MUTED,2.2,arrow=True)
    x,y,w,h=835,520,308,139
    # Two separated support intervals on the same temporal line.
    for lo,hi,color in [(.09,.42,TEAL),(.60,.88,ORANGE)]:
        band=[coord(x,y,w,h,lo,lo+.06-.065),coord(x,y,w,h,hi,hi+.06-.065),
              coord(x,y,w,h,hi,hi+.06+.065),coord(x,y,w,h,lo,lo+.06+.065)]
        c.poly(band,color,.18)
        c.line(*coord(x,y,w,h,lo,lo+.06),*coord(x,y,w,h,hi,hi+.06),color,2.5)
    plot_axes(c,x,y,w,h)
    anchors(c,x,y,w,h)
    c.text(820,697,'Extend A: e_A',23,MUTED)
    c.text(1190,697,'B band: ±wᵣ',23,MUTED,anchor='end')
    c.text(998,730,'Finite Tᵣ: ℓᵣ ≤ i < uᵣ',25,TEAL,600,'middle')
    c.path([(1218,722),(1237,722),(1237,202),(1256,202)],MUTED,2.8,arrow=True)

    # 4. The raw full-resolution descriptors and tube domain meet at local scoring.
    c.rect(1280,178,420,50,'#FFFFFF',BORDER)
    c.text(1490,211,'Cosine scores only inside Tᵣ',25,INK,600,'middle')
    c.line(1490,232,1490,252,MUTED,2.2,arrow=True)
    gx,gy,cell=1325,268,24
    for j in range(8):
        for i in range(13):
            valid=abs(i-j-2)<=2
            c.rect(gx+i*cell,gy+(7-j)*cell,21,21,'#DCEDE8' if valid else '#E9EDF2',radius=1)
    chosen=[(2,0),(3,1),(4,2),(5,3),(7,4),(8,5),(9,6),(10,7)]
    path=[(gx+i*cell+10.5,gy+(7-j)*cell+10.5) for i,j in chosen]
    c.path(path,BLUE,4.3,arrow=True)
    for px,py in path[:-1]: c.circle(px,py,3.5,'#FFFFFF',BLUE,1.5)
    c.text(gx-20,gy+8,'j',23,MUTED,italic=True)
    c.text(gx+13*cell+6,gy+8*cell,'i',23,MUTED,italic=True)
    c.text(1490,495,'Local DP with a zero restart',25,INK,600,'middle')
    c.text(1490,528,'Hᵢⱼ = max{0, rᵢⱼ, continuation}',24,PURPLE,anchor='middle')
    c.text(1490,568,'Traceback → trim → score',25,INK,anchor='middle')
    c.path([(1702,555),(1720,555),(1720,260),(1660,260)],MUTED,1.8,'5 5',True)
    c.text(1490,600,'↻ Block matched cells; repeat',23,MUTED,anchor='middle')
    # Matched output intervals share colors, not numeric evidence.
    tx,tw=1322,361
    for label,yy,shift in [('A',637,0),('B',682,.06)]:
        c.text(1289,yy+8,label,25,INK,600)
        c.line(tx,yy,tx+tw,yy,MUTED,2)
        for lo,hi,color in [(.13,.37,TEAL),(.64,.83,ORANGE)]:
            c.rect(tx+(lo+shift)*tw,yy-9,(hi-lo)*tw,18,color,radius=3)
    for lo,hi,color in [(.13,.37,TEAL),(.64,.83,ORANGE)]:
        c.poly([(tx+lo*tw,647),(tx+hi*tw,647),(tx+(hi+.06)*tw,672),(tx+(lo+.06)*tw,672)],color,.10)
    c.text(1490,727,'Score q · min(IoU_A, IoU_B) dedup.',24,INK,600,'middle')

    # Two insertion points of one shared, budgeted visual-decision model. This is a
    # figure-level design; it does not claim the historical prototype implements it.
    c.text(880,826,'ONE SHARED MODEL · TWO CALL SITES',22,ORANGE,600,'middle')
    for x,w in [(20,460),(540,680),(1280,460)]:
        c.rect(x,845,w,207,'#FFF9F1','#D6BC98',12)

    # 1. Anchor decision before RANSAC: A0 -> A1.
    c.circle(52,884,16,ORANGE)
    c.text(52,891,'1',22,'#FFFFFF',700,'middle')
    c.text(76,891,'Anchor decision',27,INK,700)
    for yy,t,color,weight in [(928,'A0 → budgeted hard-sample selection',MUTED,400),
                              (958,'NOT_COPY + margin → drop',MUTED,400),
                              (988,'COPY / uncertain / fail → keep',MUTED,400),
                              (1020,'A1 = A0 \\ D(a), then refit',INK,600)]:
        c.text(250,yy,t,22,color,weight,'middle')

    # 2. One shared model, one budget and cache, two call sites.
    c.text(880,887,'seltive model',33,INK,700,'middle')
    c.text(880,918,'one shared external model',22,MUTED,anchor='middle')
    c.text(880,952,'COPY / NOT_COPY / UNCERTAIN',21,MUTED,600,'middle')
    c.text(880,982,'MERGE / KEEP_SEPARATE',21,MUTED,600,'middle')
    c.text(880,1014,'abstain · failure keeps evidence',21,MUTED,anchor='middle')
    c.text(880,1044,'one budget K · cache · one revision',21,ORANGE,600,'middle')

    # 3. Fusion decision after candidates: C0 -> Y.
    c.circle(1312,884,16,TEAL)
    c.text(1312,891,'2',22,'#FFFFFF',700,'middle')
    c.text(1336,891,'Fusion decision',27,INK,700)
    for yy,t,color,weight in [(928,'C0 → legal edges (G, gaps)',MUTED,400),
                              (958,'same copy? + Conn',MUTED,400),
                              (988,'M = G ∧ Conn ∧ margin',MUTED,400),
                              (1020,'merge / keep · one round',INK,600),
                              (1046,'→ Y final intervals',INK,600)]:
        c.text(1510,yy,t,22,color,weight,'middle')

    # 4. Frames are the additional input of the shared model, not of one call site.
    c.rect(20,1072,1720,40,'#FFF9F1','#D6BC98',10)
    c.text(880,1098,'A/B original frames + verified index → frame map',22,INK,600,'middle')
    c.path([(880,1072),(880,1052)],ORANGE,2.4,arrow=True)

    # Directed inserts: A0 down into the anchor call site, A1 back into proposals.
    c.path([(538,748),(538,810),(250,810),(250,845)],MUTED,2.5,arrow=True)
    c.path([(430,845),(430,790),(790,790),(790,748)],MUTED,2.5,arrow=True)
    # Questions to the shared model, verdicts back, for both call sites.
    c.path([(480,930),(540,930)],ORANGE,2.4,arrow=True)
    c.path([(540,962),(480,962)],ORANGE,2.4,arrow=True)
    c.path([(1220,930),(1280,930)],ORANGE,2.4,arrow=True)
    c.path([(1280,962),(1220,962)],ORANGE,2.4,arrow=True)
    # Candidate intervals reach the fusion call site; Y leaves the last box.
    c.path([(1498,748),(1498,845)],MUTED,2.5,arrow=True)
    c.text(556,798,'A0',22,MUTED,600,'middle')
    c.text(806,780,'A1',22,MUTED,600,'middle')
    c.text(1518,812,'C0',22,MUTED,600,'end')

    # Reuse path: local similarities require full descriptors, not just sparse anchors.
    c.circle(159,704,4,BLUE)
    c.path([(159,708),(159,765),(8,765),(8,1135),(1750,1135),(1750,202),(1704,202)],BLUE,2.4,'8 6',True)
    c.rect(370,1116,1140,38,'#FFFFFF',radius=0)
    c.text(940,1143,'Full-resolution normalized descriptors + validity masks',26,BLUE,600,'middle')
    c.circle(31,1188,5.5,BLUE)
    c.text(45,1196,'anchor',24,MUTED)
    c.line(157,1188,193,1188,TEAL,3.5)
    c.text(203,1196,'track',24,MUTED)
    c.rect(299,1178,33,19,'#D4EAE5',radius=0)
    c.text(342,1196,'tube',24,MUTED)
    c.line(438,1188,473,1188,BLUE,3,arrow=True)
    c.text(486,1196,'local path',24,MUTED)
    c.text(1740,1196,'Core + two budgeted visual decisions · feature-index coordinates',24,INK,anchor='end')
    c.save()


if __name__ == '__main__':
    build_framework()
