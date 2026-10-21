#!/usr/bin/env python3
"""Zeichnet die Röntgenbilder in bilder/ (12 Tiere × 4 Diagnosen) als SVG.

Aufruf:  python3 tools/roentgenbilder.py

Every image is a stylised X-ray of a plush toy: soft, glowing "stuffing" with a
cartoon skeleton, button eyes and joint discs inside. No dependencies.
"""
import math
import os
import random

W, H = 900, 1200
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bilder')

TISSUE = '#8fb0c8'
BONE = '#e3f3ff'
DENSE = '#f6fcff'

LABEL_TOP = 'TEDDY-DOCS FAU · BAYREUTH'

# ── SVG helpers ──────────────────────────────────────────────


def n(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def attrs(**kw):
    return ''.join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in kw.items() if v is not None)


def ellipse(cx, cy, rx, ry, rot=0, **kw):
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ''
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}"{t}{attrs(**kw)}/>'


def circle(cx, cy, r, **kw):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"{attrs(**kw)}/>'


def rect(x, y, w, h, r=0, **kw):
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(r)}"{attrs(**kw)}/>'


def path(d, **kw):
    return f'<path d="{d}"{attrs(**kw)}/>'


def poly(points, **kw):
    d = 'M ' + ' L '.join(f'{n(x)} {n(y)}' for x, y in points) + ' Z'
    return path(d, **kw)


def stroke(x1, y1, x2, y2, w, **kw):
    return f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke-width="{n(w)}" stroke-linecap="round"{attrs(**kw)}/>'


def group(items, transform):
    return f'<g transform="{transform}">' + ''.join(items) + '</g>'


def heart_path(cx, cy, s):
    p = lambda x, y: f'{n(cx + x * s)} {n(cy + y * s)}'
    return (f'M {p(0, 0.9)} C {p(-0.2, 0.7)} {p(-1, 0.25)} {p(-1, -0.25)} '
            f'C {p(-1, -0.75)} {p(-0.45, -0.95)} {p(0, -0.5)} '
            f'C {p(0.45, -0.95)} {p(1, -0.75)} {p(1, -0.25)} '
            f'C {p(1, 0.25)} {p(0.2, 0.7)} {p(0, 0.9)} Z')


# ── Image builder ────────────────────────────────────────────


class Xray:
    def __init__(self, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        self.tissue = []         # filled soft tissue (also clips the stuffing texture)
        self.tissue_line = []    # stroked soft tissue (tails, trunks)
        self.seams = []
        self.skeleton = []
        self.dark = []           # eye sockets, nostrils
        self.organ = []          # the heart
        self.dense = []          # metal / plastic: buttons, swallowed objects, claws
        self.holes = []          # black cut-outs on top of dense parts
        self.marks = []          # radiologist's annotations
        self.defs = []
        self.transform = ''

    # bones -----------------------------------------------------

    def bone(self, x1, y1, x2, y2, w):
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        out = [stroke(x1, y1, x2, y2, w)]
        for (x, y, sgn) in ((x1, y1, -1), (x2, y2, 1)):
            for side in (-1, 1):
                out.append(circle(x + px * w * 0.42 * side + ux * w * 0.05 * sgn,
                                  y + py * w * 0.42 * side + uy * w * 0.05 * sgn, w * 0.5, stroke='none'))
        self.skeleton += out

    def vertebra(self, cx, cy, w, h):
        self.skeleton.append(rect(cx - w / 2, cy - h / 2, w, h, min(w, h) * 0.3, stroke='none'))

    def ring(self, cx, cy, rx, ry, width, rot=0, fill_opacity=0.15):
        self.skeleton.append(ellipse(cx, cy, rx, ry, rot, stroke_width=n(width), fill_opacity=fill_opacity))

    def spine(self, x, y1, y2, w):
        count = max(3, int((y2 - y1) / (w * 1.15)))
        step = (y2 - y1) / count
        for i in range(count + 1):
            self.vertebra(x, y1 + i * step, w, step * 0.72)

    def tail_bones(self, pts, r):
        for i, (x, y) in enumerate(pts):
            self.skeleton.append(circle(x, y, r * (1 - 0.5 * i / len(pts)), stroke='none'))

    def limb(self, cx, cy, ry, rot, w, end='paw'):
        a = math.radians(rot)
        dx, dy = -math.sin(a), math.cos(a)
        top = (cx - dx * ry * 0.72, cy - dy * ry * 0.72)
        mid = (cx + dx * ry * 0.02, cy + dy * ry * 0.02)
        bot = (cx + dx * ry * 0.6, cy + dy * ry * 0.6)
        self.bone(*top, *mid, w)
        px, py = -dy, dx
        for side in (-1, 1):
            self.bone(mid[0] + dx * 10 + px * w * 0.3 * side, mid[1] + dy * 10 + py * w * 0.3 * side,
                      bot[0] + px * w * 0.25 * side, bot[1] + py * w * 0.25 * side, w * 0.5)
        if end in ('paw', 'hand'):
            fingers = 5 if end == 'hand' else 4
            spread = 70 if end == 'hand' else 56
            for i in range(fingers):
                ang = math.radians(-spread / 2 + spread * i / (fingers - 1))
                fx = dx * math.cos(ang) - dy * math.sin(ang)
                fy = dx * math.sin(ang) + dy * math.cos(ang)
                sx, sy = bot[0] + dx * 14, bot[1] + dy * 14
                ln = ry * (0.2 if end == 'paw' else 0.27)
                self.bone(sx, sy, sx + fx * ln, sy + fy * ln, w * 0.28)
        elif end == 'hoof':
            sx, sy = bot[0] + dx * 12, bot[1] + dy * 12
            self.bone(sx, sy, sx + dx * ry * 0.22, sy + dy * ry * 0.22, w * 0.45)
        elif end == 'flipper':
            for i in range(3):
                ang = math.radians(-14 + 14 * i)
                fx = dx * math.cos(ang) - dy * math.sin(ang)
                fy = dx * math.sin(ang) + dy * math.cos(ang)
                sx, sy = bot[0] + dx * 10, bot[1] + dy * 10
                self.bone(sx, sy, sx + fx * ry * 0.3, sy + fy * ry * 0.3, w * 0.32)

    # plush details -------------------------------------------

    def buttons(self, x1, x2, y, r=21):
        for x in (x1, x2):
            self.dense.append(circle(x, y, r))
            for ox, oy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                self.holes.append(circle(x + ox * r * 0.3, y + oy * r * 0.3, r * 0.17))

    def joint_disc(self, x, y, r=30):
        self.skeleton.append(circle(x, y, r, stroke_width='6', fill_opacity='0.12'))
        self.dense.append(circle(x, y, 6))

    def seam(self, d):
        self.seams.append(path(d))

    def tag(self, x, y, rot=12):
        self.seams.append(group([rect(x, y, 46, 70, 4, fill=TISSUE, fill_opacity='0.35'),
                                 stroke(x + 10, y + 20, x + 36, y + 20, 3),
                                 stroke(x + 10, y + 34, x + 36, y + 34, 3),
                                 stroke(x + 10, y + 48, x + 28, y + 48, 3)],
                                f'rotate({rot} {n(x + 23)} {n(y + 35)})'))

    # output ----------------------------------------------------

    def svg(self, labels):
        clip = ''.join(self.tissue)
        grain_seed = self.seed % 1000
        top, sub, kind = labels
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="edge" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5"/></filter>
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="shine" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="12" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="fluff" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="4" seed="{grain_seed}"/><feColorMatrix type="matrix" values="0 0 0 0 0.75  0 0 0 0 0.86  0 0 0 0 0.95  0.55 0 0 0 -0.17"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{grain_seed + 7}"/><feColorMatrix type="matrix" values="0 0 0 0 0.8  0 0 0 0 0.9  0 0 0 0 1  0.3 0 0 0 -0.08"/></filter>
<radialGradient id="vignette" cx="50%" cy="50%" r="70%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.75"/></radialGradient>
<clipPath id="body">{clip}</clipPath>
{''.join(self.defs)}
</defs>
<rect width="{W}" height="{H}" fill="#000"/>
<g transform="{self.transform}">
<g fill="{TISSUE}" fill-opacity="0.24" filter="url(#soft)">{''.join(self.tissue)}{''.join(self.tissue_line)}</g>
<g fill="none" stroke="#b4dcf4" stroke-opacity="0.22" stroke-width="5" filter="url(#edge)">{''.join(self.tissue)}</g>
<rect width="{W}" height="{H}" filter="url(#fluff)" clip-path="url(#body)"/>
<g fill="none" stroke="#cfe9fa" stroke-opacity="0.32" stroke-width="3" stroke-dasharray="10 8">{''.join(self.seams)}</g>
<g fill="{BONE}" stroke="{BONE}" opacity="0.56" filter="url(#glow)">{''.join(self.skeleton)}</g>
<g fill="#000" opacity="0.55">{''.join(self.dark)}</g>
<g fill="#eef8ff" opacity="0.8" filter="url(#shine)">{''.join(self.organ)}</g>
<g fill="{DENSE}" opacity="0.95" filter="url(#glow)">{''.join(self.dense)}</g>
<g fill="#000" opacity="0.85">{''.join(self.holes)}</g>
<g fill="none" stroke="#ffffff" stroke-opacity="0.7" stroke-width="4" stroke-dasharray="14 10">{''.join(self.marks)}</g>
</g>
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<rect width="{W}" height="{H}" fill="url(#vignette)"/>
<g fill="#a6dcf2" fill-opacity="0.78" font-family="Menlo, Consolas, monospace" font-size="26" letter-spacing="2">
<text x="40" y="62">{LABEL_TOP}</text>
<text x="40" y="98">{top}</text>
<text x="40" y="1160" font-size="22" fill-opacity="0.6">{kind}</text>
<text x="{W - 40}" y="1160" font-size="22" fill-opacity="0.6" text-anchor="end">{sub}</text>
<text x="{W - 50}" y="90" font-size="60" font-weight="bold" text-anchor="end">R</text>
</g>
</svg>
'''


# ── Bodies ───────────────────────────────────────────────────
# Every animal is a plush toy sitting upright, seen from the front.


class Body:
    """Where things are, so diagnoses know where to put hearts and objects."""

    def __init__(self, head, body):
        self.head = head  # (cx, cy, rx, ry)
        self.body = body

    @property
    def heart(self):
        bx, by, brx, bry = self.body
        return bx + brx * 0.13, by - bry * 0.36

    @property
    def belly(self):
        bx, by, brx, bry = self.body
        return bx, by + bry * 0.2


def base(x, head, body, arms, legs, *, hand='paw', foot='paw', eyes=(55, -12), ribs=5,
         joints=True, buttons=True, skull=1.0, bone_w=1.0):
    hx, hy, hrx, hry = head
    bx, by, brx, bry = body
    x.tissue += [ellipse(bx, by, brx, bry), ellipse(hx, hy, hrx, hry)]
    for arm in arms:
        x.tissue.append(ellipse(*arm))
    for leg in legs:
        x.tissue.append(ellipse(*leg))

    # skeleton
    x.ring(hx, hy - hry * 0.05, hrx * 0.72 * skull, hry * 0.7 * skull, 13)
    x.skeleton.append(path(f'M {n(hx - hrx * 0.42)} {n(hy + hry * 0.42)} Q {n(hx)} {n(hy + hry * 0.85)} {n(hx + hrx * 0.42)} {n(hy + hry * 0.42)}',
                           fill='none', stroke_width='11'))
    ex, ey = eyes
    for sx in (-1, 1):
        x.dark.append(ellipse(hx + sx * ex, hy + ey, 34, 38))
    neck_top = hy + hry * 0.62
    spine_top = by - bry * 0.84
    x.spine(bx, neck_top, spine_top, 24 * bone_w)
    x.spine(bx, spine_top, by + bry * 0.58, 34 * bone_w)
    for sx in (-1, 1):
        x.bone(bx + sx * 18, spine_top + 10, bx + sx * brx * 0.55, spine_top + bry * 0.07, 14 * bone_w)
    for i in range(ribs):
        y = by - bry * 0.66 + i * bry * 0.13
        span = brx * 0.6 * (1 - 0.06 * i)
        for sx in (-1, 1):
            x.skeleton.append(path(f'M {n(bx + sx * 18)} {n(y)} Q {n(bx + sx * span * 1.08)} {n(y - 20)} {n(bx + sx * span)} {n(y + bry * 0.17)}',
                                   fill='none', stroke_width=n(12 * bone_w * (1 - 0.08 * i)), stroke_linecap='round'))
    for sx in (-1, 1):
        x.ring(bx + sx * brx * 0.22, by + bry * 0.64, brx * 0.24, bry * 0.12, 11, sx * 20)
    for (cx, cy, rx, ry, rot) in arms:
        x.limb(cx, cy, ry, rot, 24 * bone_w, hand)
    for (cx, cy, rx, ry, rot) in legs:
        x.limb(cx, cy, ry, rot, 28 * bone_w, foot)

    # plush details
    if buttons:
        x.buttons(hx - ex, hx + ex, hy + ey)
    if joints:
        for (cx, cy, rx, ry, rot) in arms + legs:
            a = math.radians(rot)
            x.joint_disc(cx + math.sin(a) * ry * 0.55, cy - math.cos(a) * ry * 0.55, 26)
    x.seam(f'M {n(bx)} {n(by - bry * 0.75)} L {n(bx)} {n(by + bry * 0.85)}')
    x.tag(bx + brx * 0.72, by + bry * 0.42)
    return Body(head, body)


def std_limbs(body, arm_len=150, arm_w=62, leg=(95, 112)):
    bx, by, brx, bry = body
    arms = [(bx - brx * 0.9, by - bry * 0.4 + arm_len * 0.62, arm_w, arm_len, 25),
            (bx + brx * 0.9, by - bry * 0.4 + arm_len * 0.62, arm_w, arm_len, -25)]
    legs = [(bx - brx * 0.55, by + bry * 0.98, leg[0], leg[1], 14),
            (bx + brx * 0.55, by + bry * 0.98, leg[0], leg[1], -14)]
    return arms, legs


def snout(x, hx, y, rx, ry, nose=26):
    x.tissue.append(ellipse(hx, y, rx, ry))
    x.dense.append(path(f'M {n(hx - nose)} {n(y - ry * 0.45)} Q {n(hx)} {n(y - ry * 0.65)} {n(hx + nose)} {n(y - ry * 0.45)} L {n(hx)} {n(y - ry * 0.45 + nose * 0.9)} Z',
                        opacity='0.55'))


def tail(x, pts, w):
    d = f'M {n(pts[0][0])} {n(pts[0][1])} ' + ' '.join(
        f'Q {n(pts[i][0])} {n(pts[i][1])} {n(pts[i + 1][0])} {n(pts[i + 1][1])}' for i in range(1, len(pts) - 1, 2))
    x.tissue_line.append(path(d, fill='none', stroke=TISSUE, stroke_opacity='0.24', stroke_width=n(w), stroke_linecap='round'))
    samples = []
    for i in range(0, len(pts) - 2, 2):
        (x0, y0), (x1, y1), (x2, y2) = pts[i], pts[i + 1], pts[i + 2]
        for k in range(5):
            t = k / 5
            samples.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2,
                            (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2))
    x.tail_bones(samples[1:], w * 0.22)


def baer(x):
    head, body = (450, 360, 172, 155), (450, 770, 218, 268)
    hx, hy = head[:2]
    for sx in (-1, 1):
        x.tissue.append(circle(hx + sx * 122, hy - 118, 58))
        x.tissue.append(circle(hx + sx * 122, hy - 118, 30))
    arms, legs = std_limbs(body)
    b = base(x, head, body, arms, legs)
    snout(x, hx, hy + 62, 72, 54)
    return b


def hase(x):
    head, body = (450, 400, 160, 145), (450, 790, 210, 255)
    hx, hy = head[:2]
    for sx in (-1, 1):
        x.tissue.append(ellipse(hx + sx * 62, hy - 225, 46, 130, sx * 9))
        x.dense.append(path(f'M {n(hx + sx * 50)} {n(hy - 120)} Q {n(hx + sx * 66)} {n(hy - 250)} {n(hx + sx * 82)} {n(hy - 330)}',
                            fill='none', stroke=DENSE, stroke_width='3', opacity='0.6'))
    arms, legs = std_limbs(body, arm_len=135, arm_w=55, leg=(100, 115))
    b = base(x, head, body, arms, legs, eyes=(52, -10))
    snout(x, hx, hy + 55, 60, 44, nose=20)
    x.dense += [rect(hx - 22, hy + 82, 20, 30, 4, opacity='0.7'), rect(hx + 2, hy + 82, 20, 30, 4, opacity='0.7')]
    return b


def hund(x):
    head, body = (450, 360, 165, 150), (450, 775, 215, 265)
    hx, hy = head[:2]
    for sx in (-1, 1):
        x.tissue.append(ellipse(hx + sx * 158, hy + 40, 52, 118, -sx * 14))
    arms, legs = std_limbs(body)
    b = base(x, head, body, arms, legs)
    snout(x, hx, hy + 70, 88, 62, nose=34)
    x.skeleton.append(ellipse(hx, hy + 70, 55, 38, stroke_width='9', fill_opacity='0.12'))
    tail(x, [(600, 1000), (700, 990), (720, 900)], 46)
    return b


def katze(x):
    head, body = (450, 370, 165, 145), (450, 780, 205, 260)
    hx, hy = head[:2]
    for sx in (-1, 1):
        x.tissue.append(poly([(hx + sx * 150, hy - 50), (hx + sx * 128, hy - 205), (hx + sx * 45, hy - 132)]))
        for k in range(3):
            x.dense.append(stroke(hx + sx * 50, hy + 58 + k * 12, hx + sx * 190, hy + 30 + k * 30, 2.5, stroke=DENSE, opacity='0.7'))
    arms, legs = std_limbs(body, arm_len=140, arm_w=55)
    b = base(x, head, body, arms, legs, eyes=(56, -8))
    snout(x, hx, hy + 55, 58, 40, nose=18)
    tail(x, [(590, 1010), (760, 1000), (770, 860), (775, 720), (700, 660)], 44)
    return b


def loewe(x):
    head, body = (450, 370, 165, 150), (450, 785, 220, 262)
    hx, hy = head[:2]
    x.tissue.append(circle(hx, hy + 5, 225))
    for i in range(14):
        a = 2 * math.pi * i / 14
        x.tissue.append(circle(hx + math.cos(a) * 218, hy + 5 + math.sin(a) * 210, 52))
    for sx in (-1, 1):
        x.tissue.append(circle(hx + sx * 118, hy - 112, 40))
    arms, legs = std_limbs(body)
    b = base(x, head, body, arms, legs)
    snout(x, hx, hy + 62, 78, 56, nose=28)
    tail(x, [(600, 1010), (760, 1030), (790, 900)], 34)
    x.tissue.append(ellipse(795, 870, 38, 52))
    return b


def affe(x):
    head, body = (450, 360, 158, 148), (450, 775, 205, 262)
    hx, hy = head[:2]
    for sx in (-1, 1):
        x.tissue.append(circle(hx + sx * 168, hy + 5, 56))
    x.tissue.append(ellipse(hx, hy + 30, 118, 100))
    x.tissue.append(ellipse(hx, hy + 75, 78, 50))
    bx, by, brx, bry = body
    arms = [(bx - brx * 0.95, by + 30, 50, 200, 18), (bx + brx * 0.95, by + 30, 50, 200, -18)]
    legs = [(bx - brx * 0.55, by + bry * 0.98, 92, 110, 14), (bx + brx * 0.55, by + bry * 0.98, 92, 110, -14)]
    b = base(x, head, body, arms, legs, hand='hand', foot='hand', eyes=(48, 0))
    tail(x, [(600, 1000), (780, 1040), (800, 880), (810, 740), (720, 720), (680, 760), (700, 800)], 30)
    return b


def pferd(x):
    head, body = (450, 340, 140, 165), (450, 790, 210, 260)
    hx, hy = head[:2]
    x.tissue.append(ellipse(hx, hy + 140, 108, 82))
    for sx in (-1, 1):
        x.tissue.append(poly([(hx + sx * 112, hy - 95), (hx + sx * 102, hy - 215), (hx + sx * 48, hy - 140)]))
    for k in range(6):
        x.tissue.append(ellipse(hx - 40 + k * 16, hy - 150, 16, 50, -20 + k * 8))
    arms, legs = std_limbs(body, arm_len=150, arm_w=56)
    b = base(x, head, body, arms, legs, hand='hoof', foot='hoof', eyes=(62, -40), skull=1.05)
    x.skeleton.append(ellipse(hx, hy + 130, 72, 60, stroke_width='10', fill_opacity='0.12'))
    for sx in (-1, 1):
        x.dark.append(ellipse(hx + sx * 38, hy + 165, 14, 20))
    for (cx, cy, rx, ry, rot) in arms + legs:
        a = math.radians(rot)
        fx, fy = cx - math.sin(a) * ry * 0.95, cy + math.cos(a) * ry * 0.95
        x.dense.append(ellipse(fx, fy, rx * 0.85, 28, rot, opacity='0.45'))
    for k in range(7):
        x.tissue_line.append(path(f'M {n(620 + k * 6)} 1000 Q {n(700 + k * 10)} 1040 {n(720 + k * 14)} 1130',
                                  fill='none', stroke=TISSUE, stroke_opacity='0.24', stroke_width='10', stroke_linecap='round'))
    return b


def elefant(x):
    head, body = (450, 360, 182, 160), (450, 790, 225, 262)
    hx, hy = head[:2]
    for sx in (-1, 1):
        x.tissue.append(ellipse(hx + sx * 200, hy + 15, 120, 150, sx * 8))
    arms, legs = std_limbs(body, arm_len=145, arm_w=72, leg=(105, 112))
    b = base(x, head, body, arms, legs, hand='hoof', foot='hoof', skull=1.1, eyes=(70, -25))
    x.tissue_line.append(path(f'M {n(hx)} {n(hy + 40)} Q {n(hx - 10)} {n(hy + 230)} {n(hx + 60)} {n(hy + 300)} Q {n(hx + 110)} {n(hy + 320)} {n(hx + 95)} {n(hy + 270)}',
                              fill='none', stroke=TISSUE, stroke_opacity='0.24', stroke_width='74', stroke_linecap='round'))
    for k in range(6):
        y = hy + 120 + k * 32
        x.seams.append(path(f'M {n(hx - 34 + k * 3)} {n(y)} Q {n(hx + k * 4)} {n(y + 10)} {n(hx + 34 + k * 6)} {n(y)}'))
    for sx in (-1, 1):
        x.dense.append(path(f'M {n(hx + sx * 50)} {n(hy + 80)} Q {n(hx + sx * 70)} {n(hy + 150)} {n(hx + sx * 110)} {n(hy + 165)}',
                            fill='none', stroke=DENSE, stroke_width='16', stroke_linecap='round', opacity='0.7'))
    for (cx, cy, rx, ry, rot) in arms + legs:
        a = math.radians(rot)
        fx, fy = cx - math.sin(a) * ry * 0.82, cy + math.cos(a) * ry * 0.82
        for k in (-1, 0, 1):
            x.dense.append(ellipse(fx + k * 30, fy + 8, 13, 9, rot, opacity='0.6'))
    return b


def dino(x):
    head, body = (450, 350, 178, 140), (450, 785, 220, 265)
    hx, hy = head[:2]
    x.tissue.append(ellipse(hx, hy + 75, 150, 78))
    for k in range(5):
        cx = hx - 100 + k * 50
        x.tissue.append(poly([(cx - 30, hy - 105 - abs(k - 2) * -6), (cx, hy - 190 + abs(k - 2) * 18), (cx + 30, hy - 105 - abs(k - 2) * -6)]))
    bx, by, brx, bry = body
    arms = [(bx - brx * 0.62, by - 80, 40, 80, 40), (bx + brx * 0.62, by - 80, 40, 80, -40)]
    legs = [(bx - brx * 0.58, by + bry * 0.95, 108, 120, 14), (bx + brx * 0.58, by + bry * 0.95, 108, 120, -14)]
    b = base(x, head, body, arms, legs, eyes=(70, -30), skull=1.08)
    x.dense.append(path(' '.join(f'{"M" if i == 0 else "L"} {n(hx - 120 + i * 20)} {n(hy + 92 + (8 if i % 2 else -6))}' for i in range(13)),
                        fill='none', stroke=DENSE, stroke_width='5', opacity='0.7'))
    for (cx, cy, rx, ry, rot) in legs:
        for k in (-1, 0, 1):
            tx, ty = cx + k * 34, cy + ry * 0.92
            x.dense.append(path(f'M {n(tx - 9)} {n(ty)} Q {n(tx)} {n(ty + 34)} {n(tx + 12)} {n(ty + 30)} Q {n(tx + 6)} {n(ty + 8)} {n(tx + 9)} {n(ty)} Z', opacity='0.75'))
    x.tissue_line.append(path('M 600 1000 Q 790 1010 820 860 Q 840 760 800 700', fill='none', stroke=TISSUE, stroke_opacity='0.24', stroke_width='90', stroke_linecap='round'))
    x.tail_bones([(640, 1005), (690, 1000), (735, 985), (772, 958), (798, 922), (815, 880), (822, 838), (822, 796), (815, 755)], 22)
    return b


def pinguin(x):
    head, body = (450, 330, 155, 145), (450, 760, 240, 300)
    hx, hy = head[:2]
    x.tissue.append(ellipse(450, 560, 190, 150))
    bx, by, brx, bry = body
    arms = [(bx - brx * 0.98, by - 10, 46, 175, 18), (bx + brx * 0.98, by - 10, 46, 175, -18)]
    b = base(x, head, body, arms, [], hand='flipper', eyes=(55, -15))
    for sx in (-1, 1):
        fx = bx + sx * 90
        x.tissue.append(path(f'M {n(fx - 70)} 1080 L {n(fx + 70)} 1080 L {n(fx + 40)} 1020 L {n(fx - 40)} 1020 Z'))
        for k in (-1, 0, 1):
            x.bone(fx, 1020, fx + k * 45, 1075, 9)
    x.dense.append(poly([(hx - 40, hy + 30), (hx + 40, hy + 30), (hx, hy + 110)], opacity='0.6'))
    x.skeleton.append(poly([(hx - 30, hy + 30), (hx + 30, hy + 30), (hx, hy + 95)], fill_opacity='0.2', stroke_width='6'))
    return b


def ente(x):
    head, body = (450, 330, 145, 135), (450, 770, 228, 275)
    hx, hy = head[:2]
    x.tissue.append(ellipse(450, 520, 95, 90))
    bx, by, brx, bry = body
    arms = [(bx - brx * 0.92, by - 20, 58, 150, 14), (bx + brx * 0.92, by - 20, 58, 150, -14)]
    b = base(x, head, body, arms, [], hand='flipper', eyes=(52, -22))
    x.dense.append(ellipse(hx, hy + 70, 105, 44, opacity='0.55'))
    x.holes.append(ellipse(hx - 22, hy + 60, 7, 4))
    x.holes.append(ellipse(hx + 22, hy + 60, 7, 4))
    x.skeleton.append(path(f'M {n(bx - 70)} {n(by - bry * 0.78)} Q {n(bx)} {n(by - bry * 0.45)} {n(bx + 70)} {n(by - bry * 0.78)}',
                           fill='none', stroke_width='10'))
    for sx in (-1, 1):
        fx = bx + sx * 95
        x.tissue.append(path(f'M {n(fx)} 1000 L {n(fx - 85)} 1095 Q {n(fx)} 1075 {n(fx + 85)} 1095 Z'))
        x.bone(fx, 960, fx, 1005, 16)
        for k in (-1, 0, 1):
            x.bone(fx, 1005, fx + k * 72, 1088 - abs(k) * 6, 8)
    return b


def puppe(x):
    head, body = (450, 330, 140, 150), (450, 760, 170, 250)
    hx, hy = head[:2]
    x.tissue.append(ellipse(hx, hy - 50, 170, 130))
    for sx in (-1, 1):
        x.tissue.append(ellipse(hx + sx * 180, hy + 120, 44, 120, sx * 8))
        x.dense.append(rect(hx + sx * 180 - 22, hy + 10, 44, 18, 6, opacity='0.5'))
    for k in range(18):
        sx = -1 if k < 9 else 1
        off = (k % 9) * 14
        x.seams.append(path(f'M {n(hx + sx * (30 + off))} {n(hy - 150 + off * 0.4)} Q {n(hx + sx * (80 + off))} {n(hy - 60)} {n(hx + sx * (120 + off * 0.6))} {n(hy + 40 + off)}'))
    x.tissue.append(path('M 370 540 L 530 540 L 690 1010 Q 450 1050 210 1010 Z'))
    bx, by, brx, bry = body
    arms = [(bx - 175, by - 40, 42, 150, 20), (bx + 175, by - 40, 42, 150, -20)]
    legs = [(400, 1080, 44, 100, 0), (500, 1080, 44, 100, 0)]
    b = base(x, head, body, arms, legs, hand='hand', foot='hoof', eyes=(50, -5), joints=False, buttons=False, bone_w=0.85)
    for sx in (-1, 1):
        ex = hx + sx * 50
        x.dense.append(circle(ex, hy - 5, 24, opacity='0.55'))
        x.holes.append(circle(ex, hy - 5, 10))
        x.dense.append(ellipse(450 + sx * 50, 1170, 50, 28, opacity='0.5'))
    x.seams.append(path(f'M {n(hx - 40)} {n(hy + 80)} Q {n(hx)} {n(hy + 110)} {n(hx + 40)} {n(hy + 80)}'))
    x.dense.append(rect(bx - 40, by - 120, 80, 60, 10, opacity='0.5'))
    x.holes += [circle(bx - 20 + k * 20, by - 90, 5) for k in range(3)]
    return b


# ── Swallowed objects ────────────────────────────────────────


def obj_karotte(x, ox, oy):
    items = [path(f'M {n(ox - 30)} {n(oy - 85)} Q {n(ox)} {n(oy - 100)} {n(ox + 30)} {n(oy - 85)} L {n(ox + 6)} {n(oy + 95)} Q {n(ox)} {n(oy + 104)} {n(ox - 6)} {n(oy + 95)} Z')]
    items += [ellipse(ox + k * 14, oy - 120, 9, 34, k * 18) for k in (-1, 0, 1)]
    x.dense.append(group(items, f'rotate(25 {n(ox)} {n(oy)})'))
    x.holes.append(group([stroke(ox - 22, oy - 50 + k * 34, ox - 6, oy - 46 + k * 34, 3, stroke='#000') for k in range(4)],
                         f'rotate(25 {n(ox)} {n(oy)})'))


def obj_schluessel(x, ox, oy):
    t = f'rotate(-28 {n(ox)} {n(oy)})'
    x.dense.append(group([circle(ox - 70, oy, 40), rect(ox - 36, oy - 10, 140, 20, 4),
                          rect(ox + 64, oy + 8, 14, 26, 2), rect(ox + 86, oy + 8, 14, 18, 2)], t))
    x.holes.append(group([circle(ox - 70, oy, 16)], t))


def obj_gloeckchen(x, ox, oy):
    x.dense.append(circle(ox, oy, 56, opacity='0.55'))
    x.dense.append(circle(ox, oy - 64, 14, fill='none', stroke=DENSE, stroke_width='8'))
    x.dense.append(circle(ox + 8, oy + 18, 20))
    x.holes.append(rect(ox - 40, oy + 22, 80, 8, 4))
    x.holes.append(circle(ox - 40, oy + 26, 9))
    x.holes.append(circle(ox + 40, oy + 26, 9))


def obj_lego(x, ox, oy):
    x.dense.append(rect(ox - 80, oy - 34, 160, 86, 8))
    x.dense += [rect(ox - 66 + i * 36, oy - 58, 24, 26, 4) for i in range(4)]


def obj_hufeisen(x, ox, oy):
    x.dense.append(path(f'M {n(ox - 60)} {n(oy - 60)} L {n(ox - 60)} {n(oy + 10)} A 60 60 0 0 0 {n(ox + 60)} {n(oy + 10)} L {n(ox + 60)} {n(oy - 60)}',
                        fill='none', stroke=DENSE, stroke_width='34', stroke_linecap='round'))
    for (hx, hy) in ((-60, -40), (-60, 0), (-38, 52), (60, -40), (60, 0), (38, 52)):
        x.holes.append(rect(ox + hx - 4, oy + hy - 7, 8, 14, 2))


def obj_fisch(x, ox, oy):
    x.dense.append(stroke(ox - 100, oy, ox + 70, oy, 7, stroke=DENSE))
    for k in range(7):
        rx = ox - 70 + k * 22
        h = 48 - abs(k - 3) * 6
        x.dense.append(path(f'M {n(rx)} {n(oy - h)} Q {n(rx + 10)} {n(oy)} {n(rx)} {n(oy + h)}', fill='none', stroke=DENSE, stroke_width='4'))
    x.dense.append(path(f'M {n(ox + 70)} {n(oy)} Q {n(ox + 90)} {n(oy - 50)} {n(ox + 140)} {n(oy - 10)} Q {n(ox + 150)} {n(oy)} {n(ox + 140)} {n(oy + 10)} Q {n(ox + 90)} {n(oy + 50)} {n(ox + 70)} {n(oy)} Z',
                        fill='none', stroke=DENSE, stroke_width='6'))
    x.dense.append(circle(ox + 112, oy - 8, 7))
    x.dense.append(path(f'M {n(ox - 100)} {n(oy)} L {n(ox - 150)} {n(oy - 40)} M {n(ox - 100)} {n(oy)} L {n(ox - 150)} {n(oy + 40)} M {n(ox - 100)} {n(oy)} L {n(ox - 155)} {n(oy)}',
                        fill='none', stroke=DENSE, stroke_width='5'))


def obj_erdnuss(x, ox, oy):
    t = f'rotate(-30 {n(ox)} {n(oy)})'
    x.dense.append(group([ellipse(ox - 40, oy, 50, 42), ellipse(ox + 40, oy, 46, 38)], t))
    x.holes.append(group([circle(ox - 60 + k * 22, oy + (k % 2) * 14 - 7, 3) for k in range(6)], t))


def obj_schnuller(x, ox, oy):
    x.dense.append(ellipse(ox, oy, 80, 40, opacity='0.7'))
    x.dense.append(ellipse(ox, oy - 62, 30, 40, opacity='0.5'))
    x.dense.append(circle(ox, oy + 58, 34, fill='none', stroke=DENSE, stroke_width='10'))
    x.holes.append(circle(ox - 48, oy, 9))
    x.holes.append(circle(ox + 48, oy, 9))


def obj_auto(x, ox, oy):
    x.dense.append(path(f'M {n(ox - 100)} {n(oy + 20)} L {n(ox - 100)} {n(oy - 15)} L {n(ox - 50)} {n(oy - 22)} L {n(ox - 25)} {n(oy - 60)} L {n(ox + 45)} {n(oy - 60)} L {n(ox + 70)} {n(oy - 22)} L {n(ox + 100)} {n(oy - 15)} L {n(ox + 100)} {n(oy + 20)} Z',
                        opacity='0.8'))
    for wx in (-55, 55):
        x.dense.append(circle(ox + wx, oy + 26, 26))
        x.holes.append(circle(ox + wx, oy + 26, 9))
    x.holes.append(rect(ox - 20, oy - 52, 26, 26, 3))
    x.holes.append(rect(ox + 14, oy - 52, 26, 26, 3))


def obj_gummiente(x, ox, oy):
    shape = [ellipse(ox, oy + 20, 80, 50), circle(ox + 40, oy - 45, 36)]
    x.dense.append(f'<g fill-opacity="0.25" stroke="{DENSE}" stroke-width="8">' + ''.join(shape) + '</g>')
    x.dense.append(path(f'M {n(ox + 72)} {n(oy - 50)} L {n(ox + 115)} {n(oy - 40)} L {n(ox + 72)} {n(oy - 30)} Z'))
    x.dense.append(circle(ox + 50, oy - 55, 6))


def obj_banane(x, ox, oy):
    x.dense.append(path(f'M {n(ox - 110)} {n(oy - 50)} Q {n(ox - 20)} {n(oy + 70)} {n(ox + 110)} {n(oy - 30)} Q {n(ox + 100)} {n(oy - 10)} {n(ox + 95)} {n(oy)} Q {n(ox - 20)} {n(oy + 100)} {n(ox - 115)} {n(oy - 30)} Z',
                        opacity='0.8'))
    x.dense.append(rect(ox - 128, oy - 60, 22, 16, 4, transform=f'rotate(40 {n(ox - 117)} {n(oy - 52)})'))


def obj_krone(x, ox, oy):
    x.dense.append(poly([(ox - 85, oy + 45), (ox - 95, oy - 50), (ox - 45, oy - 5), (ox, oy - 70), (ox + 45, oy - 5),
                         (ox + 95, oy - 50), (ox + 85, oy + 45)]))
    for px, py in ((-95, -60), (0, -80), (95, -60)):
        x.dense.append(circle(ox + px, oy + py, 11))
    for px in (-45, 0, 45):
        x.holes.append(circle(ox + px, oy + 20, 11))


# ── Diagnoses ────────────────────────────────────────────────


def heart(x, b, broken=False):
    hx, hy = b.heart
    s = 70
    if not broken:
        x.organ.append(path(heart_path(hx, hy, s)))
        return
    crack = [(0, -0.5), (-0.14, -0.28), (0.1, -0.06), (-0.12, 0.2), (0.09, 0.44), (0, 0.9)]
    pts = lambda side: ' '.join(f'{n(hx + cx * s)},{n(hy + cy * s)}' for cx, cy in
                                [(side * 1.5, -1.5), (0, -1.5)] + crack + [(0, 1.5), (side * 1.5, 1.5)])
    x.defs.append(f'<clipPath id="halfL"><polygon points="{pts(-1)}"/></clipPath>')
    x.defs.append(f'<clipPath id="halfR"><polygon points="{pts(1)}"/></clipPath>')
    x.organ.append(f'<g transform="translate(-22 6) rotate(-14 {n(hx)} {n(hy)})"><path d="{heart_path(hx, hy, s)}" clip-path="url(#halfL)"/></g>')
    x.organ.append(f'<g transform="translate(22 0) rotate(14 {n(hx)} {n(hy)})"><path d="{heart_path(hx, hy, s)}" clip-path="url(#halfR)"/></g>')
    for (dx, dy, r) in ((-6, 0.1, 5), (8, 0.35, 4), (-4, 0.62, 3.5)):
        x.organ.append(circle(hx + dx, hy + dy * s, r))
    x.marks.append(circle(hx, hy, s * 1.45))


def fracture(x, end):
    """Close-up of one leg with a broken bone; deliberately not left or right."""
    x.transform = 'rotate(-14 450 640) translate(30 40)'
    x.tissue.append(ellipse(450, 330, 175, 640))
    feet = {
        'paw': lambda: (
            x.tissue.append(ellipse(450, 900, 200, 175)),
            [x.tissue.append(ellipse(450 + k * 78, 1035 - abs(k) * 12, 42, 52)) for k in (-1.5, -0.5, 0.5, 1.5)],
            x.tissue.append(ellipse(450, 935, 85, 60)),
        ),
        'hand': lambda: (
            x.tissue.append(ellipse(450, 880, 165, 140)),
            [x.tissue.append(ellipse(450 + k * 62, 1030, 30, 90, k * 6)) for k in (-1.5, -0.5, 0.5, 1.5)],
            x.tissue.append(ellipse(270, 900, 30, 80, 50)),
        ),
        'hoof': lambda: (
            x.tissue.append(ellipse(450, 900, 150, 120)),
            x.dense.append(path('M 330 960 L 570 960 L 610 1110 Q 450 1140 290 1110 Z', opacity='0.35')),
        ),
        'elephant': lambda: (
            x.tissue.append(ellipse(450, 930, 215, 175)),
            [x.dense.append(ellipse(450 + k * 80, 1085 - abs(k) * 10, 30, 18, opacity='0.6')) for k in (-1.5, -0.5, 0.5, 1.5)],
        ),
        'flipper': lambda: x.tissue.append(path('M 300 760 Q 250 980 380 1130 Q 460 1170 560 1110 Q 640 940 600 760 Z')),
        'webfoot': lambda: (
            x.tissue.append(ellipse(450, 860, 120, 100)),
            x.tissue.append(path('M 450 880 L 230 1110 Q 450 1060 670 1110 Z')),
        ),
        'claw': lambda: (
            x.tissue.append(ellipse(450, 900, 190, 150)),
            [x.tissue.append(ellipse(450 + k * 110, 1030, 46, 80, k * 10)) for k in (-1, 0, 1)],
        ),
    }
    feet[end]()

    # the two long bones: the thick one is broken, the thin one is fine
    x.bone(530, -120, 525, 760, 32)
    # broken shaft: two jagged pieces, the lower one shifted and tilted
    x.skeleton.append(poly([(379, -160), (441, -160), (446, 292), (434, 314), (421, 294), (408, 320), (394, 298), (382, 310)], stroke='none'))
    x.skeleton.append(poly([(416, 378), (427, 352), (440, 372), (453, 348), (466, 370), (480, 358), (456, 760), (394, 760)], stroke='none'))
    x.bone(425, 700, 424, 770, 62)
    x.dense += [poly([(372, 346), (388, 336), (384, 360)], opacity='0.6'), poly([(476, 318), (494, 312), (488, 332)], opacity='0.6'),
                poly([(452, 326), (462, 322), (458, 334)], opacity='0.5')]
    x.marks.append(circle(432, 336, 120))

    # wrist / ankle
    for i, (cx, cy) in enumerate([(395, 800), (450, 795), (505, 800), (420, 840), (480, 842)]):
        x.skeleton.append(ellipse(cx, cy, 24, 18, stroke='none'))
    if end == 'paw':
        for k in (-1.5, -0.5, 0.5, 1.5):
            x.bone(450 + k * 30, 868, 450 + k * 70, 975, 20)
            x.bone(450 + k * 72, 990, 450 + k * 80, 1045, 15)
    elif end == 'hand':
        for k in (-1.5, -0.5, 0.5, 1.5):
            x.bone(450 + k * 28, 868, 450 + k * 55, 950, 18)
            x.bone(450 + k * 58, 965, 450 + k * 62, 1030, 14)
            x.bone(450 + k * 63, 1045, 450 + k * 65, 1090, 12)
        x.bone(360, 860, 300, 900, 18)
        x.bone(290, 908, 250, 935, 14)
    elif end in ('hoof', 'elephant'):
        x.bone(450, 865, 450, 950, 46)
        x.bone(450, 965, 450, 1020, 42)
        x.skeleton.append(path('M 385 1030 L 515 1030 L 545 1100 Q 450 1115 355 1100 Z', stroke='none'))
    elif end == 'flipper':
        for k in (-1, 0, 1):
            x.bone(450 + k * 40, 870, 450 + k * 70, 1000, 22)
            x.bone(450 + k * 72, 1015, 450 + k * 78, 1090, 14)
    elif end == 'webfoot':
        for k in (-1, 0, 1):
            x.bone(450 + k * 30, 870, 450 + k * 110, 980, 16)
            x.bone(450 + k * 115, 995, 450 + k * 175, 1080, 12)
            x.dense.append(circle(450 + k * 182, 1092, 9, opacity='0.7'))
    elif end == 'claw':
        for k in (-1, 0, 1):
            x.bone(450 + k * 40, 870, 450 + k * 105, 990, 22)
            cx = 450 + k * 112
            x.dense.append(path(f'M {n(cx - 16)} 1080 Q {n(cx)} 1150 {n(cx + 22)} 1140 Q {n(cx + 12)} 1100 {n(cx + 16)} 1080 Z', opacity='0.8'))
            x.bone(450 + k * 108, 1005, cx, 1070, 16)
    x.seam('M 300 -40 Q 290 400 320 760')


# ── Catalogue ────────────────────────────────────────────────

TIERE = [
    # id, Name, Körper, Bruch-Typ, Gegenstand
    ('hase',    'HASE',     hase,    'paw',      obj_karotte),
    ('hund',    'HUND',     hund,    'paw',      obj_schluessel),
    ('katze',   'KATZE',    katze,   'paw',      obj_gloeckchen),
    ('baer',    'BÄR',      baer,    'paw',      obj_lego),
    ('pferd',   'PFERD',    pferd,   'hoof',     obj_hufeisen),
    ('pinguin', 'PINGUIN',  pinguin, 'flipper',  obj_fisch),
    ('elefant', 'ELEFANT',  elefant, 'elephant', obj_erdnuss),
    ('puppe',   'PUPPE',    puppe,   'hand',     obj_schnuller),
    ('dino',    'DINO',     dino,    'claw',     obj_auto),
    ('ente',    'ENTE',     ente,    'webfoot',  obj_gummiente),
    ('affe',    'AFFE',     affe,    'hand',     obj_banane),
    ('loewe',   'LÖWE',     loewe,   'paw',      obj_krone),
]

DIAGNOSEN = ['gesund', 'bruch', 'herz', 'gegenstand']


def render(index, tier, diagnose):
    tid, name, body_fn, bruch_typ, obj_fn = tier
    x = Xray(seed=index * 10 + DIAGNOSEN.index(diagnose) + 1)
    kind = 'GANZKÖRPER A.P.'
    if diagnose == 'bruch':
        fracture(x, bruch_typ)
        kind = 'DETAILAUFNAHME'
    else:
        b = body_fn(x)
        heart(x, b, broken=(diagnose == 'herz'))
        if diagnose == 'gegenstand':
            obj_fn(x, *b.belly)
    serial = f'TD-{index + 1:02d}{DIAGNOSEN.index(diagnose) + 1}'
    return x.svg((f'PATIENT: {name}', serial, kind))


def main():
    os.makedirs(OUT, exist_ok=True)
    for i, tier in enumerate(TIERE):
        for diagnose in DIAGNOSEN:
            with open(os.path.join(OUT, f'{tier[0]}-{diagnose}.svg'), 'w', encoding='utf-8') as fh:
                fh.write(render(i, tier, diagnose))
    print(f'{len(TIERE) * len(DIAGNOSEN)} Bilder in {os.path.normpath(OUT)} geschrieben.')


if __name__ == '__main__':
    main()
