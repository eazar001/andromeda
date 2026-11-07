"""Load the decoded MZ interpreter at a segment, applying its relocations."""
from dataclasses import dataclass
import struct


@dataclass(frozen=True)
class Image:
    data: bytes
    load_seg: int
    cs: int
    ip: int
    ss: int
    sp: int


def load_mz(raw: bytes, load_seg: int) -> Image:
    """Return the program image with every relocated word shifted by `load_seg`."""
    if raw[:2] != b"MZ":
        raise ValueError("not an MZ executable")
    last, pages, nrel, hdr_par = struct.unpack_from("<HHHH", raw, 2)
    ss, sp, _, ip, cs, rel_off = struct.unpack_from("<HHHHHH", raw, 14)
    size = pages * 512 - (512 - last if last else 0)
    body = bytearray(raw[hdr_par * 16:size])
    for i in range(nrel):
        off, seg = struct.unpack_from("<HH", raw, rel_off + 4 * i)
        at = seg * 16 + off
        word = struct.unpack_from("<H", body, at)[0]
        struct.pack_into("<H", body, at, (word + load_seg) & 0xFFFF)
    return Image(bytes(body), load_seg, cs + load_seg, ip, ss + load_seg, sp)
