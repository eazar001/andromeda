"""Just enough display hardware to read back what a driver drew.

EGA is modelled at the register level: map mask, graphics controller, latches, write modes 0
and 2. The other adapters' memory is plain RAM in the machine, so they only need decoding.
"""
from dataclasses import dataclass, field

EGA_BASE, EGA_SIZE = 0xA0000, 0x10000


@dataclass
class Ega:
    planes: list = field(default_factory=lambda: [bytearray(EGA_SIZE) for _ in range(4)])
    latch: list = field(default_factory=lambda: [0, 0, 0, 0])
    seq_index: int = 0
    gc_index: int = 0
    map_mask: int = 0x0F
    gc: list = field(default_factory=lambda: [0] * 9 + [0xFF])

    def __post_init__(self):
        self.gc[8] = 0xFF

    def out(self, port, value):
        if port == 0x3C4:
            self.seq_index = value
        elif port == 0x3C5 and self.seq_index == 2:
            self.map_mask = value & 0x0F
        elif port == 0x3CE:
            self.gc_index = value & 0x0F
        elif port == 0x3CF and self.gc_index < 9:
            self.gc[self.gc_index] = value

    def read(self, off):
        self.latch = [p[off] for p in self.planes]

    def _data(self, p, value):
        mode = self.gc[5] & 3
        if mode == 2:
            return 0xFF if value >> p & 1 else 0
        if self.gc[1] >> p & 1:                            # set/reset enabled for this plane
            return 0xFF if self.gc[0] >> p & 1 else 0
        return value

    def write(self, off, value):
        bm, func = self.gc[8], self.gc[3] >> 3 & 3
        for p in range(4):
            if not self.map_mask >> p & 1:
                continue
            d, lat = self._data(p, value), self.latch[p]
            d = (d, d & lat, d | lat, d ^ lat)[func]
            self.planes[p][off] = (d & bm) | (lat & ~bm & 0xFF)

    def clear(self):
        for p in self.planes:
            p[:] = bytes(EGA_SIZE)

    def mode0d(self, page=0):
        """The 320x200 16-color picture, as rows of color indexes."""
        base = page * 0x2000
        rows = []
        for y in range(200):
            row = []
            for xb in range(40):
                o = base + y * 40 + xb
                bits = [self.planes[p][o] for p in range(4)]
                row += [sum((bits[p] >> (7 - i) & 1) << p for p in range(4)) for i in range(8)]
            rows.append(row)
        return rows


def cga_mode4(ram: bytes):
    """CGA 320x200x4 from B800: even lines at 0, odd lines at 0x2000, 2 bits per pixel."""
    return [[ram[(y & 1) * 0x2000 + (y >> 1) * 80 + x // 4] >> (6 - 2 * (x % 4)) & 3 for x in range(320)]
            for y in range(200)]


def vga_mode13(ram: bytes):
    return [list(ram[y * 320:(y + 1) * 320]) for y in range(200)]


def hercules(ram: bytes, page=0):
    """Hercules 720x348 1bpp: four banks of 0x2000, 90 bytes a line."""
    base = page * 0x8000
    return [[ram[base + (y & 3) * 0x2000 + (y >> 2) * 90 + x // 8] >> (7 - x % 8) & 1 for x in range(720)]
            for y in range(348)]


def pcjr_mode9(ram: bytes):
    """PCjr/Tandy 320x200x16: four banks of 0x2000, 160 bytes a line, 4 bits per pixel."""
    return [[ram[(y & 3) * 0x2000 + (y >> 2) * 160 + x // 2] >> (4 * (1 - x % 2)) & 0xF for x in range(320)]
            for y in range(200)]
