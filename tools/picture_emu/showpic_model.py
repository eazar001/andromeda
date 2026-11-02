"""A port of AGI_Specifications/Code/showpic.c, with switches for the parts under test.

`render` returns a 160x168 buffer of (priority << 4) | color, or None on a stray opcode.
Lance Ewing's two splatter tables are here too, for checking them against the shift register.
"""
import math
import struct
from collections import deque

from rules_model import splatter_step

W, H = 160, 168


def f32(v):
    return struct.unpack("f", struct.pack("f", v))[0]


SPLATTER_MAP = bytes([
    0x20, 0x94, 0x02, 0x24, 0x90, 0x82, 0xa4, 0xa2, 0x82, 0x09, 0x0a, 0x22, 0x12, 0x10, 0x42, 0x14,
    0x91, 0x4a, 0x91, 0x11, 0x08, 0x12, 0x25, 0x10, 0x22, 0xa8, 0x14, 0x24, 0x00, 0x50, 0x24, 0x04])

SPLATTER_START_SHOWPIC = bytes([
    0x00, 0x18, 0x30, 0xc4, 0xdc, 0x65, 0xeb, 0x48, 0x60, 0xbd, 0x89, 0x05, 0x0a, 0xf4, 0x7d, 0x7d,
    0x85, 0xb0, 0x8e, 0x95, 0x1f, 0x22, 0x0d, 0xdf, 0x2a, 0x78, 0xd5, 0x73, 0x1c, 0xb4, 0x40, 0xa1,
    0xb9, 0x3c, 0xca, 0x58, 0x92, 0x34, 0xcc, 0xce, 0xd7, 0x42, 0x90, 0x0f, 0x8b, 0x7f, 0x32, 0xed,
    0x5c, 0x9d, 0xc8, 0x99, 0xad, 0x4e, 0x56, 0xa6, 0xf7, 0x68, 0xb7, 0x25, 0x82, 0x37, 0x3a, 0x51,
    0x69, 0x26, 0x38, 0x52, 0x9e, 0x9a, 0x4f, 0xa7, 0x43, 0x10, 0x80, 0xee, 0x3d, 0x59, 0x35, 0xcf,
    0x79, 0x74, 0xb5, 0xa2, 0xb1, 0x96, 0x23, 0xe0, 0xbe, 0x05, 0xf5, 0x6e, 0x19, 0xc5, 0x66, 0x49,
    0xf0, 0xd1, 0x54, 0xa9, 0x70, 0x4b, 0xa4, 0xe2, 0xe6, 0xe5, 0xab, 0xe4, 0xd2, 0xaa, 0x4c, 0xe3,
    0x06, 0x6f, 0xc6, 0x4a, 0xa4, 0x75, 0x97, 0xe1])

SPLATTER_START_PROSE = bytes([
    0x00, 0x18, 0x30, 0xc4, 0xdc, 0x65, 0xeb, 0x48, 0x60, 0xbd, 0x89, 0x04, 0x0a, 0xf4, 0x7d, 0x6d,
    0x85, 0xb0, 0x8e, 0x95, 0x1f, 0x22, 0x0d, 0xdf, 0x2a, 0x78, 0xd5, 0x73, 0x1c, 0xb4, 0x40, 0xa1,
    0xb9, 0x3c, 0xca, 0x58, 0x92, 0x34, 0xcc, 0xce, 0xd7, 0x42, 0x90, 0x0f, 0x8b, 0x7f, 0x32, 0xed,
    0x5c, 0x9d, 0xc8, 0x99, 0xad, 0x4e, 0x56, 0xa6, 0xf7, 0x68, 0xb7, 0x25, 0x82, 0x37, 0x3a, 0x51,
    0x69, 0x26, 0x38, 0x52, 0x9e, 0x9a, 0x4f, 0xa7, 0x43, 0x10, 0x80, 0xee, 0x3d, 0x59, 0x35, 0xcf,
    0x79, 0x74, 0xb5, 0xa2, 0xb1, 0x96, 0x23, 0xe0, 0xbe, 0x05, 0xf5, 0x6e, 0x19, 0xc5, 0x66, 0x49,
    0xf0, 0xd1, 0x54, 0xa9, 0x70, 0x4b, 0xa4, 0xe2, 0xe6, 0xe5, 0xab, 0xe4, 0xd2, 0xaa, 0x4c, 0xe3,
    0x06, 0x6f, 0xc6, 0x4a, 0x75, 0xa3, 0x97, 0xe1])

CIRCLES = [
    [0x80], [0xfc], [0x5f, 0xf4], [0x66, 0xff, 0xf6, 0x60], [0x23, 0xbf, 0xff, 0xff, 0xee, 0x20],
    [0x31, 0xe7, 0x9e, 0xff, 0xff, 0xde, 0x79, 0xe3, 0x00],
    [0x38, 0xf9, 0xf3, 0xef, 0xff, 0xff, 0xff, 0xfe, 0xf9, 0xf3, 0xe3, 0x80],
    [0x18, 0x3c, 0x7e, 0x7e, 0x7e, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7e, 0x7e, 0x7e, 0x3c, 0x18]]


class Showpic:
    def __init__(self, data, stale_color=True, pri_only_if_4=False):
        self.d, self.p = data, 0
        self.vis = bytearray([15]) * (W * H)
        self.pri = bytearray([4]) * (W * H)
        self.pic_on = self.pri_on = False
        self.pic_c = self.pri_c = 0
        self.pat, self.pat_num = 0, 0
        self.stale = stale_color
        self.pri_only_if_4 = pri_only_if_4

    def nx(self):
        b = self.d[self.p] if self.p < len(self.d) else 0xFF
        self.p += 1
        return b

    def pset(self, x, y):
        if self.pic_on and 2 * x <= 319 and y < H:
            self.vis[y * W + x] = self.pic_c & 0xFF
        if self.pri_on and 2 * x <= 319 and y < H:
            self.pri[y * W + x] = self.pri_c & 0xFF

    @staticmethod
    def rnd(v, dirn):
        fl = math.floor(v)
        if dirn < 0:
            return fl if v - fl <= 0.501 else math.ceil(v)
        return fl if v - fl < 0.499 else math.ceil(v)

    def drawline(self, x1, y1, x2, y2):
        h, w = y2 - y1, x2 - x1
        add_x = f32(0 if h == 0 else f32(w) / abs(h))
        add_y = f32(0 if w == 0 else f32(h) / abs(w))
        if abs(w) > abs(h):
            y = f32(y1)
            add_x = 0 if w == 0 else (1 if w > 0 else -1)
            x = f32(x1)
            while x != x2:
                self.pset(self.rnd(x, add_x), self.rnd(y, add_y))
                x = f32(x + add_x)
                y = f32(y + add_y)
            self.pset(x2, y2)
        else:
            x = f32(x1)
            add_y = 0 if h == 0 else (1 if h > 0 else -1)
            y = f32(y1)
            while y != y2:
                self.pset(self.rnd(x, add_x), self.rnd(y, add_y))
                x = f32(x + add_x)
                y = f32(y + add_y)
            self.pset(x2, y2)

    def ok(self, x, y):
        if not 0 <= x < W or not 0 <= y < H:
            return False
        if not self.pic_on and not self.pri_on:
            return False
        if self.stale:
            if self.pic_c == 15:
                return False
        else:
            if self.pic_on and self.pic_c == 15:
                return False
            if not self.pic_on and self.pri_c == 4:
                return False
        if not self.pri_on:
            return self.vis[y * W + x] == 15
        if not self.pic_on:
            return self.pri[y * W + x] == 4
        return self.vis[y * W + x] == 15

    def fill(self, x, y):
        q = deque([(x, y)])
        while q:
            x1, y1 = q.popleft()
            if self.ok(x1, y1):
                keep = self.pri[y1 * W + x1]
                self.pset(x1, y1)
                if self.pri_only_if_4 and self.pic_on and self.pri_on and keep != 4:
                    self.pri[y1 * W + x1] = keep
                if self.ok(x1, y1 - 1):
                    q.append((x1, y1 - 1))
                if self.ok(x1 - 1, y1):
                    q.append((x1 - 1, y1))
                if self.ok(x1 + 1, y1):
                    q.append((x1 + 1, y1))
                if self.ok(x1, y1 + 1):
                    q.append((x1, y1 + 1))

    def plot(self, x, y):
        size = self.pat & 7
        bitpos = SPLATTER_START_SHOWPIC[self.pat_num]
        if x < size // 2 + 1:
            x = size // 2 + 1
        elif x > 160 - (size // 2 + 1):
            x = 160 - (size // 2 + 1)
        if y < size:
            y = size
        elif y >= 168 - size:
            y = 167 - size
        cp = 0
        for y1 in range(y - size, y + size + 1):
            for x1 in range(x - math.ceil(size / 2), x + size // 2 + 1):
                go = True
                if not self.pat & 0x10:
                    go = (CIRCLES[size][cp >> 3] >> (7 - (cp & 7))) & 1
                    cp += 1
                if go:
                    if self.pat & 0x20:
                        if (SPLATTER_MAP[bitpos >> 3] >> (7 - (bitpos & 7))) & 1:
                            self.pset(x1, y1)
                        bitpos = (bitpos + 1) & 0xFF
                        if bitpos == 0xFF:
                            bitpos = 0
                    else:
                        self.pset(x1, y1)

    def run(self):
        while True:
            a = self.nx()
            if a == 0xFF:
                break
            if a == 0xF0:
                self.pic_c = self.nx()
                self.pic_on = True
            elif a == 0xF1:
                self.pic_on = False
            elif a == 0xF2:
                self.pri_c = self.nx()
                self.pri_on = True
            elif a == 0xF3:
                self.pri_on = False
            elif a in (0xF4, 0xF5):
                self.corner(a == 0xF4)
            elif a == 0xF6:
                self.absline()
            elif a == 0xF7:
                self.rel()
            elif a == 0xF8:
                while True:
                    x = self.nx()
                    if x >= 0xF0:
                        break
                    y = self.nx()
                    if y >= 0xF0:
                        break
                    self.fill(x, y)
                self.p -= 1
            elif a == 0xF9:
                self.pat = self.nx()
            elif a == 0xFA:
                self.brush()
            else:
                return None
        return bytes((p << 4) & 0xF0 | (v & 0xF) for p, v in zip(self.pri, self.vis))

    def corner(self, vertical):
        x1, y1 = self.nx(), self.nx()
        self.pset(x1, y1)
        while True:
            v = self.nx()
            if v >= 0xF0:
                break
            if vertical:
                self.drawline(x1, y1, x1, v)
                y1 = v
            else:
                self.drawline(x1, y1, v, y1)
                x1 = v
            vertical = not vertical
        self.p -= 1

    def absline(self):
        x1, y1 = self.nx(), self.nx()
        self.pset(x1, y1)
        while True:
            x2 = self.nx()
            if x2 >= 0xF0:
                break
            y2 = self.nx()
            if y2 >= 0xF0:
                break
            self.drawline(x1, y1, x2, y2)
            x1, y1 = x2, y2
        self.p -= 1

    def rel(self):
        x1, y1 = self.nx(), self.nx()
        self.pset(x1, y1)
        while True:
            d = self.nx()
            if d >= 0xF0:
                break
            dx, dy = (d >> 4) & 0xF, d & 0xF
            if dx & 8:
                dx = -(dx & 7)
            if dy & 8:
                dy = -(dy & 7)
            self.drawline(x1, y1, x1 + dx, y1 + dy)
            x1 = (x1 + dx) & 0xFF
            y1 = (y1 + dy) & 0xFF
        self.p -= 1

    def brush(self):
        while True:
            if self.pat & 0x20:
                n = self.nx()
                if n >= 0xF0:
                    break
                self.pat_num = (n >> 1) & 0x7F
            x = self.nx()
            if x >= 0xF0:
                break
            y = self.nx()
            if y >= 0xF0:
                break
            self.plot(x, y)
        self.p -= 1


def render(data, **switches):
    return Showpic(data, **switches).run()


def offset_disagreements(table, compared_bits=225):
    """Return the indices of `table` where the offset doesn't reproduce the shift register."""
    bits = [(SPLATTER_MAP[i >> 3] >> (7 - (i & 7))) & 1 for i in range(256)]
    return [index for index, offset in enumerate(table)
            if _table_bits(bits, offset, compared_bits) != _register_bits(index, compared_bits)]


def _table_bits(bits, offset, count):
    out = []
    for _ in range(count):
        out.append(bits[offset])
        offset = (offset + 1) & 0xFF
        if offset == 0xFF:
            offset = 0
    return out


def _register_bits(pattern, count):
    register, out = (pattern << 1) | 1, []
    for _ in range(count):
        register, drawn = splatter_step(register)
        out.append(1 if drawn else 0)
    return out
