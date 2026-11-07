"""Build PICTURE and VIEW payloads for scenarios."""
import struct

END = 0xFF


def picture(*ops):
    """PICTURE bytecode from opcode tuples, ended by 0xFF."""
    return bytes(b for op in ops for b in op) + bytes([END])


def priority_line(pri, x0, y0, x1, y1):
    """Priority-only absolute line: disable visual, set priority, draw."""
    return (0xF1, 0xF2, pri, 0xF6, x0, y0, x1, y1)


def _rle_row(row, alpha):
    out, i = bytearray(), 0
    while i < len(row):
        n = 1
        while i + n < len(row) and row[i + n] == row[i] and n < 15:
            n += 1
        out.append(row[i] << 4 | n)
        i += n
    while out and out[-1] >> 4 == alpha:          # trailing transparent runs are implied
        out.pop()
    return bytes(out) + b"\0"


def cel(rows, alpha):
    """One cel: width, height, transparent color, then RLE rows each ending in 0."""
    return bytes([len(rows[0]), len(rows), alpha & 0x0F]) + b"".join(_rle_row(r, alpha) for r in rows)


def view(cels):
    """A one-loop VIEW holding `cels`, each a (rows, alpha) pair."""
    bodies = [cel(r, a) for r, a in cels]
    loop_head = 1 + 2 * len(bodies)
    offsets, pos = [], loop_head
    for b in bodies:
        offsets.append(pos)
        pos += len(b)
    loop = bytes([len(bodies)]) + b"".join(struct.pack("<H", o) for o in offsets) + b"".join(bodies)
    header = bytes([1, 1, 1]) + struct.pack("<H", 0) + struct.pack("<H", 7)
    return header + loop
