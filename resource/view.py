from dataclasses import dataclass, field

from resource.volume import VolumeReader
from util.byte import nibble
from io import BytesIO


@dataclass
class Cel:
    width: int
    height: int
    mirror: int
    non_mirror_idx: int
    alpha: int
    cel_data: list[tuple] = field(default_factory=list)

@dataclass
class Loop:
    loop_idx: int
    cels: list[Cel] = field(default_factory=list)

@dataclass
class View:
    desc_offset: int
    loops: list[Loop] = field(default_factory=list)


# view_offset is the value returned by read_dir: the byte offset of this resource within its VOL file.
# VolumeReader.read_resource() strips the 5-byte VOL chunk header and returns the VIEW payload as bytes.
#
# Layout of the VIEW payload (BytesIO position 0 = start of payload):
#   +0..+1   VIEW version markers (always 0x01/0x02 then 0x01) -- skipped
#   +2       number of loops
#   +3..+4   description offset (LE, relative to payload start)
#   +5..     loop offsets, 2 bytes each (LE, relative to payload start)
def get_view_data(reader: VolumeReader, view_offset: int):
    _header, view_bytes = reader.read_resource(view_offset)

    with BytesIO(view_bytes) as bs:
        # Skip VIEW version bytes (2 bytes) to land on num_loops.
        bs.seek(2)

        i, num_loops, desc_bytes, loop_offsets = 0, int.from_bytes(bs.read(1), 'big'), bs.read(2), []
        desc_ls, desc_ms = desc_bytes
        # Offsets are relative to payload start (BytesIO position 0).
        desc_offset = (desc_ms << 8) + desc_ls

        while i < num_loops:
            ls, ms = bs.read(2)
            loop_offsets.append((ms << 8) + ls)
            i += 1

        loops = get_cel_data(bs, get_view_cels(bs, loop_offsets))

    return View(desc_offset, loops)


def get_view_cels(bs, loop_offsets):
    cel_offsets = []
    loop_idx = 0

    for loop_offset in loop_offsets:
        bs.seek(loop_offset)
        i, num_cells = 0, int.from_bytes(bs.read(1), 'big')

        while i < num_cells:
            ls, ms = bs.read(2)
            cel_offsets.append((loop_idx, (ms << 8) + ls + loop_offset))
            i += 1

        loop_idx += 1

    return cel_offsets


def get_cel_data(bs, cel_offsets):
    cels, loops, last_loop_idx = [], [], cel_offsets[0][0]

    for loop_idx, cel_offset in cel_offsets:
        bs.seek(cel_offset)

        width, height, alpha_mirroring = bs.read(3)
        # Cel header byte 2 layout (verified empirically against AGI Studio for SQ1):
        #   high nibble (bits 4-7) = mirror info (bit 0 signals whether mirror exists, bits 1 - 3 is the loop index of the non-mirrored loop)
        #   low nibble  (bits 0-3) = transparent color index
        # Note: this is the OPPOSITE of what agidev's AGI spec page states. The empirical
        # behavior matches AGI Studio's renderer, so the spec page appears to be wrong
        # (or uses non-standard bit numbering).
        mirror, alpha = nibble(alpha_mirroring, 'hi'), nibble(alpha_mirroring, 'lo')
        mirror, non_mirror_idx = mirror >> 3, mirror & 7
        cel_data = []

        i = 0

        while i < height:
            b = bs.read(1)

            if not b:
                raise ValueError(f"Truncated cel data at {cel_offset}")

            b = b[0]

            if b == 0x00:
                i += 1

            cel_data.append((nibble(b, 'hi'), nibble(b, 'lo')))

        if last_loop_idx == loop_idx:
            cels.append(Cel(width, height, mirror, non_mirror_idx, alpha, cel_data))
        else:
            loops.append(Loop(last_loop_idx, cels))
            cels = [Cel(width, height, mirror, non_mirror_idx, alpha, cel_data)]

        last_loop_idx = loop_idx

    loops.append(Loop(last_loop_idx, cels))

    return loops
