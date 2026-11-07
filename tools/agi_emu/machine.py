"""The whole interpreter under Unicorn: memory, interrupt dispatch, ports, timer and probes."""
from dataclasses import dataclass, field
import struct

from unicorn import (UcError, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UC_HOOK_INSN, UC_HOOK_INTR,
                     UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, Uc)
from unicorn.x86_const import (
    UC_X86_INS_IN, UC_X86_INS_OUT,
    UC_X86_REG_AX, UC_X86_REG_BX, UC_X86_REG_CX, UC_X86_REG_DX, UC_X86_REG_SI, UC_X86_REG_DI,
    UC_X86_REG_BP, UC_X86_REG_SP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS,
    UC_X86_REG_IP, UC_X86_REG_EFLAGS,
)

import bios
import dos
from image import load_mz
from video import EGA_BASE, EGA_SIZE, Ega

LOAD_SEG = 0x1000
PSP_SEG = LOAD_SEG - 0x10
DATA_SEG = 0x19F5
ROM_SEG = 0xF000
TICK_INSNS = 20_000
PUT_CHAR = 0x29F6                                     # 2.917's one-character output
IF_FLAG, CF_FLAG, ZF_FLAG = 0x200, 0x001, 0x040
REGS = {"ax": UC_X86_REG_AX, "bx": UC_X86_REG_BX, "cx": UC_X86_REG_CX, "dx": UC_X86_REG_DX,
        "si": UC_X86_REG_SI, "di": UC_X86_REG_DI, "bp": UC_X86_REG_BP, "sp": UC_X86_REG_SP,
        "cs": UC_X86_REG_CS, "ds": UC_X86_REG_DS, "es": UC_X86_REG_ES, "ss": UC_X86_REG_SS,
        "ip": UC_X86_REG_IP, "flags": UC_X86_REG_EFLAGS}
HLE = {0x10: bios.int10, 0x11: bios.int11, 0x12: bios.int12, 0x15: bios.int15,
       0x16: bios.int16, 0x1A: bios.int1a, 0x21: dos.int21}
# ROM stubs: int 8 calls int 1Ch then returns; every other vector is a bare IRET.
ROM_INT8, ROM_IRET = 0x0000, 0x0010
ROM_CODE = {ROM_INT8: b"\xcd\x1c\xcf", ROM_IRET: b"\xcf"}


@dataclass
class Machine:
    files: dict
    switches: str = ""
    keys: list = field(default_factory=list)          # (tick, bios key word), sorted
    tick: int = 0
    exit_code: int | None = None
    stdout: bytearray = field(default_factory=bytearray)
    text: dict = field(default_factory=dict)          # (row, col) -> (char, attr) the interpreter printed
    bios_chars: dict = field(default_factory=dict)    # (row, col) -> (char, attr) as sent to int 10h
    video_log: list = field(default_factory=list)     # (tick, ah, al, bx, cx, dx)
    port_log: list = field(default_factory=list)      # (tick, port, value) for OUTs
    log_ports: bool = False
    waiting: bool = False
    halted: bool = False
    floppies: int = 1
    shift_flags: int = 0
    joy_port: int = 0xFF
    scans: list = field(default_factory=list)         # (tick, scan code) for the keyboard interrupt
    port60: int = 0
    model: int = 0xFF                                 # BIOS model byte at F000:FFFE
    ega_present: bool = True
    jr_page: int = 0x24                               # PCjr video page, 16K units: segment 0x9000
    mem_top: int = 0x9000                             # DOS memory ends here, below the PCjr page
    auto_key: int | None = None                       # answers a blocking key read when none is queued
    unknown: list = field(default_factory=list)       # services not emulated
    last_ip: tuple = (0, 0)                           # CS:IP the last tick interrupted
    crash: tuple | None = None                        # (CS, IP, error) if the CPU faulted

    def __post_init__(self):
        self.uc = Uc(UC_ARCH_X86, UC_MODE_16)
        self.uc.mem_map(0, 0x100000)
        self.dos = dos.DosState(self)
        self.bios = bios.BiosState()
        self.ega = Ega()
        self._load()
        self.uc.hook_add(UC_HOOK_INTR, self._on_int)
        self.uc.hook_add(UC_HOOK_INSN, self._on_in, None, 1, 0, UC_X86_INS_IN)
        self.uc.hook_add(UC_HOOK_INSN, self._on_out, None, 1, 0, UC_X86_INS_OUT)
        self.probe(PUT_CHAR, self._on_put_char)
        end = EGA_BASE + EGA_SIZE - 1
        self.uc.hook_add(UC_HOOK_MEM_READ, self._on_vread, None, EGA_BASE, end)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._on_vwrite, None, EGA_BASE, end)

    # ----- setup
    def _load(self):
        img = load_mz(self.files["AGI.DECODED"], LOAD_SEG)
        self.write(LOAD_SEG, 0, img.data)
        for off, code in ROM_CODE.items():
            self.write(ROM_SEG, off, code)
        self.write(ROM_SEG, 0xFFFE, bytes([self.model]))
        for n in range(256):
            self.set_vector(n, ROM_SEG, ROM_INT8 if n == 8 else ROM_IRET)
        self._psp(img)
        for name, seg in (("cs", img.cs), ("ss", img.ss), ("ds", PSP_SEG), ("es", PSP_SEG)):
            self.reg(name, seg)
        self.reg("ip", img.ip); self.reg("sp", img.sp); self.reg("flags", IF_FLAG | 2)
        self.dos.init_memory(PSP_SEG, LOAD_SEG + (len(img.data) + 15) // 16 + 0x270)

    def _psp(self, img):
        tail = (" " + self.switches if self.switches else "").encode("ascii")
        self.write(PSP_SEG, 0, b"\xcd\x20" + struct.pack("<H", 0xA000))
        self.write(PSP_SEG, 0x80, bytes([len(tail)]) + tail + b"\r")

    # ----- memory and registers
    def write(self, seg, off, data):
        self.uc.mem_write(seg * 16 + off, bytes(data))

    def read(self, seg, off, n):
        return bytes(self.uc.mem_read(seg * 16 + off, n))

    def word(self, seg, off):
        return struct.unpack("<H", self.read(seg, off, 2))[0]

    def reg(self, name, value=None):
        if value is None:
            return self.uc.reg_read(REGS[name])
        self.uc.reg_write(REGS[name], value & 0xFFFF if name != "flags" else value)

    def set_flag(self, mask, on):
        f = self.reg("flags")
        self.reg("flags", f | mask if on else f & ~mask)

    def set_vector(self, n, seg, off):
        self.write(0, 4 * n, struct.pack("<HH", off, seg))

    def vector(self, n):
        off, seg = struct.unpack("<HH", self.read(0, 4 * n, 4))
        return seg, off

    # ----- AGI state
    def ds(self, off, n=1):
        return self.read(DATA_SEG, off, n)

    def var(self, n):
        return self.ds(0x09 + n)[0]

    def flag(self, n):
        return bool(self.ds(0x109 + n // 8)[0] & (0x80 >> (n % 8)))

    def screen(self):
        """The 160x168 screen buffer: visual in the low nibble, priority in the high."""
        return self.read(self.word(DATA_SEG, 0x1365), 0, 160 * 168)

    # ----- interrupts
    def push(self, value):
        sp = (self.reg("sp") - 2) & 0xFFFF
        self.reg("sp", sp)
        self.write(self.reg("ss"), sp, struct.pack("<H", value))

    def enter_vector(self, n):
        """Do what the CPU does for `int n`: push FLAGS, CS, IP and jump through the IVT."""
        flags = self.reg("flags")
        self.push(flags); self.push(self.reg("cs")); self.push(self.reg("ip"))
        self.reg("flags", flags & ~(IF_FLAG | 0x100))
        seg, off = self.vector(n)
        self.reg("cs", seg); self.reg("ip", off)

    def _on_int(self, uc, n, _):
        handler = HLE.get(n)
        if handler and self.vector(n) == (ROM_SEG, ROM_IRET):
            handler(self)
        else:
            self.enter_vector(n)
        if self.waiting or self.exit_code is not None:
            uc.emu_stop()

    def halt(self):
        """End `run` at the current instruction; a probe calls this."""
        self.halted = True
        self.uc.emu_stop()

    def _on_in(self, uc, port, size, _):
        return bios.port_in(self, port)

    def _on_vread(self, uc, access, addr, size, value, _):
        self.ega.read((addr + size - 1 - EGA_BASE) & 0xFFFF)

    def _on_vwrite(self, uc, access, addr, size, value, _):
        for i in range(size):
            self.ega.write((addr + i - EGA_BASE) & 0xFFFF, value >> (8 * i) & 0xFF)

    def _on_out(self, uc, port, size, value, _):
        self.ega.out(port, value & 0xFF)
        if size == 2:
            self.ega.out(port + 1, value >> 8)
        if self.log_ports:
            self.port_log.append((self.tick, port, value))

    def _on_put_char(self, _):
        ch = self.word(self.reg("ss"), self.reg("sp") + 2) & 0xFF
        if ch >= 0x20:
            self.text[self.bios.cursor] = (ch, self.word(DATA_SEG, 0x05CD))

    # ----- keys
    def key_ready(self):
        return bool(self.keys) and self.keys[0][0] <= self.tick

    def type_keys(self, at_tick, words):
        self.keys.extend((at_tick, w) for w in words)
        self.keys.sort(key=lambda k: k[0])

    # ----- probes and running
    def probe(self, off, fn, seg=LOAD_SEG):
        """Call fn(machine) each time execution reaches seg:off."""
        lin = seg * 16 + off
        self.uc.hook_add(UC_HOOK_CODE, lambda uc, a, s, _: fn(self), None, lin, lin)

    def _timer(self):
        self.tick += 1
        self.last_ip = (self.reg("cs"), self.reg("ip"))
        if not self.reg("flags") & IF_FLAG:
            return
        if self.scans and self.scans[0][0] <= self.tick:
            self.port60 = self.scans.pop(0)[1]
            self.enter_vector(9)
        self.enter_vector(8)

    def press(self, at_tick, scan, hold_ticks):
        """A hardware make code at `at_tick` and its break code `hold_ticks` later."""
        self.scans += [(at_tick, scan), (at_tick + hold_ticks, scan | 0x80)]
        self.scans.sort()

    def run(self, ticks):
        """Run for at most `ticks` 60 Hz timer ticks; stop early on exit or `halt`."""
        end, self.halted = self.tick + ticks, False
        while self.tick < end and self.exit_code is None and not self.halted:
            self.waiting = False
            pc = self.reg("cs") * 16 + self.reg("ip")
            try:
                self.uc.emu_start(pc, 0x100000, count=TICK_INSNS)
            except UcError as e:
                self.crash = (self.reg("cs"), self.reg("ip"), str(e))
                break
            if not self.halted:
                self._timer()
        return self
