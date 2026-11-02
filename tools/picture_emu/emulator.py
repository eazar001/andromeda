"""Run the interpreter's own PICTURE routine under Unicorn.

The bytes come straight from AGI.decoded and AGIDATA.OVL at their load addresses, so this
executes the real 1000:637E and 1000:6379 code rather than a model of it.
"""
from pathlib import Path

from unicorn import UC_ARCH_X86, UC_MODE_16, Uc
from unicorn.x86_const import (
    UC_X86_REG_CS,
    UC_X86_REG_DS,
    UC_X86_REG_ES,
    UC_X86_REG_SP,
    UC_X86_REG_SS,
)

CODE_SEG, DATA_SEG, STACK_SEG, BUF_SEG = 0x1000, 0x19F5, 0x1BDC, 0x3000
PIC_OFF, STOP_OFF = 0x4000, 0x0000
DRAW, OVERLAY = 0x637E, 0x6379
WIDTH, HEIGHT = 160, 168
STACK_TOP, STACK_FILL = 0x1000, 0xA5
MZ_HEADER = 0x200
MAX_INSTRUCTIONS = 300_000_000


def linear(seg, off=0):
    return (seg << 4) + off


class PictureEmu:
    """One emulated machine. Each `run` returns the 160x168 buffer after a picture."""

    def __init__(self, game_dir, machine=0, monitor=3):
        game_dir = Path(game_dir)
        self.uc = Uc(UC_ARCH_X86, UC_MODE_16)
        self.uc.mem_map(0, 0x100000)
        self.uc.mem_write(linear(CODE_SEG), (game_dir / "AGI.decoded").read_bytes()[MZ_HEADER:])
        self.uc.mem_write(linear(DATA_SEG), (game_dir / "AGIDATA.OVL").read_bytes())
        self.uc.mem_write(linear(CODE_SEG, STOP_OFF), b"\xf4")
        self._word(0x1365, BUF_SEG)
        self._word(0x1126, machine)
        self._word(0x1128, monitor)

    def _word(self, off, value):
        self.uc.mem_write(linear(DATA_SEG, off), value.to_bytes(2, "little"))

    def run(self, picture, entry=DRAW):
        uc = self.uc
        uc.mem_write(linear(DATA_SEG, PIC_OFF), bytes(picture))
        self._word(0x136D, PIC_OFF)
        uc.mem_write(linear(STACK_SEG), bytes([STACK_FILL]) * STACK_TOP)
        for reg, seg in ((UC_X86_REG_CS, CODE_SEG), (UC_X86_REG_DS, DATA_SEG),
                         (UC_X86_REG_ES, DATA_SEG), (UC_X86_REG_SS, STACK_SEG)):
            uc.reg_write(reg, seg)
        sp = STACK_TOP - 2
        uc.mem_write(linear(STACK_SEG, sp), STOP_OFF.to_bytes(2, "little"))
        uc.reg_write(UC_X86_REG_SP, sp)
        uc.emu_start(linear(CODE_SEG, entry), linear(CODE_SEG, STOP_OFF), count=MAX_INSTRUCTIONS)
        return bytes(uc.mem_read(linear(BUF_SEG), WIDTH * HEIGHT))

    def stack_used(self):
        stack = bytes(self.uc.mem_read(linear(STACK_SEG), STACK_TOP))
        touched = next((i for i, b in enumerate(stack) if b != STACK_FILL), STACK_TOP)
        return STACK_TOP - touched


def load_pens(game_dir):
    """Read the eight circle masks from AGIDATA.OVL, as rows of 16-bit words per size."""
    agidata = (Path(game_dir) / "AGIDATA.OVL").read_bytes()
    pens = []
    for size in range(8):
        off = int.from_bytes(agidata[0x160F + 2 * size:0x1611 + 2 * size], "little")
        rows = 2 * size + 1
        pens.append([int.from_bytes(agidata[off + 2 * r:off + 2 * r + 2], "little") for r in range(rows)])
    return pens


def game_pictures(game_dir):
    """Yield (number, payload) for every present PICDIR entry whose VOL header is valid."""
    game_dir = Path(game_dir)
    directory = (game_dir / "PICDIR").read_bytes()
    vols = {}
    for n in range(len(directory) // 3):
        a, b, c = directory[3 * n:3 * n + 3]
        if a >> 4 == 0xF:
            continue
        vol, off = a >> 4, ((a & 0xF) << 16) | (b << 8) | c
        v = vols.setdefault(vol, (game_dir / f"VOL.{vol}").read_bytes())
        if off + 5 <= len(v) and v[off:off + 2] == b"\x12\x34":
            size = int.from_bytes(v[off + 3:off + 5], "little")
            yield n, v[off + 5:off + 5 + size]
