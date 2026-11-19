"""Pixel District: a 320x200 pixel-art room at night, drawn in code.

A night room with rain on the window, a blinking city, a bed, plants, a shelf, and two cats. The grey
desk cat codes at the monitor while Claude works; the orange cat watches from the sill.

Writes scene/scene.svg (root class "work") and plugin/hooks/scene.ts (the same SVG as a string the
mod imports). The mod swaps the root class to show what Claude is doing (see docs/CUSTOMIZE.md).
Static pixels are merged into one stroked path per colour (cap: 131,072 chars).
Run: python3 tools/gen_scene.py
"""
import random
from pathlib import Path

W, H = 320, 200
OUT = Path(__file__).resolve().parent.parent / "scene"

C = {
    # room
    "ceil": "#140f2b", "ceil2": "#1a1436", "cove": "#8f7af0", "cove2": "#5a47b8",
    "wall": "#2a1f57", "wall2": "#271c51", "walllt": "#33266a", "wallsh": "#211848",
    "base": "#18112e", "base2": "#2a2050",
    "floor": "#2b1a42", "floor2": "#26173b", "floorlt": "#36224f", "seam": "#1c1130",
    # window
    "frame": "#1a1336", "framelt": "#2e2459", "sill": "#6b4f88", "silllt": "#8a6cab", "sillsh": "#1c1440",
    "blind": "#4c3c82", "blind2": "#3a2d69", "blindlt": "#5f4d9a",
    "sky0": "#0a0820", "sky1": "#0e0b2b", "sky2": "#130f36", "sky3": "#191343", "sky4": "#20184f", "sky5": "#291e5c",
    "star": "#c8c0ff", "star2": "#8f86d8", "moon": "#ffe6ad", "moon2": "#e8c98a", "moon3": "#fff4d1",
    "bfar": "#1d1747", "bfar2": "#231b52", "bnear": "#2c2163", "bnear2": "#352872", "bedge": "#4a3a92",
    "win": "#ffb347", "win2": "#ffd27a", "windim": "#c97c2e", "winv": "#a68cff", "winc": "#7ae0ff",
    "neon": "#ff5c9a", "street": "#3b2c72", "street2": "#4a3887",
    # furniture
    "wood": "#583451", "woodd": "#41263f", "woodl": "#7a4a68", "woodhl": "#95627f",
    "blanket": "#3a55a0", "blanketl": "#5472c2", "blanketd": "#2b3e78", "blanketdd": "#22316a",
    "sheet": "#c6bfe6", "sheetd": "#a29bd0", "pillow": "#8b77d6", "pillowl": "#a894ea", "pillowd": "#6f5cbd",
    "rug": "#43347f", "rugb": "#6652b4", "rugd": "#372a6b",
    "poster": "#1d1640", "postera": "#ff8a5c", "posterb": "#6f58d8", "posterc": "#ffcf6e", "posterd": "#4a3aa0",
    "book1": "#c45b7a", "book2": "#4f7ccc", "book3": "#d99a3c", "book4": "#6b9f7a", "book5": "#8a6bd8", "book6": "#e0d6ff",
    "plant": "#3f9a73", "plant2": "#2b7155", "plant3": "#5bb88d", "pot": "#b8694a", "pot2": "#8f4e38", "pot3": "#d08562",
    # desk set
    "bezel": "#100c1f", "bezel2": "#221a3e", "screen": "#1b2a66", "screen2": "#16225a", "stand": "#2a2140",
    "tower": "#17112a", "tower2": "#251c42", "towerhl": "#3a2f62", "led": "#7ae0ff", "led2": "#ff7ad9",
    "key": "#3e3468", "key2": "#5a4d92", "keyhl": "#8170c8", "mouse": "#5a4d92",
    "mug": "#ece5ff", "mug2": "#b9aee2", "coffee": "#4a2e24",
    "chair": "#231b3d", "chair2": "#3a2e62", "chair3": "#14101f", "chairhl": "#4a3c7a",
    "lampc": "#2a2140", "shade": "#3b2f5c", "shadehl": "#52427e", "bulb": "#fff1c4",
    # person
    "hair": "#1e1426", "hairhl": "#3d2a55", "hood": "#6c50c8", "hood2": "#5640a6", "hood3": "#45338a",
    "hoodhl": "#8a70e0", "rim": "#93a9ff", "skin": "#e2a47c", "skin2": "#c4835e",
    "phones": "#ff7a9a", "phones2": "#c9506f",
    "pants": "#463c8f", "pants2": "#342c72", "pantshl": "#6457b8", "shoe": "#171329", "sole": "#d6cff5",
    # cat
    "catO": "#e48a3c", "catD": "#bf6929", "catL": "#f6ad62", "catW": "#f6deb3", "catE": "#2a1a14",
    "catG": "#fff3c8", "catN": "#ec8592", "catP": "#f1a1a8",
    "rain": "#a9b8ff", "steam": "#d9d2ff",
    "strip": "#ffd27a", "strip2": "#e0a64e",
    "halo1": "#1d1847", "halo2": "#141137", "neonhalo": "#4a2257",
    "gcat": "#9ea3c4", "gcatd": "#737899", "gcatl": "#c6c9e2", "gcatw": "#eef0fb", "gcato": "#3a3560",
    "gcate": "#8ff0a8", "gcatk": "#1b1a2e", "gcatn": "#f09aa6", "gcatp": "#e8a0b8",
}


class Canvas:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.px = {}

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h and c:
            self.px[(x, y)] = C.get(c, c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def sprite(self, ox, oy, rows, key):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch not in ". ":
                    self.set(ox + i, oy + j, key[ch])

    def dither(self, x, y, w, h, a, b, phase=0):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, a if (xx + yy + phase) % 2 else b)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r + r * 0.6:
                    self.set(xx, yy, c)

    def paths(self):
        by_color, rows = {}, {}
        for (x, y), c in self.px.items():
            rows.setdefault(y, {})[x] = c
        for y in sorted(rows):
            row = rows[y]
            xs = sorted(row)
            start = prev = xs[0]
            col = row[start]
            for x in xs[1:] + [None]:
                if x is not None and x == prev + 1 and row[x] == col:
                    prev = x
                    continue
                by_color.setdefault(col, []).append(f"M{start} {y}h{prev - start + 1}")
                if x is not None:
                    start = prev = x
                    col = row[x]
        return "".join(f'<path stroke="{c}" d="{"".join(d)}"/>' for c, d in by_color.items())


def sprite_canvas(ox, oy, rows, key):
    c = Canvas()
    c.sprite(ox, oy, rows, key)
    return c


random.seed(23)
bg = Canvas()

# ================= room shell =================
bg.rect(0, 0, W, 14, "ceil")
bg.rect(0, 11, W, 3, "ceil2")
bg.hline(0, 14, W, "cove")
bg.hline(0, 15, W, "cove2")
bg.rect(0, 16, W, 138, "wall")
bg.rect(0, 16, W, 2, "walllt")
for x in range(14, W, 22):  # wallpaper stripes
    bg.vline(x, 19, 135, "wall2")
bg.rect(0, 149, W, 5, "wallsh")  # shadow at the wall's foot
bg.hline(0, 154, W, "base2")
bg.rect(0, 155, W, 2, "base")
bg.rect(0, 157, W, 43, "floor")
for y in range(163, H, 8):
    bg.hline(0, y, W, "seam")
for i, y0 in enumerate(range(157, H, 8)):
    off = (i * 17) % 41
    for x in range(off, W, 41):
        bg.vline(x, y0, 6, "floor2")
# moonlight from the window on the floor (stepped patch, plank seams kept)
for i, y in enumerate(range(157, H)):
    x0 = 100 - i // 2
    x1 = 210 + i // 3
    for x in range(x0, x1):
        if bg.px.get((x, y)) == C["floor"]:
            bg.set(x, y, "floorlt")

# ================= window =================
WX0, WX1, WY0, WY1 = 98, 206, 30, 116
GX0, GX1, GY0, GY1 = 102, 202, 46, 110
bg.rect(WX0, WY0, WX1 - WX0 + 1, WY1 - WY0 + 1, "frame")
bg.hline(WX0, WY0, WX1 - WX0 + 1, "framelt")
bg.vline(WX0, WY0, WY1 - WY0 + 1, "framelt")
# sky bands
bands = [("sky0", 46, 10), ("sky1", 56, 10), ("sky2", 66, 10), ("sky3", 76, 10), ("sky4", 86, 12), ("sky5", 98, 13)]
for c, y, h in bands:
    bg.rect(GX0, y, GX1 - GX0 + 1, h, c)
# (band edges left hard: dithering costs too many runs)
for _ in range(34):
    bg.set(random.randint(GX0, GX1), random.randint(GY0 + 1, 80), random.choice(["star", "star", "star2"]))
for yy in range(48, 69):  # LIGHT v4: stepped pixel halo, not a soft glow
    for xx in range(174, 195):
        d2 = (xx - 184) ** 2 + (yy - 58) ** 2
        if bg.px.get((xx, yy)) in (C["sky0"], C["sky1"]):
            if d2 <= 64:
                bg.set(xx, yy, "halo1")
            elif d2 <= 100:
                bg.set(xx, yy, "halo2")
bg.disc(184, 58, 6, "moon2")
bg.disc(183, 57, 5, "moon")
bg.set(181, 55, "moon3"); bg.set(182, 55, "moon3"); bg.set(181, 56, "moon3")
bg.set(186, 59, "moon2"); bg.set(184, 61, "moon2")
# far skyline
x = GX0
while x <= GX1:
    w = random.randint(5, 11)
    top = random.randint(70, 88)
    bg.rect(x, top, w, GY1 - top + 1, "bfar")
    bg.vline(x + w - 1, top, GY1 - top + 1, "bfar2")
    for wy in range(top + 3, GY1, 4):
        for wx in range(x + 2, x + w - 2, 3):
            if random.random() < 0.12:
                bg.set(wx, wy, "windim")
    x += w
# near skyline with windows; remember lit ones for blinking
lit = []
neon_at = None
x = GX0 - 3
while x <= GX1:
    w = random.randint(11, 19)
    top = random.randint(80, 98)
    bg.rect(x, top, w, GY1 - top + 1, "bnear")
    bg.rect(x, top, w // 3, GY1 - top + 1, "bnear2")  # lit left face
    bg.hline(x, top, w, "bedge")
    if random.random() < 0.45:
        bg.rect(x + w // 2, top - 5, 1, 5, "bedge")
        bg.set(x + w // 2, top - 6, "neon")
    elif random.random() < 0.4:
        bg.rect(x + 2, top - 3, 4, 3, "bnear2")  # water tank
        bg.hline(x + 2, top - 3, 4, "bedge")
    for wy in range(top + 3, GY1 - 2, 3):
        for wx in range(x + 2, x + w - 2, 3):
            r = random.random()
            if r < 0.24:
                bg.rect(wx, wy, 2, 1, random.choice(["win", "win", "win2"]))
                lit.append((wx, wy))
            elif r < 0.31:
                bg.rect(wx, wy, 2, 1, "windim")
            elif r < 0.34:
                bg.rect(wx, wy, 2, 1, random.choice(["winv", "winc"]))
    if neon_at is None and x > GX0 + 20 and w >= 13:
        neon_at = (x + 3, top + 4)
    x += w + random.randint(0, 3)
bg.rect(GX0, GY1 - 3, GX1 - GX0 + 1, 3, "street")
bg.hline(GX0, GY1 - 4, GX1 - GX0 + 1, "street2")
# blinds rolled up at the top
for i, y in enumerate(range(34, 46)):
    bg.hline(102, y, 101, "blind" if i % 2 == 0 else "blind2")
bg.hline(102, 34, 101, "blindlt")
bg.hline(102, 45, 101, "frame")
for x in (114, 140, 166, 192):
    bg.vline(x, 46, 6, "blind2")
    bg.set(x, 52, "blindlt")
# mullion and frame repaint over overflow
bg.rect(151, 46, 3, 65, "frame")
bg.vline(151, 46, 65, "framelt")
bg.rect(WX0, WY0, 4, WY1 - WY0 + 1, "frame")
bg.vline(WX0, WY0, WY1 - WY0 + 1, "framelt")
bg.rect(WX1 - 3, WY0, 4, WY1 - WY0 + 1, "frame")
bg.rect(GX0, 111, GX1 - GX0 + 1, 2, "frame")
# sill
bg.rect(92, 111, 121, 4, "sill")
bg.hline(92, 111, 121, "silllt")
bg.hline(92, 115, 121, "sillsh")
bg.rect(92, 116, 121, 2, "wallsh")

# ================= wall decor =================
# poster
bg.rect(48, 46, 28, 34, "frame")
bg.rect(50, 48, 24, 30, "poster")
bg.rect(50, 64, 24, 14, "posterb")
bg.disc(62, 57, 4, "posterc")
bg.sprite(50, 66, [
    "..........aaaa..........",
    "......aaaaaaaaaa........",
    "...aaaaaaaaaaaaaaaa.....",
    "aaaaaaaaaaaaaaaaaaaaaaa.",
    "ddddddddddddddddddddddda",
    "dddddddddddddddddddddddd",
], {"a": "postera", "d": "posterd"})
bg.hline(48, 46, 28, "framelt")
# shelf above the desk with books, a frame and a small plant
bg.rect(240, 66, 78, 3, "wood")
bg.hline(240, 66, 78, "woodhl")
bg.hline(240, 69, 78, "strip2")
bg.hline(242, 69, 74, "strip")                # warm LED strip on the shelf's underside
bg.rect(241, 69, 1, 3, "woodd"); bg.rect(316, 69, 1, 3, "woodd")   # brackets
# left end of the shelf: a little succulent and a tiny framed print
bg.sprite(246, 58, [".p.p.", "pPpPp", ".pLp.", "ooooo", "oOOOo", ".ooo.", ".ooo.", ".ooo."],
          {"p": "plant", "P": "plant2", "L": "plant3", "o": "pot", "O": "pot3"})
bg.rect(256, 56, 8, 10, "frame")
bg.rect(257, 57, 6, 8, "posterd")
bg.rect(258, 61, 4, 3, "postera")
bg.set(260, 59, "posterc")
bx = 284
for h, c, w in [(13, "book1", 3), (11, "book2", 3), (14, "book3", 2), (10, "book4", 3), (12, "book5", 3), (9, "book6", 2)]:
    bg.rect(bx, 66 - h, w, h, c)
    bg.hline(bx, 66 - h, w, "book6" if c != "book6" else "book2")
    bx += w + 1
bg.rect(305, 57, 6, 9, "frame")  # tiny photo
bg.rect(306, 58, 4, 7, "posterb")
bg.sprite(312, 54, ["..pp.", ".pPPp", "pPpPp", ".ooo.", ".ooo.", "..o.."], {"p": "plant", "P": "plant3", "o": "pot"})
bg.rect(312, 60, 5, 6, "pot")
bg.hline(312, 60, 5, "pot3")

# ================= bed (left) =================
bg.rect(0, 96, 8, 62, "woodd")
bg.rect(0, 96, 8, 2, "woodhl")
bg.vline(7, 98, 60, "wood")
bg.rect(8, 121, 82, 5, "sheet")
bg.hline(8, 125, 82, "sheetd")
bg.rect(8, 126, 82, 12, "blanket")
bg.hline(8, 126, 82, "blanketl")
for x in range(20, 86, 9):  # folds
    bg.vline(x, 128, 9, "blanketd")
    bg.vline(x + 1, 128, 5, "blanketl")
bg.hline(8, 137, 82, "blanketdd")
bg.rect(86, 122, 6, 26, "blanketd")  # draped over the foot
bg.vline(86, 122, 26, "blanket")
bg.rect(8, 138, 80, 10, "wood")
bg.hline(8, 138, 80, "woodhl")
bg.hline(8, 147, 80, "woodd")
bg.rect(10, 148, 4, 12, "woodd")
bg.rect(82, 148, 4, 12, "woodd")
bg.sprite(10, 110, [
    "...pppppppppppppppppp...",
    ".pplllllllllllllllllpp..",
    "pplllllllllllllllllllpp.",
    "pplllllllllllllllllllppd",
    "pppppppppppppppppppppppd",
    ".ppppppppppppppppppppppd",
    "..dddddddddddddddddddd..",
], {"p": "pillow", "l": "pillowl", "d": "pillowd"})

# ================= floor plant between bed and window wall: leafy, on stems =================
LEAVES = [(97, 126, 4), (109, 123, 4), (102, 120, 4), (113, 131, 3), (93, 134, 3), (104, 129, 4)]
for (lx, ly, r) in LEAVES:  # stems first, so leaves sit over them
    for i in range(0, 143 - ly):
        bg.set(round(103 + (lx - 103) * i / max(1, 143 - ly)), 142 - i, "plant2")
for (lx, ly, r) in LEAVES:
    bg.disc(lx, ly, r, "plant2")
    bg.disc(lx + 1, ly - 1, r - 1, "plant")
    bg.set(lx + 1, ly - 2, "plant3"); bg.set(lx + 2, ly - 1, "plant3")
    bg.vline(lx, ly - r + 1, r * 2 - 1, "plant2")  # leaf vein
bg.rect(96, 142, 14, 15, "pot")
bg.hline(96, 142, 14, "pot3")
bg.hline(96, 143, 14, "pot2")
bg.vline(96, 144, 13, "pot2")
bg.vline(97, 144, 13, "pot2")
bg.vline(108, 144, 13, "pot3")   # lit side faces the window

# ================= rug =================
for i, y in enumerate(range(168, 190)):
    inset = (21 - i) // 3
    bg.hline(150 + inset, y, 116 - inset * 2, "rug")
    bg.set(150 + inset, y, "rugb")
    bg.set(150 + 115 - inset, y, "rugb")
bg.hline(157, 168, 102, "rugb")
bg.hline(150, 189, 116, "rugb")
for y in (172, 177, 182, 186):
    for x in range(164, 252, 6):
        bg.rect(x, y, 3, 1, "rugd")

# ================= desk =================
bg.rect(226, 120, 93, 4, "wood")
bg.hline(226, 120, 93, "woodhl")
bg.hline(226, 123, 93, "woodd")
bg.rect(228, 124, 4, 40, "wood")
bg.vline(228, 124, 40, "woodl")
bg.rect(288, 124, 30, 38, "wood")
bg.vline(288, 124, 38, "woodl")
bg.hline(288, 142, 30, "woodd")
bg.rect(299, 132, 8, 1, "woodhl")
bg.rect(299, 151, 8, 1, "woodhl")
bg.hline(226, 164, 6, "woodd")
bg.hline(288, 162, 30, "woodd")

# monitor (16:10, on a stand)
bg.rect(246, 80, 46, 28, "bezel")
bg.hline(246, 80, 46, "bezel2")
bg.rect(248, 82, 42, 24, "screen")
bg.rect(266, 108, 6, 8, "stand")
bg.vline(266, 108, 8, "bezel2")
bg.rect(260, 116, 18, 3, "stand")
bg.hline(260, 116, 18, "bezel2")
# screen chrome: tab bar and gutter (static)
bg.rect(248, 82, 42, 2, "screen2")
bg.rect(249, 82, 6, 1, "#ffb347"); bg.rect(256, 82, 5, 1, "#6c7bb8"); bg.rect(262, 82, 5, 1, "#6c7bb8")
bg.rect(248, 84, 2, 22, "screen2")
bg.rect(275, 84, 1, 22, "#2a3a7a")

# tower on the desk
bg.rect(302, 92, 15, 28, "tower")
bg.rect(303, 93, 13, 26, "tower2")
bg.vline(302, 92, 28, "towerhl")
bg.vline(305, 96, 18, "led")
bg.disc(311, 104, 3, "tower")
bg.set(311, 104, "towerhl")
bg.rect(308, 114, 6, 1, "towerhl")

# keyboard (right of the desk cat, who sits on its left end)
bg.rect(259, 117, 31, 3, "key")
bg.hline(259, 117, 31, "key2")
for x in range(260, 289, 2):
    bg.set(x, 118, "keyhl")

# mug on the desk (bottom row sits on the desk top at y=120)
bg.sprite(293, 111, [
    "mmmmm..",
    "mcccm..",
    "mmmmmMm",
    "mmmmm.M",
    "mmmmmMm",
    "mmmmm..",
    "Mmmmm..",
    ".MMMM..",
], {"m": "mug", "M": "mug2", "c": "coffee"})


# ================= LIGHT v4: hard-edged pixel light, no soft gradients =================
WALLS = {C["wall"]: 0, C["wall2"]: 1, C["wallsh"]: 2, C["walllt"]: 0}
WASH = [["#3d2b63", "#3a2960", "#33265a"], ["#33255e", "#30235a", "#2b2052"]]  # [near, far][wall tone]
for y in range(70, 99):  # the LED strip washes the wall below the shelf; bands step out as they fall
    half = 40 + (y - 70) // 3
    band = 0 if y < 80 else 1
    for x in range(279 - half, 279 + half + 1):
        tone = WALLS.get(bg.px.get((x, y)))
        if tone is not None:
            bg.px[(x, y)] = WASH[band][tone]

FLOORS = {C["floor"]: "#221437", C["floor2"]: "#1f1232", C["floorlt"]: "#2a1a40"}


def floor_shadow(pixels):
    for (x, y) in pixels:
        col = bg.px.get((x, y))
        if col in FLOORS:
            bg.px[(x, y)] = FLOORS[col]


# contact shadows under the bed and the desk (light from above), and the plant's shadow
# thrown down-left, away from the window
floor_shadow([(x, y) for y in range(157, 161) for x in range(6, 92)])
floor_shadow([(x, y) for y in range(157, 165) for x in range(224, 320) if y < 163 or 226 <= x <= 233])
floor_shadow([(x, y) for (y, x0, x1) in ((157, 86, 98), (158, 83, 97), (159, 81, 95), (160, 80, 92), (161, 81, 88))
              for x in range(x0, x1)])

# the screen lights the wall round the monitor in two hard steps (flickers while the cat types)
screen_glow = Canvas()
SCREEN_NEAR = "#2f2a72"
SCREEN_FAR = "#2c2463"
for y in range(70, 118):
    for x in range(236, 302):
        dx = max(246 - x, x - 291, 0)
        dy = max(80 - y, y - 107, 0)
        if dx == 0 and dy == 0:
            continue
        d2 = dx * dx + dy * dy          # rounded, stepped falloff
        base = bg.px.get((x, y))
        if base in WALLS or base in [c for row in WASH for c in row]:
            screen_glow.set(x, y, SCREEN_NEAR if d2 <= 9 else SCREEN_FAR if d2 <= 49 else None)

# ================= hanging plant: three cords, round pot, bushy top =================
for (x1, x2) in ((30, 24), (30, 30), (30, 36)):
    for i in range(19):
        bg.set(round(x1 + (x2 - x1) * i / 18), 16 + i, "lampc")
bg.sprite(22, 30, [
    "....pP..Lp..Pp....",
    "..pPLPpPPpLPpPLp..",
    ".pPPpLPPpPPpPPLPp.",
    "pPLPPpPPLPPpPLPPpP",
    ".pPPpPPpPLPPpPPpP.",
], {"p": "plant", "P": "plant2", "L": "plant3"})
bg.sprite(23, 35, [
    "oOOOOOOOOOOOOOo",
    "ooooooooooooooo",
    "ooooooooooooooq",
    ".ooooooooooooq.",
    "..oooooooooqq..",
    "....qqqqqqq....",
], {"o": "pot", "O": "pot3", "q": "pot2"})

# ================= animated layers =================
LEAF = ["plant", "plant2", "plant3"]
VINES = [(23, 14), (27, 9), (34, 12), (38, 17)]  # (x, length) hanging from the pot rim


def vines(sway):
    c = Canvas()
    for vi, (vx, length) in enumerate(VINES):
        for j in range(length):
            x = vx + (sway * (j // 5) if vi % 2 == 0 else sway * (j // 6))
            y = 40 + j
            c.set(x, y, LEAF[(j + vi) % 2])
            if j % 3 == 1:  # a leaf on alternating sides
                c.set(x + (1 if (j // 3 + vi) % 2 else -1), y, LEAF[2] if j % 2 else LEAF[0])
    return c


leaf_a = vines(0)
leaf_b = vines(1)
front = Canvas()  # things on the sill sit in front of the rain on the glass
# small plant on the sill (static)
front.sprite(106, 98, [
    "...p..p...",
    "..pPp.Pp..",
    ".pPLpPLPp.",
    "pPpPPpPpPp",
    ".pPpLPpPp.",
    "..ooooooo.",
    "..oOOOOOo.",
    "..ooooooo.",
    "...ooooo..",
    "...ooooo..",
    "...ooooo..",
    "...ooooo..",
    "....ooo...",
], {"p": "plant", "P": "plant2", "L": "plant3", "o": "pot", "O": "pot3"})

# ---- cat on the sill, front view; tail frames share the body joint so it never breaks
CAT = {"O": "catO", "D": "catD", "L": "catL", "W": "catW", "E": "catE", "G": "catG", "N": "catN", "P": "catP"}
CX, CY = 168, 91
ORANGE = [
    ".O............O.",
    ".OO..........OO.",
    ".OPO........OPO.",
    ".OPOO......OOPO.",
    ".OOLLOOOOOOOOOO.",
    "OOLLOOOOOOOOOOOO",
    "OOGEOOOOOOOOGEOO",
    "OOEEOOOOOOOOEEOO",
    "OOOOOOWWWWOOOOOO",
    "DOOOOWWNNWWOOOOD",
    ".DOOOWWWWWWOOOD.",
    "..DDOOWWWWOODD..",
    "...OOOOOOOOOO...",
    "..OOLDOOOODOOO..",
    "..OLWWWWWWWWOO..",
    ".OODWWWWWWWWDOO.",
    ".OOOWWWWWWWWOOO.",
    ".OODOWWWWWWODOO.",
    ".OOOOOOOOOOOOOO.",
    "..WWW......WWW..",
]
TAIL_BASE = ["....OO.", "...OO..", "..OO...", ".OOO...", "OOO...."]
TAIL_TOPS = [
    ["...DO..", "...OO..", "...OOO.", "....OO."],
    ["....DO.", "....OO.", "....OO.", "....OO."],
    ["......D", ".....OO", ".....O.", "....OO."],
]


def orange_cat(ox, oy):
    body = sprite_canvas(ox, oy, ORANGE, CAT)
    blk = sprite_canvas(ox, oy, ["", "", "", "", "", "", "..OO........OO..", "..DD........DD.."], CAT)
    tails = [sprite_canvas(ox + 13, oy + 10, top + TAIL_BASE, CAT) for top in TAIL_TOPS]
    return body, blk, tails


def orange_group(cls, cat):
    body, blk, tails = cat
    return (f'<g class="{cls}">{body.paths()}'
            + "".join(f'<g class="t{i}">{t.paths()}</g>' for i, t in enumerate(tails))
            + f'<g class="blink">{blk.paths()}</g></g>')


sill_cat = orange_cat(CX, CY)
helper_cat = orange_cat(273, 100)   # jumps onto the desk while helper agents run

# ---- the desk cat: seen from behind at a slight angle, watching the screen.
# Every frame is one whole cat (body + head + ears + legs + tail) shaded and outlined as a single
# silhouette, so legs join the body with no line between them.
CAT2_X, CAT2_Y = 234, 94          # local (0,0); local row 25 is y=119, on the desk top
TONE = {"g": "gcat", "l": "gcatl", "d": "gcatd", "s": "gcatd", "w": "gcatw", "o": "gcato", "p": "gcatp", "x": "gcato"}


def ellipse(m, cx, cy, rx, ry, part):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                m[(x, y)] = part


def ear(m, apex, base_l, base_r, base_y):
    ax, ay = apex
    for y in range(ay, base_y + 1):
        t = (y - ay) / max(1, base_y - ay)
        x0 = round(ax + (base_l - ax) * t)
        x1 = round(ax + (base_r - ax) * t)
        for x in range(x0, x1 + 1):
            m[(x, y)] = "head"


def limb(m, pts, r, part):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            cx = x0 + (x1 - x0) * i / n
            cy = y0 + (y1 - y0) * i / n
            for y in range(round(cy - r), round(cy + r) + 1):
                for x in range(round(cx - r), round(cx + r) + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                        m[(x, y)] = part


TAIL_TIPS = {
    "up":    [(5, 24), (3, 24), (1, 23), (0, 21), (0, 19), (1, 18)],
    "curl":  [(5, 24), (3, 24), (1, 23), (0, 21), (1, 19), (2, 19)],
    "flat":  [(5, 24), (3, 24), (1, 24), (-1, 24), (-2, 23)],
    "sleep": [(4, 22), (6, 24), (11, 24), (16, 24), (19, 23)],
}


def cat_frame(near=None, far=None, tail="up", ear_flick=False, idle_paw=False, pose="sit", breath=0):
    """near/far: ((shoulder), (elbow), (paw)) for the forelegs reaching to the keys, or None."""
    m = {}
    if pose == "sleep":                          # curled up, head down on the paws
        ellipse(m, 14, 21.5, 11, 4 + breath * 0.6, "body")
        ellipse(m, 23, 20.5, 4.5, 3.5, "head")
        ear(m, (21, 15), 20, 23, 18)
        ear(m, (26, 16), 24, 27, 18)
        limb(m, TAIL_TIPS["sleep"], 1, "tail")
        tail = "sleep"
    else:
        _sit(m, near, far, tail, ear_flick, idle_paw)
    return _finish(m, near, far, tail, idle_paw, pose)


def _sit(m, near, far, tail, ear_flick, idle_paw):
    ellipse(m, 14, 20, 10.5, 6, "body")         # haunches
    ellipse(m, 14.5, 14.5, 7, 6.5, "body")      # back
    ellipse(m, 15.5, 7, 7.5, 5.5, "head")       # head, turned a little toward the screen
    ear(m, (9, -2), 8, 13, 4)                    # left ear
    ear(m, (21, -2) if not ear_flick else (23, -1), 17, 22, 4)  # right ear (flicks outward)
    limb(m, TAIL_TIPS[tail], 1, "tail")
    if far:
        limb(m, far, 1.2, "far")
    if near:
        limb(m, near, 1.5, "near")
    if idle_paw:
        ellipse(m, 21, 24, 2.2, 1.4, "paw")


def _finish(m, near, far, tail, idle_paw, pose):
    for (x, y) in list(m):
        if y > 25:
            del m[(x, y)]                        # sits flat on the desk
    # shade: light from the lamp on the left, the screen's blue on the right edge
    rows = {}
    for (x, y), part in m.items():
        rows.setdefault((y, part in ("body", "head")), []).append(x)
    c = Canvas()
    for (x, y), part in m.items():
        tone = "g"
        if part in ("body", "head"):
            xs = rows[(y, True)]
            t = (x - min(xs)) / max(1, max(xs) - min(xs))
            tone = "l" if t < 0.2 else ("d" if t > 0.84 else "g")
            if part == "body" and y in (13, 16, 19) and 0.35 < t < 0.7:
                tone = "s"                        # tabby stripes across the back
        elif part == "far":
            tone = "d"
        elif part == "tail":
            tone = "d" if pose == "sleep" else "g"
        elif part == "near":
            tone = "g"
        c.set(CAT2_X + x, CAT2_Y + y, TONE[tone])
    # paws: the last few pixels of each foreleg are white
    for leg in (near, far):
        if leg:  # a round white paw at the end of the leg, part of the silhouette (no seam)
            px_, py_ = leg[-1]
            for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (1, 1), (-1, 1), (2, 0), (2, 1)):
                q = (px_ + dx, py_ + dy)
                if q[1] <= 25:
                    m[q] = m.get(q, "paw")
                    c.set(CAT2_X + q[0], CAT2_Y + q[1], "gcatw")
    if idle_paw:
        for (x, y), part in m.items():
            if part == "paw":
                c.set(CAT2_X + x, CAT2_Y + y, "gcatw")
    tx, ty = TAIL_TIPS[tail][-1]
    c.set(CAT2_X + tx, CAT2_Y + ty, "gcatl")      # light tail tip
    # one outline round the whole silhouette
    ring = {}
    for (x, y) in m:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in m and q[1] <= 25:
                ring[(CAT2_X + q[0], CAT2_Y + q[1])] = C["gcato"]
    for q, col in ring.items():
        c.px.setdefault(q, col)
    return c


# typing: both forelegs reach from the right shoulder to the keys; paws alternate
NEAR_DOWN = ((20, 15), (24, 19), (26, 22))
NEAR_UP = ((20, 15), (24, 18), (26, 20))
FAR_DOWN = ((19, 14), (21, 18), (23, 22))
FAR_UP = ((19, 14), (21, 17), (23, 20))
cat_wa = cat_frame(near=NEAR_DOWN, far=FAR_UP, tail="up")
cat_wb = cat_frame(near=NEAR_UP, far=FAR_DOWN, tail="curl")
cat_i0 = cat_frame(tail="up", idle_paw=True)
cat_i1 = cat_frame(tail="curl", idle_paw=True)
cat_i2 = cat_frame(tail="flat", idle_paw=True, ear_flick=True)
cat_s0 = cat_frame(pose="sleep", breath=0)
cat_s1 = cat_frame(pose="sleep", breath=1)

# ---- monitor code: editor (left pane) + log (right pane), drawn three times so the scroll loops
CODE = ["#8fb0ff", "#ffb347", "#c39bff", "#7fe0c0", "#6c7bb8", "#ff8fb1"]
tape = Canvas(W, 400)
rows_code, indent = [], 0
for i in range(16):
    indent = max(0, min(6, indent + random.choice([-2, 0, 0, 2])))
    segs, x = [], 252 + indent
    for _ in range(random.randint(1, 4)):
        ln = random.randint(2, 7)
        if x + ln > 273:
            break
        segs.append((x, ln, random.choice(CODE)))
        x += ln + 1
    rows_code.append(segs)
log_rows = [(random.randint(3, 12), random.choice(["#7fe0c0", "#8fb0ff", "#6c7bb8", "#ffb347"])) for _ in range(16)]
tape2 = Canvas(W, 400)
for rep in range(3):
    for i, segs in enumerate(rows_code):
        for (x, ln, col) in segs:
            tape.rect(x, 85 + rep * 32 + i * 2, ln, 1, col)
    for i, (ln, col) in enumerate(log_rows):
        tape2.rect(277, 85 + rep * 32 + i * 2, min(ln, 12), 1, col)

# ---- rain on the glass, drawn twice so the fall loops
rain = Canvas(W, 300)
drops = [(random.randint(GX0, GX1), random.randint(0, 64)) for _ in range(70)]
for rep in (0, 1):
    for (x, y) in drops:
        if not 151 <= x <= 153:
            rain.rect(x, GY0 + rep * 65 + y, 1, 3, "rain")

# ---- city windows that go dark now and then (four rhythms)
random.shuffle(lit)
blinkers = [Canvas() for _ in range(4)]
for i, (x, y) in enumerate(lit[:24]):
    blinkers[i % 4].rect(x, y, 2, 1, "bnear")

neon = Canvas()
if neon_at:
    nx, ny = neon_at
    neon.rect(nx - 1, ny - 1, 8, 4, "neonhalo")
    neon.rect(nx, ny, 6, 2, "neon")
    neon.set(nx, ny + 2, "neon")

steam = Canvas()
steam.set(295, 107, "steam"); steam.set(296, 105, "steam"); steam.set(295, 103, "steam")


# ================= STATES v3: what Claude is doing, shown in the room =================
def pix(rows, ox, oy, key):
    return sprite_canvas(ox, oy, rows, key)


INK = "#3a3560"
BUB = {"o": INK, "w": "#f2efff", "q": INK, "r": "#ff5c7a", "y": "#ffb347"}
bubble_q = pix([".ooooooo.", "owwwwwwwo", "owwqqqwwo", "owwwwwqwo", "owwwwqwwo", "owwwqwwwo", "owwwwwwwo",
                "owwwqwwwo", ".ooooooo.", "...oo....", "..o......"], 249, 74, BUB)
bubble_bang = pix([".ooooooo.", "owwwwwwwo", "owwwrwwwo", "owwwrwwwo", "owwwrwwwo", "owwwwwwwo", "owwwrwwwo",
                   "owwwwwwwo", ".ooooooo.", "...oo....", "..o......"], 249, 74, BUB)
bubble_dots = pix([".ooooooooo.", "owwwwwwwwwo", "owwwwwwwwwo", "owqwwqwwqwo", "owwwwwwwwwo", ".ooooooooo.",
                   "...oo......", "..o........"], 248, 77, BUB)
heart = pix([".hh.hh.", "hHhhhhh", "hhhhhhh", ".hhhhh.", "..hhh..", "...h..."], 249, 80,
            {"h": "#ff6f91", "H": "#ffc2d1"})
sparks = []
for (sx, sy) in ((240, 96), (262, 92), (238, 108), (266, 104)):
    sparks.append(pix([".y.", "yYy", ".y."], sx, sy, {"y": "#ffcf6e", "Y": "#fff4d1"}))
zees = [pix(["zzz", ".z.", "zzz"], 260, 104, {"z": "#d9d2ff"}) for _ in range(3)]

# screens (inside the monitor's clip): terminal, document, editor, browser, compacting, waiting, error, done, sleep
scr_term = Canvas(W, 400)
scr_term.rect(248, 84, 42, 22, "#0b0d14")
for rep in range(2):
    for i in range(11):
        y = 85 + rep * 22 + i * 2
        scr_term.rect(251, y, 2, 1, "#7dff9a")
        scr_term.rect(254, y, random.randint(4, 26), 1, random.choice(["#7dff9a", "#3fbf62", "#a8ffbf"]))
scr_read = Canvas(W, 400)
scr_read.rect(254, 84, 30, 22, "#e9e4f7")
for rep in range(2):
    for i in range(11):
        y = 86 + rep * 22 + i * 2
        scr_read.rect(257, y, random.randint(10, 24), 1, "#a49dd0" if i % 4 else "#6f58d8")
scr_edit = Canvas()
for (y, ln) in ((90, 16), (94, 12), (98, 18)):
    scr_edit.rect(250, y - 1, 24, 3, "#1f5a3a")
    scr_edit.rect(252, y, ln, 1, "#7dff9a")
    scr_edit.set(250, y, "#a8ffbf")
scr_web = Canvas()
scr_web.rect(248, 84, 42, 22, "#141a3a")
scr_web.rect(250, 85, 38, 3, "#c9d3ff")
scr_web.rect(252, 86, 16, 1, "#6c7bb8")
for (bx, by) in ((252, 91), (270, 91), (252, 99), (270, 99)):
    scr_web.rect(bx, by, 14, 5, "#24305e")
    scr_web.rect(bx + 1, by + 1, 8, 1, "#8fb0ff")
globes = []
for f in range(3):
    g = Canvas()
    g.disc(269, 95, 4, "#2f6fd6")
    g.vline(266 + f * 2, 92, 7, "#7fe0c0")
    g.hline(265, 95, 9, "#7fe0c0")
    globes.append(g)
scr_compact = Canvas()
scr_compact.rect(248, 84, 42, 22, "#141a3a")
scr_compact.rect(255, 92, 28, 5, "#3a3560")
scr_compact.rect(256, 93, 26, 3, "#0f1738")
scr_compact.rect(258, 99, 18, 1, "#6c7bb8")
compact_fill = Canvas()
compact_fill.rect(256, 93, 26, 3, "#ffb347")
scr_wait = Canvas()
scr_wait.rect(258, 88, 24, 13, "#c9c0ee")
scr_wait.rect(258, 88, 24, 2, "#6f58d8")
scr_wait.sprite(268, 91, ["qqq", "..q", ".q.", "...", ".q."], {"q": INK})
scr_wait.rect(261, 98, 7, 2, "#7fe0c0")
scr_wait.rect(272, 98, 7, 2, "#ff8fb1")
scr_err = Canvas()
scr_err.rect(248, 84, 42, 22, "#5a0f24")
scr_err.sprite(265, 89, ["r...r", ".r.r.", "..r..", ".r.r.", "r...r"], {"r": "#ff5c7a"})
scr_done = Canvas()
scr_done.rect(248, 84, 42, 22, "#141a3a")
scr_done.disc(269, 95, 7, "#1f5a3a")
scr_done.sprite(264, 92, ["........g", ".......gg", "g.....gg.", "gg...gg..", ".gg.gg...", "..ggg....", "...g....."],
                {"g": "#7dff9a"})
scr_sleep = Canvas()
scr_sleep.rect(248, 84, 42, 22, "#06060c")
star_saver = pix([".s.", "sSs", ".s."], 252, 87, {"s": "#6c7bb8", "S": "#c8c0ff"})

# progress pips on the monitor's tab bar: one per finished step (up to five)
pips = [Canvas() for _ in range(5)]
for i, c in enumerate(pips):
    c.rect(272 + i * 3, 82, 2, 1, "#ffcf6e")
saved_dot = Canvas()
saved_dot.rect(287, 82, 2, 1, "#7dff9a")

# tired: the mug is empty
mug_empty = Canvas()
mug_empty.rect(294, 112, 3, 1, "mug")

defs = f"""<defs>
<linearGradient id="todDawn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb3c7"/><stop offset="1" stop-color="#8fa8ff"/></linearGradient>
<linearGradient id="todDay" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fbaff"/><stop offset="1" stop-color="#d4defc"/></linearGradient>
<linearGradient id="todDusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff9a6b"/><stop offset="1" stop-color="#7a4ac8"/></linearGradient>
<clipPath id="glass"><rect x="{GX0}" y="{GY0}" width="{GX1 - GX0 + 1}" height="{GY1 - GY0 - 1}"/></clipPath>
<clipPath id="scr"><rect x="250" y="84" width="40" height="22"/></clipPath>
</defs>"""

css = """
.px{fill:none;stroke-width:1;shape-rendering:crispEdges}
.rain{opacity:.28;animation:fall 1.5s linear infinite}
@keyframes fall{from{transform:translateY(-65px)}to{transform:translateY(0)}}
.b0{animation:off 9s steps(1) infinite}.b1{animation:off 13s steps(1) -4s infinite}
.b2{animation:off 17s steps(1) -9s infinite}.b3{animation:off 11s steps(1) -2s infinite}
@keyframes off{0%{opacity:0}80%{opacity:1}}
.neon{animation:neon 12s steps(1) infinite}
@keyframes neon{0%{opacity:1}91%{opacity:.3}92%{opacity:1}94%{opacity:.3}95%{opacity:1}}
.blink{opacity:0;animation:blink 6.5s steps(1) infinite}
@keyframes blink{0%{opacity:0}95%{opacity:1}97.5%{opacity:0}}
.t0{animation:t0 7s steps(1) infinite}.t1{opacity:0;animation:t1 7s steps(1) infinite}.t2{opacity:0;animation:t2 7s steps(1) infinite}
@keyframes t0{0%{opacity:1}70%{opacity:0}88%{opacity:1}}
@keyframes t1{0%{opacity:0}70%{opacity:1}76%{opacity:0}82%{opacity:1}88%{opacity:0}}
@keyframes t2{0%{opacity:0}76%{opacity:1}82%{opacity:0}}
.la{animation:la 6s steps(1) infinite}.lb{opacity:0;animation:lb 6s steps(1) infinite}
@keyframes la{0%{opacity:1}50%{opacity:0}}
@keyframes lb{0%{opacity:0}50%{opacity:1}}
.steam path{animation:rise 3.6s linear infinite}
@keyframes rise{0%{transform:translateY(2px);opacity:0}30%{opacity:.8}100%{transform:translateY(-6px);opacity:0}}
.pend{animation:hum 5s ease-in-out infinite alternate}
@keyframes hum{from{opacity:.85}to{opacity:1}}
.glowScr{opacity:.5}
.work .glowScr{opacity:1;animation:flick .34s steps(1) infinite}
@keyframes flick{0%{opacity:1}50%{opacity:.82}}
.idle .kw,.idle .inbar,.idle .typer{display:none}
.work .ki,.work .cur{display:none}
.idle .tape{opacity:.32}
.work .tape{animation:scroll 1.3s steps(16) infinite}
.work .tape2{animation-duration:.8s}
@keyframes scroll{from{transform:translateY(0)}to{transform:translateY(-32px)}}
.ka{animation:fa .16s steps(1) infinite}.kb{opacity:0;animation:fb .16s steps(1) infinite}
@keyframes fa{0%{opacity:1}50%{opacity:0}}
@keyframes fb{0%{opacity:0}50%{opacity:1}}
.typer{transform-box:fill-box;transform-origin:0 50%;animation:type .7s steps(14) infinite}
@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.k0{animation:i0 8s steps(1) infinite}.k1{opacity:0;animation:i1 8s steps(1) infinite}.k2{opacity:0;animation:i2 8s steps(1) infinite}
@keyframes i0{0%{opacity:1}55%{opacity:0}62%{opacity:1}84%{opacity:0}90%{opacity:1}}
@keyframes i1{0%{opacity:0}55%{opacity:1}62%{opacity:0}}
@keyframes i2{0%{opacity:0}84%{opacity:1}90%{opacity:0}}
.cur{animation:cur 1.1s steps(1) infinite}
@keyframes cur{0%{opacity:1}50%{opacity:0}}
.st,.pip,.helper,.ks,.tod{display:none}
.agents .helper{display:inline}.agents .sillcat{display:none}
.helper .t0{animation-duration:2.4s}.helper .t1{animation-duration:2.4s}.helper .t2{animation-duration:2.4s}
.t-term .s-term,.t-read .s-read,.t-edit .s-edit,.t-web .s-web{display:inline}
.t-edit .s-saved{display:inline;animation:pulse .5s steps(1) 4}
.s-term .tp,.s-read .tp{animation:scroll2 1.2s steps(11) infinite}
.s-read .tp{animation-duration:4s}
@keyframes scroll2{to{transform:translateY(-22px)}}
.s-edit path{animation:ins .9s steps(1) infinite}
@keyframes ins{0%{opacity:0}35%{opacity:1}}
.g0{animation:g0 .9s steps(1) infinite}.g1{opacity:0;animation:g1 .9s steps(1) infinite}.g2{opacity:0;animation:g2 .9s steps(1) infinite}
@keyframes g0{0%{opacity:1}33%{opacity:0}}@keyframes g1{0%{opacity:0}33%{opacity:1}66%{opacity:0}}@keyframes g2{0%{opacity:0}66%{opacity:1}}
.f-compact .s-compact{display:inline}
.cfill{transform-box:fill-box;transform-origin:0 50%;animation:fill 2.4s steps(13) infinite}
@keyframes fill{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.m-wait .s-wait,.m-wait .b-q{display:inline}
.f-error .s-err,.f-error .b-bang,.f-stopped .b-bang{display:inline}
.s-err{animation:pulse .4s steps(1) 4}
@keyframes pulse{0%{opacity:1}50%{opacity:.35}}
.f-error .deskcat{animation:shake .12s steps(1) 6}
@keyframes shake{0%{transform:translateX(-1px)}50%{transform:translateX(1px)}}
.f-done .s-done,.f-done .heart,.f-done .spark{display:inline}
.s-done{transform-box:fill-box;transform-origin:50% 50%;animation:pop .6s ease-out 1}
.heart{animation:float 2.6s ease-out 1 forwards}
@keyframes float{0%{transform:translateY(4px);opacity:0}15%{opacity:1}100%{transform:translateY(-10px);opacity:0}}
.spark{animation:burst 1.1s ease-out 1 forwards}
.sp0{--dx:-6px;--dy:-5px}.sp1{--dx:6px;--dy:-6px}.sp2{--dx:-7px;--dy:3px}.sp3{--dx:7px;--dy:2px}
@keyframes burst{0%{transform:translate(0,0);opacity:1}100%{transform:translate(var(--dx),var(--dy));opacity:0}}
.f-done .pips path{stroke:#7dff9a}
.pop,.pip{transform-box:fill-box;transform-origin:50% 50%}
@keyframes pop{0%{transform:scale(2.6);opacity:.2}60%{transform:scale(.9);opacity:1}100%{transform:scale(1)}}
.m-typing .b-dots,.f-heard .b-dots{display:inline}
.b-dots,.b-q{animation:bob2 1s steps(1) infinite}
@keyframes bob2{0%{transform:translateY(0)}50%{transform:translateY(-1px)}}
.m-typing .k0,.m-typing .k1,.m-typing .k2,.m-wait .k0,.m-wait .k1,.m-wait .k2{animation-duration:1.8s}
.m-typing .sillcat .t0,.m-typing .sillcat .t1,.m-typing .sillcat .t2{animation-duration:2s}
.m-sleep .ki,.m-sleep .kw{display:none}
.m-sleep .ks,.m-sleep .s-sleep,.m-sleep .zz{display:inline}
.ks0{animation:la 6s steps(1) infinite}.ks1{opacity:0;animation:lb 6s steps(1) infinite}
.m-sleep .sillcat .blink{opacity:1;animation:none}
.m-sleep .glowScr{opacity:.12}
.m-sleep .tape,.m-sleep .cur{display:none}
.saver{animation:drift 9s linear infinite}
@keyframes drift{0%{transform:translate(0,0)}25%{transform:translate(28px,6px)}50%{transform:translate(14px,14px)}75%{transform:translate(30px,12px)}100%{transform:translate(0,0)}}
.zz{animation:zz 3.6s linear infinite;opacity:0}
.z1{animation-delay:1.2s}.z2{animation-delay:2.4s}
@keyframes zz{0%{transform:translate(0,0);opacity:0}20%{opacity:.9}100%{transform:translate(6px,-14px);opacity:0}}
.tired .mugempty{display:inline}.tired .steam{display:none}
.tired .ka,.tired .kb{animation-duration:.32s}
.tod-dawn .tdawn,.tod-day .tday,.tod-dusk .tdusk{display:inline}
.tod-day .moonglow{opacity:0}
.p1 .pip1,.p2 .pip1,.p3 .pip1,.p4 .pip1,.p5 .pip1{display:inline}
.p1 .pip1{animation:pop .7s ease-out 1}
.p2 .pip2,.p3 .pip2,.p4 .pip2,.p5 .pip2{display:inline}
.p2 .pip2{animation:pop .7s ease-out 1}
.p3 .pip3,.p4 .pip3,.p5 .pip3{display:inline}
.p3 .pip3{animation:pop .7s ease-out 1}
.p4 .pip4,.p5 .pip4{display:inline}
.p4 .pip4{animation:pop .7s ease-out 1}
.p5 .pip5{display:inline}
.p5 .pip5{animation:pop .7s ease-out 1}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg(state):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="{state}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">',
        f"<style>{css.strip()}</style>", defs,
        '<g class="px" transform="translate(0 .5)">',
        bg.paths(),
        f'<g class="glowScr">{screen_glow.paths()}</g>',
        f'<g clip-path="url(#glass)"><g class="rain">{rain.paths()}</g></g>',
        "".join(f'<g class="b{i}">{b.paths()}</g>' for i, b in enumerate(blinkers)),
        f'<g class="neon">{neon.paths()}</g>',
        '<g transform="translate(0 -.5)">'
        f'<rect class="tod tdawn" x="{GX0}" y="{GY0}" width="{GX1 - GX0 + 1}" height="{GY1 - GY0 - 1}" fill="url(#todDawn)" opacity=".42"/>'
        f'<rect class="tod tday" x="{GX0}" y="{GY0}" width="{GX1 - GX0 + 1}" height="{GY1 - GY0 - 1}" fill="url(#todDay)" opacity=".72"/>'
        f'<rect class="tod tdusk" x="{GX0}" y="{GY0}" width="{GX1 - GX0 + 1}" height="{GY1 - GY0 - 1}" fill="url(#todDusk)" opacity=".5"/></g>',
        front.paths(),
        f'<g class="la">{leaf_a.paths()}</g><g class="lb">{leaf_b.paths()}</g>',
        orange_group("sillcat", sill_cat),
        f'<g clip-path="url(#scr)"><g class="tape">{tape.paths()}</g><g class="tape tape2">{tape2.paths()}</g></g>',
        '<g transform="translate(0 -.5)"><rect class="cur" x="279" y="103" width="2" height="1" fill="#e8e0ff"/>'
        '<rect class="inbar" x="276" y="102" width="14" height="3" fill="#0f1738"/>'
        '<rect class="typer" x="277" y="103" width="11" height="1" fill="#ffd27a"/></g>',
        f'<g clip-path="url(#scr)">'
        f'<g class="st s-term"><g class="tp">{scr_term.paths()}</g></g>'
        f'<g class="st s-read"><g class="tp">{scr_read.paths()}</g></g>'
        f'<g class="st s-edit">{scr_edit.paths()}</g>'
        f'<g class="st s-web">{scr_web.paths()}' + "".join(f'<g class="g{i}">{g.paths()}</g>' for i, g in enumerate(globes)) + '</g>'
        f'<g class="st s-compact">{scr_compact.paths()}<g class="cfill">{compact_fill.paths()}</g></g>'
        f'<g class="st s-wait">{scr_wait.paths()}</g>'
        f'<g class="st s-err">{scr_err.paths()}</g>'
        f'<g class="st s-done">{scr_done.paths()}</g>'
        f'<g class="st s-sleep">{scr_sleep.paths()}<g class="saver">{star_saver.paths()}</g></g>'
        '</g>',
        '<g class="pips">' + "".join(f'<g class="pip pip{i + 1}">{c.paths()}</g>' for i, c in enumerate(pips)) + '</g>',
        f'<g class="st s-saved">{saved_dot.paths()}</g>',
        '<g class="deskcat">'
        f'<g class="kw ka">{cat_wa.paths()}</g><g class="kw kb">{cat_wb.paths()}</g>'
        f'<g class="ki k0">{cat_i0.paths()}</g><g class="ki k1">{cat_i1.paths()}</g><g class="ki k2">{cat_i2.paths()}</g>'
        f'<g class="ks ks0">{cat_s0.paths()}</g><g class="ks ks1">{cat_s1.paths()}</g>'
        '</g>',
        orange_group("helper", helper_cat),
        f'<g class="st b-q">{bubble_q.paths()}</g><g class="st b-bang">{bubble_bang.paths()}</g><g class="st b-dots">{bubble_dots.paths()}</g>',
        f'<g class="st heart">{heart.paths()}</g>',
        "".join(f'<g class="st spark sp{i}">{c.paths()}</g>' for i, c in enumerate(sparks)),
        "".join(f'<g class="st zz z{i}">{c.paths()}</g>' for i, c in enumerate(zees)),
        f'<g class="st mugempty">{mug_empty.paths()}</g>',
        f'<g class="steam">{steam.paths()}</g>',
        "</g>",

        # light, over the pixels
        "</svg>",
    ]
    return "".join(parts)


import json

OUT.mkdir(exist_ok=True)
s = svg("work")  # the mod rewrites class="work" to the classes of the moment
(OUT / "scene.svg").write_text(s)
print("scene/scene.svg", len(s), "chars (cap 131072)")
if len(s) > 131072:
    raise SystemExit("the scene is over the 131,072-character cap: merge colours or drop detail")
MOD = OUT.parent / "plugin" / "hooks" / "scene.ts"
MOD.write_text("// Generated by tools/gen_scene.py. Don't edit: change the generator and run it again.\n"
               f"export const SCENE = {json.dumps(s)}\n")
print("plugin/hooks/scene.ts written")

# the install guide carries its own copy of the scene, so it works as a single file
from build_install import build
build()
