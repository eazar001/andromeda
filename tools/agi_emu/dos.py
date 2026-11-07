"""DOS int 21h over the machine's in-memory file map. Writes stay in memory."""
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
import struct

CF = 0x001
NOT_FOUND, NO_HANDLES, BAD_HANDLE, NO_MEMORY = 2, 4, 6, 8
FILE_TIME, FILE_DATE = 0x6000, 0x1A21          # 12:00, 1993-01-01


@dataclass
class Handle:
    name: str
    pos: int = 0


@dataclass
class DosState:
    m: object
    handles: dict = field(default_factory=dict)
    dta: tuple = (0, 0x80)
    drive: int = 2
    free_seg: int = 0
    finds: list = field(default_factory=list)

    psp: int = 0

    def init_memory(self, psp, first_free):
        self.psp, self.free_seg = psp, first_free
        self.dta = (self.m.reg("ds"), 0x80)

    def data(self, name):
        return self.m.files.get(name)


def _ah(m):
    return m.reg("ax") >> 8


def _ok(m, ax=None):
    m.set_flag(CF, False)
    if ax is not None:
        m.reg("ax", ax)


def _fail(m, code):
    m.set_flag(CF, True); m.reg("ax", code)


def _asciiz(m, seg, off):
    raw = m.read(seg, off, 128)
    return raw[:raw.index(0)].decode("ascii", "replace")


def file_name(path):
    """DOS path to a file-map key: no drive, no directories, upper case."""
    return path.replace("/", "\\").split("\\")[-1].split(":")[-1].upper()


def _path_arg(m):
    return file_name(_asciiz(m, m.reg("ds"), m.reg("dx")))


def _new_handle(m, name):
    st = m.dos
    n = next(h for h in range(5, 64) if h not in st.handles)
    st.handles[n] = Handle(name)
    _ok(m, n)


def open_file(m):
    name = _path_arg(m)
    if m.dos.data(name) is None:
        return _fail(m, NOT_FOUND)
    _new_handle(m, name)


def create_file(m):
    name = _path_arg(m)
    m.files[name] = b""
    _new_handle(m, name)


def close_file(m):
    if m.dos.handles.pop(m.reg("bx"), None) is None:
        return _fail(m, BAD_HANDLE)
    _ok(m)


def read_file(m):
    h = m.dos.handles.get(m.reg("bx"))
    if h is None:
        return _fail(m, BAD_HANDLE)
    chunk = m.dos.data(h.name)[h.pos:h.pos + m.reg("cx")]
    m.write(m.reg("ds"), m.reg("dx"), chunk)
    h.pos += len(chunk)
    _ok(m, len(chunk))


def write_file(m):
    n, data = m.reg("bx"), m.read(m.reg("ds"), m.reg("dx"), m.reg("cx"))
    if n in (1, 2):
        m.stdout += data
        return _ok(m, len(data))
    h = m.dos.handles.get(n)
    if h is None:
        return _fail(m, BAD_HANDLE)
    old = m.files[h.name]
    m.files[h.name] = old[:h.pos].ljust(h.pos, b"\0") + data + old[h.pos + len(data):]
    h.pos += len(data)
    _ok(m, len(data))


def seek_file(m):
    h = m.dos.handles.get(m.reg("bx"))
    if h is None:
        return _fail(m, BAD_HANDLE)
    dist = (m.reg("cx") << 16) | m.reg("dx")
    base = (0, h.pos, len(m.dos.data(h.name)))[m.reg("ax") & 0xFF]
    h.pos = (base + dist) & 0xFFFFFFFF
    m.reg("dx", h.pos >> 16)
    _ok(m, h.pos & 0xFFFF)


def delete_file(m):
    if m.files.pop(_path_arg(m), None) is None:
        return _fail(m, NOT_FOUND)
    _ok(m)


def dup_handle(m):
    h = m.dos.handles.get(m.reg("bx"))
    if h is None:
        return _fail(m, BAD_HANDLE)
    _new_handle(m, h.name)
    m.dos.handles[m.reg("ax")].pos = h.pos


def file_date(m):
    m.reg("cx", FILE_TIME); m.reg("dx", FILE_DATE)
    _ok(m)


def _fill_dta(m, name):
    seg, off = m.dos.dta
    entry = (b"\0" * 0x15 + bytes([0x20]) + struct.pack("<HHI", FILE_TIME, FILE_DATE, len(m.files[name]))
             + name.encode("ascii").ljust(13, b"\0"))
    m.write(seg, off, entry)


def find_next(m):
    if not m.dos.finds:
        return _fail(m, 18)
    _fill_dta(m, m.dos.finds.pop(0))
    _ok(m, 0)


def find_first(m):
    pattern = _path_arg(m).replace("*.*", "*")
    m.dos.finds = sorted(n for n in m.files if fnmatchcase(n, pattern))
    if not m.dos.finds:
        return _fail(m, NOT_FOUND)
    find_next(m)


def alloc(m):
    """Blocks go one paragraph after their MCB, as DOS places them; `free_seg` is the next MCB."""
    want, st = m.reg("bx"), m.dos
    avail = m.mem_top - st.free_seg - 1
    if want > avail:
        m.reg("bx", avail)
        return _fail(m, NO_MEMORY)
    seg, st.free_seg = st.free_seg + 1, st.free_seg + 1 + want
    _ok(m, seg)


def resize(m):
    """Only the program's own block is resized: the next MCB follows it."""
    if m.reg("es") == m.dos.psp:
        m.dos.free_seg = m.dos.psp + m.reg("bx")
    _ok(m)


def set_vector(m):
    m.set_vector(m.reg("ax") & 0xFF, m.reg("ds"), m.reg("dx"))


def get_vector(m):
    seg, off = m.vector(m.reg("ax") & 0xFF)
    m.reg("es", seg); m.reg("bx", off)


def select_disk(m):
    m.dos.drive = m.reg("dx") & 0xFF
    m.reg("ax", (m.reg("ax") & 0xFF00) | 3)


def current_disk(m):
    m.reg("ax", (m.reg("ax") & 0xFF00) | m.dos.drive)


def set_dta(m):
    m.dos.dta = (m.reg("ds"), m.reg("dx"))


def get_cwd(m):
    m.write(m.reg("ds"), m.reg("si"), b"\0")
    _ok(m)


def exit_program(m):
    m.exit_code = m.reg("ax") & 0xFF


SERVICES = {
    0x0E: select_disk, 0x19: current_disk, 0x1A: set_dta, 0x25: set_vector, 0x35: get_vector,
    0x30: lambda m: m.reg("ax", 0x0003), 0x3C: create_file, 0x3D: open_file, 0x3E: close_file,
    0x3F: read_file, 0x40: write_file, 0x41: delete_file, 0x42: seek_file, 0x45: dup_handle,
    0x47: get_cwd, 0x48: alloc, 0x4A: resize, 0x4C: exit_program, 0x4E: find_first,
    0x4F: find_next, 0x57: file_date,
}


def int21(m):
    service = SERVICES.get(_ah(m))
    if service is None:
        m.unknown.append((m.tick, 0x21, _ah(m)))
        return _fail(m, 1)
    service(m)
