"""BIOS services the interpreter calls, and the port reads it makes."""
from dataclasses import dataclass, field

CF, ZF = 0x001, 0x040
TEXT_COLS = 40


@dataclass
class BiosState:
    mode: int = 3
    cursor: tuple = (0, 0)
    vstatus: int = 0


def _ah(m):
    return m.reg("ax") >> 8


def _al(m):
    return m.reg("ax") & 0xFF


def int10(m):
    ah, b = _ah(m), m.bios
    m.video_log.append((m.tick, ah, _al(m), m.reg("bx"), m.reg("cx"), m.reg("dx")))
    if ah == 0x00:
        b.mode = _al(m) & 0x7F
        if not _al(m) & 0x80:
            m.ega.clear()
    elif ah == 0x02:
        dx = m.reg("dx"); b.cursor = (dx >> 8, dx & 0xFF)
    elif ah == 0x03:
        m.reg("dx", (b.cursor[0] << 8) | b.cursor[1]); m.reg("cx", 0x0607)
    elif ah == 0x09:
        _write_chars(m, _al(m), m.reg("bx") & 0xFF, m.reg("cx"))
    elif ah == 0x05 and _al(m) == 0x80:                      # PCjr: read CRT and CPU page registers
        m.reg("bx", m.jr_page << 8 | m.jr_page)
    elif ah == 0x0F:
        m.reg("ax", (TEXT_COLS << 8) | b.mode); m.reg("bx", m.reg("bx") & 0xFF)
    elif ah == 0x12 and (m.reg("bx") & 0xFF) == 0x10 and m.ega_present:
        m.reg("bx", 0x0003); m.reg("cx", 0x0009)             # colour EGA, 256K, switches 9


def _write_chars(m, ch, attr, count):
    row, col = m.bios.cursor
    for i in range(count):
        m.bios_chars[(row, col + i)] = (ch, attr)


def int11(m):
    m.reg("ax", 0x0021 | (m.floppies - 1) << 6)


def int12(m):
    m.reg("ax", 640)


def int15(m):
    m.set_flag(CF, True); m.reg("ax", (0x86 << 8) | _al(m))


def int16(m):
    ah = _ah(m) & 0x0F
    if ah == 0x00:
        if not m.key_ready() and m.auto_key is not None:
            m.reg("ax", m.auto_key)
            return
        if not m.key_ready():
            m.reg("ip", m.reg("ip") - 2); m.waiting = True     # retry after the next tick
            return
        m.reg("ax", m.keys.pop(0)[1])
    elif ah == 0x01:
        ready = m.key_ready()
        m.set_flag(ZF, not ready)
        if ready:
            m.reg("ax", m.keys[0][1])
    elif ah == 0x02:
        m.reg("ax", (m.reg("ax") & 0xFF00) | m.shift_flags)


def int1a(m):
    if _ah(m) == 0x00:
        t = m.tick * 18206 // 60000 + 0x1234
        m.reg("cx", t >> 16); m.reg("dx", t & 0xFFFF); m.reg("ax", m.reg("ax") & 0xFF00)


def port_in(m, port):
    if port in (0x3DA, 0x3BA):                                  # retrace bits toggle
        m.bios.vstatus ^= 0x89
        return m.bios.vstatus
    if port == 0x201:
        return m.joy_port
    if port == 0x60:
        return m.port60
    return 0xFF
