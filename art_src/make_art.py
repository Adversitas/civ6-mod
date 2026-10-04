"""Generates all 2D art for the Assyria mod: icons + loading-screen leader art.

Style: Neo-Assyrian palace relief (profile figures, lapis-blue glazed brick, gold).
Everything is drawn procedurally with Pillow, supersampled for anti-aliasing,
then written as uncompressed RGBA .dds (the format Civ VI loads via <ImportFiles>).

    python art_src/make_art.py           -> writes Textures/*.dds and art_src/preview/*.png
"""
import math
import random
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT_DDS = ROOT / "Textures"
OUT_PNG = ROOT / "art_src" / "preview"

SS = 4  # supersampling factor

# Palette
LAPIS_LIGHT = (52, 92, 178)
LAPIS = (30, 62, 146)
LAPIS_DARK = (16, 34, 92)
GOLD = (222, 176, 72)
GOLD_DARK = (150, 108, 36)
SKIN = (196, 146, 102)
SKIN_SHADE = (160, 112, 74)
HAIR = (38, 27, 24)
HAIR_LIGHT = (104, 76, 54)
CROWN = (236, 226, 204)
CROWN_SHADE = (200, 188, 160)
RED = (150, 34, 38)
RED_DARK = (104, 22, 28)
BRONZE = (176, 128, 62)
BRONZE_LIGHT = (224, 180, 104)
BRONZE_DARK = (112, 76, 34)
WHITE = (255, 255, 255)
INK = (24, 16, 14)


# ----------------------------------------------------------------------------- helpers
class Canvas:
    """Draw in a virtual coordinate box; rendered at size*SS, downsampled on finish()."""

    def __init__(self, w, h, box=1000.0, bg=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.scale = (min(w, h) * SS) / box
        self.img = Image.new("RGBA", (w * SS, h * SS), bg)
        self.d = ImageDraw.Draw(self.img)
        self.ox = (w * SS - box * self.scale) / 2
        self.oy = (h * SS - box * self.scale) / 2

    def view(self, cx, cy, zoom):
        """Zoom so that box point (cx, cy) lands in the middle of the image."""
        self.scale *= zoom
        self.ox = self.w * SS / 2 - cx * self.scale
        self.oy = self.h * SS / 2 - cy * self.scale

    def p(self, x, y):
        return (self.ox + x * self.scale, self.oy + y * self.scale)

    def pts(self, pts):
        return [self.p(x, y) for x, y in pts]

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon(self.pts(pts), fill=fill)
        if outline and width:
            self.line(list(pts) + [pts[0]], outline, width)

    def line(self, pts, fill, width):
        self.d.line(self.pts(pts), fill=fill, width=max(1, int(width * self.scale)), joint="curve")

    def circle(self, cx, cy, r, fill=None, outline=None, width=0):
        x0, y0 = self.p(cx - r, cy - r)
        x1, y1 = self.p(cx + r, cy + r)
        self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline,
                       width=max(1, int(width * self.scale)) if outline else 0)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=0):
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline,
                       width=max(1, int(width * self.scale)) if outline else 0)

    def finish(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


def bezier(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3
        b = 3 * (1 - t) ** 2 * t
        c = 3 * (1 - t) * t ** 2
        d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def rosette(c, cx, cy, r, petal=WHITE, center=GOLD, n=8):
    """Assyrian rosette: n round petals around a gold center."""
    for i in range(n):
        a = 2 * math.pi * i / n
        c.circle(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, r * 0.42, fill=petal)
    c.circle(cx, cy, r * 0.35, fill=center)


def star(c, cx, cy, r, fill, points=8):
    pts = []
    for i in range(points * 2):
        rr = r if i % 2 == 0 else r * 0.42
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    c.poly(pts, fill)


def curl_rows(c, x0, x1, y0, y1, r, base, light, stagger=True):
    """Rows of spiral curls (the classic Assyrian beard/hair texture)."""
    row = 0
    y = y0 + r
    while y <= y1 - r * 0.5:
        x = x0 + r + (r if (stagger and row % 2) else 0)
        while x <= x1 - r * 0.5:
            c.circle(x, y, r, fill=base)
            c.circle(x - r * 0.15, y - r * 0.15, r * 0.62, fill=light)
            c.circle(x - r * 0.05, y - r * 0.05, r * 0.3, fill=base)
            x += r * 2
        y += r * 1.75
        row += 1


def clip_to(img, mask_img):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask_img)
    return out


# ----------------------------------------------------------------------------- the king
def draw_king(c, full=False, detail=False):
    """Tiglath-Pileser III in profile, facing left, in a 1000x1000 box (head ~ upper half).
    full=True extends the robe and adds a mace for the loading-screen figure.
    detail=True adds ink outlines, finer curls and ornament (large diplomacy-screen art)."""
    def ink(pts, w=3.0):
        if detail:
            c.line(list(pts) + [pts[0]], INK, w)
    curl = 12 if detail else 16
    # --- robe / shoulders
    if full:
        robe = [(150, 1000), (190, 860), (300, 790), (470, 770), (640, 780), (790, 850), (860, 1000)]
    else:
        robe = [(150, 1000), (200, 880), (310, 810), (470, 790), (640, 800), (790, 870), (850, 1000)]
    c.poly(robe, RED)
    if detail:  # woven pattern on the robe
        for y in range(860, 1000, 46):
            c.line([(190, y), (850, y - 10)], RED_DARK, 4)
    ink(robe)
    # fringed shawl band across the chest
    band = [(250, 1000), (330, 820), (420, 805), (360, 1000)]
    c.poly(band, GOLD_DARK)
    for i in range(9):
        t = i / 9
        x = 330 + (250 - 330) * t + 5
        y = 820 + (1000 - 820) * t
        c.poly([(x, y), (x + 40, y - 4), (x + 34, y + 14), (x - 4, y + 18)], GOLD)
    for i in range(7):  # rosettes on the robe
        rosette(c, 520 + (i % 3) * 95, 880 + (i // 3) * 70, 20, petal=(230, 200, 150), center=GOLD)

    # --- ribbons of the diadem, falling behind
    c.poly([(640, 300), (668, 300), (735, 640), (712, 648)], RED_DARK)
    c.poly([(668, 300), (690, 305), (770, 600), (750, 610)], RED)
    for y in (420, 500, 580):
        c.line([(660 + (y - 300) * 0.2, y), (690 + (y - 300) * 0.22, y - 6)], GOLD, 5)

    # --- hair mass falling to the shoulders
    hair = [(560, 300), (660, 320), (700, 420), (715, 560), (730, 700), (700, 800),
            (600, 815), (540, 760), (545, 560)]
    c.poly(hair, HAIR)
    curl_rows(c, 560, 725, 640, 810, curl, HAIR, HAIR_LIGHT)
    ink(hair)
    for y in range(380, 640, 26):  # wavy strands
        c.line([(575, y), (620, y + 8), (665, y), (705, y + 8)], HAIR_LIGHT, 4)

    # --- neck
    c.poly([(450, 660), (560, 660), (585, 820), (430, 830)], SKIN_SHADE)

    # --- face (profile, facing left)
    face = [(455, 330), (430, 360), (418, 395), (410, 420), (385, 450), (352, 488),
            (360, 500), (392, 506), (388, 528), (420, 560), (560, 560), (575, 470),
            (565, 380), (540, 330)]
    c.poly(face, SKIN)
    if detail:  # soft modelling on brow, nose and lips
        c.poly([(418, 395), (455, 335), (470, 340), (440, 400)], (214, 166, 120))
        c.poly([(385, 450), (410, 420), (418, 440), (395, 470)], (214, 166, 120))
        c.line([(360, 492), (392, 500)], SKIN_SHADE, 3)
    c.poly([(520, 440), (575, 470), (560, 560), (500, 560)], SKIN_SHADE)  # cheek shadow
    ink(face)

    # --- ear + earring
    c.ellipse(548, 455, 20, 32, fill=SKIN_SHADE)
    c.ellipse(548, 455, 10, 20, fill=SKIN)
    c.line([(548, 488), (548, 515)], GOLD_DARK, 4)
    c.ellipse(548, 528, 10, 15, fill=GOLD)

    # --- beard: long, squared, rows of curls
    beard = [(388, 520), (430, 548), (545, 548), (590, 600), (600, 760), (560, 790),
             (420, 790), (390, 740), (380, 600)]
    c.poly(beard, HAIR)
    curl_rows(c, 385, 600, 560, 785, curl, HAIR, HAIR_LIGHT)
    ink(beard)
    for y in (640, 720):  # gold beard bands
        c.line([(384, y), (598, y)], GOLD_DARK, 7)
    # moustache
    c.poly([(385, 507), (430, 500), (470, 512), (470, 530), (420, 528), (380, 522)], HAIR)
    c.line([(392, 512), (465, 518)], HAIR_LIGHT, 3)
    # sideburn joining hair and beard
    c.poly([(520, 380), (560, 360), (575, 470), (545, 548), (500, 545), (530, 470)], HAIR)
    curl_rows(c, 505, 575, 470, 545, 12, HAIR, HAIR_LIGHT)

    # --- eye: frontal almond eye, typical of reliefs
    c.ellipse(452, 420, 26, 12, fill=(242, 236, 222), outline=INK, width=4)
    c.circle(446, 420, 9, fill=INK)
    if detail:
        c.circle(443, 417, 3, fill=(242, 236, 222))  # catch-light
        for dx in (-18, -8, 2, 12):  # lashes
            c.line([(452 + dx, 408), (450 + dx, 401)], INK, 2)
    # heavy brow
    c.poly([(418, 395), (470, 388), (510, 398), (508, 406), (468, 398), (422, 404)], HAIR)

    # --- crown: royal tiara (truncated cone + point), banded
    crown = [(430, 345), (650, 318), (628, 170), (462, 180)]
    c.poly(crown, CROWN)
    ink(crown)
    c.poly([(560, 175), (628, 170), (650, 318), (590, 326)], CROWN_SHADE)
    c.poly([(520, 178), (566, 175), (548, 105)], CROWN)  # the royal point
    c.poly([(548, 105), (566, 175), (556, 176)], CROWN_SHADE)
    for (yl, yr) in ((345, 318), (300, 278), (225, 205)):  # gold bands
        c.poly([(430 + (yl - 345) * -0.15, yl), (650 + (yr - 318) * 0.15, yr),
                (650 + (yr - 318) * 0.15, yr - 16), (430 + (yl - 345) * -0.15, yl - 16)], GOLD)
    for i in range(5):  # rosettes between the bands
        x = 470 + i * 40
        y = 262 - i * 5
        rosette(c, x, y, 14, petal=RED, center=GOLD, n=8)
    # diadem band across the crown base
    c.poly([(428, 352), (652, 324), (652, 340), (428, 368)], GOLD_DARK)
    if detail:  # zig-zag gold work on the lower band
        for i in range(11):
            x = 438 + i * 20
            y = 333 - i * 2.4
            c.line([(x, y), (x + 10, y - 12), (x + 20, y)], GOLD_DARK, 3)
        ink([(548, 105), (566, 175), (520, 178)])

    if full:
        # mace held in front of the chest
        c.line([(250, 760), (330, 1000)], BRONZE_DARK, 18)
        c.circle(245, 745, 34, fill=BRONZE)
        c.circle(237, 737, 18, fill=BRONZE_LIGHT)
        # hand
        c.ellipse(295, 900, 34, 26, fill=SKIN)
        c.line([(275, 892), (318, 892)], SKIN_SHADE, 4)


# ----------------------------------------------------------------------------- the soldier
def draw_soldier(c, color=True):
    """Kisir Sharruti infantryman, facing left: pointed helmet, scale armour, round shield, spear."""
    col = (lambda rgb: rgb) if color else (lambda rgb: WHITE)
    cut = (0, 0, 0, 0)

    # spear behind
    c.line([(690, 40), (650, 980)], col(BRONZE_DARK), 16)
    c.poly([(692, 0), (712, 70), (690, 110), (672, 66)], col(BRONZE_LIGHT))

    # body with scale armour
    body = [(330, 980), (360, 700), (440, 620), (620, 620), (720, 700), (740, 980)]
    c.poly(body, col(BRONZE))
    if color:
        for row, y in enumerate(range(650, 990, 34)):
            off = 22 if row % 2 else 0
            for x in range(350 + off, 740, 44):
                c.ellipse(x, y, 22, 20, fill=BRONZE_DARK)
                c.ellipse(x, y - 4, 19, 16, fill=BRONZE_LIGHT if (x + y) % 3 else BRONZE)
        c.poly([(330, 980), (360, 900), (740, 900), (740, 980)], RED)  # kilt

    # neck + head
    c.poly([(470, 560), (580, 560), (590, 650), (460, 650)], col(SKIN_SHADE))
    head = [(470, 330), (448, 380), (440, 410), (410, 450), (420, 466), (445, 470), (445, 500),
            (480, 540), (600, 540), (615, 420), (600, 340)]
    c.poly(head, col(SKIN))
    if color:
        c.poly([(560, 420), (615, 420), (600, 540), (545, 540)], SKIN_SHADE)
    # short beard
    c.poly([(440, 490), (478, 498), (590, 500), (605, 600), (560, 640), (465, 640), (440, 590)],
           col(HAIR))
    if color:
        curl_rows(c, 442, 605, 505, 638, 14, HAIR, HAIR_LIGHT)
        c.ellipse(492, 418, 20, 9, fill=(242, 236, 222), outline=INK, width=4)
        c.circle(487, 418, 7, fill=INK)
        c.poly([(458, 398), (520, 392), (522, 400), (460, 406)], HAIR)
    else:
        c.ellipse(492, 418, 18, 8, fill=cut)  # eye cut-out keeps the icon readable

    # pointed helmet with cheek guard
    helmet = [(452, 360), (630, 345), (612, 230), (548, 70), (478, 235)]
    c.poly(helmet, col(BRONZE))
    if color:
        c.poly([(548, 70), (612, 230), (630, 345), (570, 352)], BRONZE_DARK)
        c.poly([(450, 352), (632, 336), (634, 362), (452, 378)], BRONZE_LIGHT)  # rim
        c.poly([(585, 360), (630, 355), (622, 470), (590, 470)], BRONZE)  # cheek guard
    else:
        c.poly([(452, 362), (632, 346), (632, 352), (452, 368)], cut)

    # round shield in front
    c.circle(400, 760, 215, fill=col(BRONZE_DARK))
    c.circle(400, 760, 195, fill=col(BRONZE))
    if color:
        for r, f in ((160, BRONZE_LIGHT), (148, BRONZE), (100, BRONZE_DARK), (90, BRONZE), (40, BRONZE_LIGHT)):
            c.circle(400, 760, r, fill=f)
        for i in range(12):
            a = 2 * math.pi * i / 12
            c.circle(400 + math.cos(a) * 172, 760 + math.sin(a) * 172, 9, fill=BRONZE_DARK)
    else:
        c.circle(400, 760, 150, outline=cut, width=14)
        c.circle(400, 760, 48, fill=cut)
        c.circle(400, 760, 30, fill=WHITE)


# ----------------------------------------------------------------------------- assets
def civ_symbol(size):
    """Winged sun disk: white silhouette (the game tints it with player colours)."""
    c = Canvas(size, size)
    # wings: layered feather rows, longest on top
    for side in (-1, 1):
        for k in range(4):
            y0 = 395 + k * 52
            reach = 445 - k * 85
            inner = 500 + side * 95
            outer = 500 + side * reach
            pts = [(inner, y0), (outer, y0 + 6), (outer - side * 22, y0 + 44), (inner, y0 + 44)]
            c.poly(pts, WHITE)
            # feather notches along the outer edge
            for n in range(1, 4):
                fx = outer - side * (n * reach * 0.12)
                c.poly([(fx, y0 + 44), (fx + side * 14, y0 + 44), (fx + side * 7, y0 + 30)], (0, 0, 0, 0))
    # tail fan
    c.poly([(440, 575), (560, 575), (630, 760), (370, 760)], WHITE)
    for x in (430, 470, 500, 530, 570):
        c.line([(500 + (x - 500) * 0.5, 600), (x + (x - 500) * 0.3, 760)], (0, 0, 0, 0), 9)
    # streamers curling down
    for side in (-1, 1):
        c.line(bezier((500 + side * 70, 560), (500 + side * 170, 600), (500 + side * 120, 720),
                      (500 + side * 220, 760)), WHITE, 22)
    # the disk (ring + center)
    c.circle(500, 440, 125, fill=WHITE)
    c.circle(500, 440, 88, fill=(0, 0, 0, 0))
    c.circle(500, 440, 52, fill=WHITE)
    return c.finish()


def leader_icon(size):
    """Round leader portrait with a gold frame."""
    c = Canvas(size, size)
    # lapis background with gold stars
    c.circle(500, 500, 480, fill=LAPIS_DARK)
    c.circle(500, 500, 450, fill=LAPIS)
    rnd = random.Random(7)
    for _ in range(14):
        a, rr = rnd.random() * 2 * math.pi, 120 + rnd.random() * 300
        star(c, 500 + math.cos(a) * rr, 500 + math.sin(a) * rr, 12, (200, 170, 90))
    # king, scaled into the circle (head centered)
    king = Canvas(size, size)
    king.view(530, 470, 1.3)  # head and beard fill the circle
    draw_king(king)
    k = king.img
    mask = Image.new("L", k.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([c.p(50, 50), c.p(950, 950)], fill=255)
    c.img.alpha_composite(clip_to(k, mask))
    # frame
    c.circle(500, 500, 470, outline=GOLD_DARK, width=34)
    c.circle(500, 500, 462, outline=GOLD, width=16)
    return c.finish()


def district_icon(size, fow=False):
    """Ekal Masharti: palace gate between two crenellated towers, shaded like base-game district icons."""
    if fow:
        light, mid, dark = (170, 170, 170), (128, 128, 128), (88, 88, 88)
    else:
        light, mid, dark = (206, 222, 238), (150, 174, 204), (92, 114, 150)
    c = Canvas(size, size)
    # platform
    c.poly([(90, 800), (910, 800), (950, 900), (50, 900)], dark)
    # wall
    c.poly([(150, 430), (850, 430), (850, 800), (150, 800)], mid)
    # towers
    for x0 in (120, 640):
        c.poly([(x0, 330), (x0 + 240, 330), (x0 + 240, 800), (x0, 800)], light)
        c.poly([(x0 + 170, 330), (x0 + 240, 330), (x0 + 240, 800), (x0 + 170, 800)], mid)
        for k in range(4):  # crenellations
            cx = x0 + 10 + k * 60
            c.poly([(cx, 270), (cx + 40, 270), (cx + 40, 330), (cx, 330)], light)
    for k in range(5):
        cx = 375 + k * 52
        c.poly([(cx, 385), (cx + 32, 385), (cx + 32, 430), (cx, 430)], light)
    # gate arch
    arch = [(400, 800), (400, 600)] + bezier((400, 600), (400, 470), (600, 470), (600, 600), 20) + [(600, 800)]
    c.poly(arch, dark)
    # rosette band over the gate
    for k in range(4):
        rosette(c, 410 + k * 60, 455, 18, petal=light, center=(222, 176, 72) if not fow else light)
    return c.finish()


def diplomacy_leader():
    """800x1080 detailed figure for the diplomacy screen (same pose as the loading art, more defined)."""
    w, h = 800, 1080
    c = Canvas(w, h, box=1000)
    c.scale = h * SS / 960
    c.ox = w * SS / 2 - 505 * c.scale
    c.oy = -50 * c.scale
    draw_king(c, full=True, detail=True)
    return c.finish()


def unit_portrait(size):
    c = Canvas(size, size)
    draw_soldier(c, color=True)
    return c.finish()


def unit_icon(size):
    c = Canvas(size, size)
    draw_soldier(c, color=False)
    return c.finish()


def loading_foreground():
    """800x1080 leader figure on transparency for the loading screen."""
    w, h = 800, 1080
    c = Canvas(w, h, box=1000)
    # fill the height: box y 80..1000 -> image 0..1080, figure centered horizontally
    c.scale = h * SS / 920
    c.ox = w * SS / 2 - 505 * c.scale
    c.oy = -80 * c.scale
    draw_king(c, full=True)
    return c.finish()


def loading_background():
    """1920x960 lapis glazed-brick wall with rosette friezes (Ishtar-gate style)."""
    w, h = 1920, 960
    img = Image.new("RGBA", (w, h), LAPIS + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    bw, bh = 96, 40
    for row in range(h // bh + 1):
        off = (bw // 2) if row % 2 else 0
        for col in range(-1, w // bw + 2):
            x0, y0 = col * bw + off, row * bh
            v = rnd.randint(-14, 14)
            base = tuple(max(0, min(255, ch + v)) for ch in LAPIS)
            d.rectangle([x0 + 2, y0 + 2, x0 + bw - 2, y0 + bh - 2], fill=base + (255,))
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    c = Canvas(w, h, box=960)
    c.img = img.resize((w * SS, h * SS), Image.LANCZOS)
    c.d = ImageDraw.Draw(c.img)
    c.ox, c.oy, c.scale = 0, 0, SS
    for y0 in (90, 790):
        c.d.rectangle([0, y0 * SS, w * SS, (y0 + 80) * SS], fill=LAPIS_DARK)
        c.d.rectangle([0, (y0 - 6) * SS, w * SS, y0 * SS], fill=GOLD)
        c.d.rectangle([0, (y0 + 80) * SS, w * SS, (y0 + 86) * SS], fill=GOLD)
        for x in range(40, w, 96):
            rosette(c, x, y0 + 40, 30, petal=(240, 236, 226), center=GOLD)
    return c.img.resize((w, h), Image.LANCZOS)


# ----------------------------------------------------------------------------- output
def write_dds(img, path):
    """Uncompressed 32-bit RGBA DDS, same layout the game accepts for imported UI textures."""
    img = img.convert("RGBA")
    w, h = img.size
    header = struct.pack(
        "<4sIIIIIII44sIIIIIIIIIIIII",
        b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1, b"\x00" * 44,
        32, 0x41, 0, 32, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000,
        0x1000, 0, 0, 0, 0)
    path.write_bytes(header + img.tobytes())


ICON_SETS = {
    # name prefix: (generator, sizes) ; sizes match the base game's atlases
    "Assyria_Civ": (civ_symbol, [22, 30, 36, 44, 45, 48, 50, 64, 80, 256]),
    "Assyria_Leader": (leader_icon, [32, 45, 50, 55, 64, 80, 256]),
    "Assyria_UU": (unit_icon, [22, 32, 38, 50, 80, 256]),
    "Assyria_UU_Portrait": (unit_portrait, [38, 50, 70, 95, 200, 256]),
    "Assyria_UD": (district_icon, [22, 32, 38, 50, 80, 128, 256]),
}


def main():
    OUT_DDS.mkdir(exist_ok=True)
    OUT_PNG.mkdir(parents=True, exist_ok=True)
    for prefix, (fn, sizes) in ICON_SETS.items():
        big = fn(256)
        big.save(OUT_PNG / f"{prefix}.png")
        for s in sizes:
            img = big if s == 256 else fn(s)
            write_dds(img, OUT_DDS / f"{prefix}{s}.dds")
    write_dds(district_icon(256, fow=True), OUT_DDS / "Assyria_UD_FOW256.dds")
    district_icon(256, fow=True).save(OUT_PNG / "Assyria_UD_FOW.png")
    diplo = diplomacy_leader()
    diplo.save(OUT_PNG / "Assyria_Diplomacy_Leader.png")
    write_dds(diplo, OUT_DDS / "Assyria_Diplomacy_Leader.dds")
    fg = loading_foreground()
    bg = loading_background()
    fg.save(OUT_PNG / "Assyria_Loading_Leader.png")
    bg.save(OUT_PNG / "Assyria_Loading_Background.png")
    write_dds(fg, OUT_DDS / "Assyria_Loading_Leader.dds")
    write_dds(bg, OUT_DDS / "Assyria_Loading_Background.dds")
    # composite preview of the loading screen
    comp = bg.copy()
    comp.alpha_composite(fg.resize((int(800 * 0.889), 960)), (1920 - 760, 0))
    comp.save(OUT_PNG / "Assyria_Loading_Composite.png")
    print("done:", len(list(OUT_DDS.glob("*.dds"))), "dds files")


if __name__ == "__main__":
    main()
