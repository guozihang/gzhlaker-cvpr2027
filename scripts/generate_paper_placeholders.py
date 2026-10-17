#!/usr/bin/env python3
"""Generate editable, explicitly illustrative paper figures; never fabricate results.
Requires Python 3 and rsvg-convert for PDF/PNG export. Run from any directory.
"""
from pathlib import Path
from html import escape
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
C = dict(ink='#172B44', muted='#536579', line='#CBD5E1', blue='#2864B4', teal='#16857C',
         orange='#CB7928', bg='#F4F7FB', pale='#E5F2EF', white='#FFFFFF')

class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
                      f'<title>{escape(title)}</title>',
                      '<desc>Draft conceptual figure. No experimental measurements or model outputs.</desc>',
                      '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#536579"/></marker></defs>']
        self.rect(0, 0, w, h, C['white'], rx=0)
    def rect(self,x,y,w,h,fill,stroke='none',rx=10):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')
    def text(self,x,y,s,size=22,color=None,weight=400,anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color or C["ink"]}" text-anchor="{anchor}">{escape(s)}</text>')
    def line(self,x1,y1,x2,y2,color=None,width=2,dash=None,arrow=False):
        extra = (f' stroke-dasharray="{dash}"' if dash else '') + (' marker-end="url(#arrow)"' if arrow else '')
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or C["line"]}" stroke-width="{width}"{extra}/>')
    def circle(self,x,y,r,fill,stroke='none'):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
    def polygon(self,points,fill,opacity=1):
        self.parts.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in points)}" fill="{fill}" opacity="{opacity}"/>')
    def banner(self,title,label='DRAFT SCHEMATIC  /  PROPOSED DESIGN'):
        self.text(28,30,label,16,C['muted'],600)
        self.text(28,72,title,29,weight=700)
    def save(self,name):
        OUT.mkdir(exist_ok=True)
        svg=OUT/(name+'.svg')
        svg.write_text('\n'.join(self.parts+['</svg>'])+'\n',encoding='utf-8')
        for fmt in ('pdf','png'):
            subprocess.run(['rsvg-convert','--format',fmt,'--output',str(OUT/(name+'.'+fmt)),str(svg)],check=True)
        print(name, 'SVG / PDF / PNG')

def axes(s,x,y,w,h):
    s.line(x,y+h,x+w,y+h,C['muted'],2,arrow=True)
    s.line(x,y+h,x,y,C['muted'],2,arrow=True)
    s.text(x+w/2,y+h+30,'Query feature index',17,C['muted'],anchor='middle')
    s.text(x,y-12,'Reference feature index',17,C['muted'])

def point(x,y,w,h,a,b): return x+a*w,y+(1-b)*h

def tube(s,x,y,w,h,lo,hi,offset=0.05,half=0.055):
    points=[point(x,y,w,h,lo,lo+offset-half),point(x,y,w,h,hi,hi+offset-half),
            point(x,y,w,h,hi,hi+offset+half),point(x,y,w,h,lo,lo+offset+half)]
    s.polygon(points,C['teal'],.18)
    a,b=point(x,y,w,h,lo,lo+offset),point(x,y,w,h,hi,hi+offset)
    s.line(*a,*b,C['teal'],3)

# Figure 1: visual contrast is conceptual, not a claim about a specific baseline.
s=SVG(1320,540,'Selective refinement: conceptual teaser')
s.banner('Selective refinement of temporal copy correspondences')
for x in (28,690): s.rect(x,96,602,365,C['bg'])
s.text(48,128,'(a) Dense comparison schematic',24,weight=700)
s.text(710,128,'(b) Sparse proposals + local refinement',24,weight=700)
for x in (82,744): axes(s,x,174,470,210)
for i in range(17):
    for j in range(10):
        a,b=(i+1)/19,(j+1)/12
        px,py=point(82,174,470,210,a,b)
        supported = (.12 <= a <= .39) or (.62 <= a <= .85)
        s.rect(px-6,py-6,12,12,C['blue'] if supported and abs(b-a-.05)<.07 else '#DCE3EC',rx=1)
for lo,hi in ((.12,.39),(.62,.85)): tube(s,744,174,470,210,lo,hi)
for a in (.13,.20,.28,.37,.64,.72,.82):
    px,py=point(744,174,470,210,a,a+.05)
    s.circle(px,py,6,C['blue'])
for a,b in ((.12,.76),(.44,.23),(.60,.80),(.87,.31)):
    s.circle(*point(744,174,470,210,a,b),4,C['orange'])
s.text(48,443,'Broad matching domain',20,C['muted'])
s.text(710,443,'Proposal coverage determines what can be refined',20,C['muted'])
s.text(28,495,'Question: can selective refinement retain localization quality at lower measured cost?',23,weight=600)
s.text(28,524,'Illustrative geometry only. No measured speedup, accuracy, or real video pair is shown.',17,C['muted'])
s.save('fig_1_teaser')

# Figure 2: open research choices are deliberately visible.
s=SVG(1440,555,'Proposed FastVCL framework')
s.banner('FastVCL: proposed sparse-to-tube workflow')
labels=[('Fixed frame features',['Query / reference','ISC descriptors','M x d and N x d']),
        ('Sparse correspondences',['Sample feature indices','Tiled mutual Top-K','Retain index mapping']),
        ('Temporal proposals',['Robust track fitting','Check support on both axes','Split unsupported gaps']),
        ('Local refinement',['Bounded tube regions','Monotone path alignment','Recover interval boundaries']),
        ('Copy intervals',['Validate and deduplicate','Zero or more segment pairs','Attach ranking scores'])]
for i,(title,lines) in enumerate(labels):
    x=28+i*283
    s.rect(x,147,252,206,C['bg'],C['line'])
    s.circle(x+25,176,14,C['teal'])
    s.text(x+25,182,str(i+1),17,C['white'],600,'middle')
    s.text(x+16,218,title,20,weight=700)
    for j,line in enumerate(lines): s.text(x+16,256+j*29,line,18,C['muted'])
    if i<4: s.line(x+257,247,x+276,247,C['muted'],2,arrow=True)
for x,title,desc in [(28,'Scope','Given video pairs; fixed pretrained descriptors'),(510,'Training claim','No additional downstream model training'),(1015,'Open design choices','Sampling, alignment, and scoring')]:
    s.text(x,408,title,21,weight=700)
    if x==1015:
        s.text(x,439,desc,18,C['muted']); s.text(x,466,'require specification and validation.',18,C['muted'])
    else: s.text(x,439,desc,18,C['muted'])
s.line(28,490,1412,490)
s.text(28,525,'Conceptual architecture. The prototype is incomplete; arrows do not certify implementation or effectiveness.',20,C['muted'])
s.save('fig_2_framework')

# Figure 3: coordinates are authored illustrations, not synthetic benchmark outputs.
s=SVG(1320,570,'Illustration of anchors, separated tracks, and tubes')
s.banner('From anchor support to bounded refinement')
for k,title in enumerate(['(a) Sparse anchors','(b) Separate supported intervals','(c) Refine inside finite tubes']):
    px=28+k*434
    s.rect(px,100,406,352,C['bg'])
    s.text(px+16,135,title,21,weight=700)
    x,y,w,h=px+42,185,315,196
    axes(s,x,y,w,h)
    if k==2:
        for lo,hi in ((.10,.40),(.61,.88)): tube(s,x,y,w,h,lo,hi)
    if k==1:
        for lo,hi in ((.13,.37),(.65,.84)):
            s.line(*point(x,y,w,h,lo,lo+.05),*point(x,y,w,h,hi,hi+.05),C['teal'],4)
        a,b=point(x,y,w,h,.41,.46),point(x,y,w,h,.59,.64)
        s.line(*a,*b,C['orange'],2,'5 5')
        s.text(px+160,322,'gap',18,C['orange'])
    for a in (.13,.21,.29,.37,.65,.74,.84): s.circle(*point(x,y,w,h,a,a+.05),5,C['blue'])
    if k==0:
        for a,b in ((.16,.78),(.47,.18),(.82,.33)): s.circle(*point(x,y,w,h,a,b),4,C['orange'])
s.circle(44,485,5,C['blue']); s.text(58,491,'illustrative anchor',19,C['muted'])
s.line(300,484,328,484,C['teal'],4); s.text(342,491,'candidate track',19,C['muted'])
s.rect(565,475,30,18,C['pale'],rx=0); s.text(608,491,'tube search region',19,C['muted'])
s.text(28,542,'Schematic only: no ground truth, inferred path, benchmark sample, or measured boundary accuracy is shown.',19,C['muted'])
s.save('fig_3_sparse_tracks')

# Figure 4: empty plotting frame; there are intentionally no data points or numeric ticks.
s=SVG(1120,600,'Results-pending placeholder for accuracy versus latency')
s.banner('Accuracy versus localization cost','DRAFT PLACEHOLDER  /  RESULTS PENDING')
x,y,w,h=142,128,920,355
s.line(x,y+h,x+w,y+h,C['muted'],2,arrow=True)
s.line(x,y+h,x,y,C['muted'],2,arrow=True)
s.text(x,y-16,'VCSL F1 (%)',22,weight=600)
s.text(x+w/2,y+h+39,'Localization latency (ms / pair)',23,anchor='middle')
s.rect(350,226,500,143,C['bg'],C['line'])
s.text(600,269,'RESULTS PENDING',28,C['muted'],700,'middle')
s.text(600,307,'No data points or curves are plotted.',21,C['muted'],anchor='middle')
s.text(600,337,'Axes and operating points will follow the frozen protocol.',17,C['muted'],anchor='middle')
s.text(28,565,'Replace using verified results on identical pairs, features, evaluator, and timing boundaries.',19,C['muted'])
s.save('fig_4_tradeoff')
