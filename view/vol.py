from util.byte import nibble


# view_offset is the value returned by read_dir: the byte offset of this resource within its VOL file.
#
# Layout at view_offset:
#   +0..+4   VOL chunk header (5 bytes: signature, vol number, resource length) -- skipped
#   +5..+6   VIEW header bytes 0-1 (format version markers, always 1 or 2, then 1) -- skipped
#   +7       VIEW header byte 2: number of loops
#   +8..+9   VIEW header bytes 3-4: description offset (relative to view_offset + 5)
#   +10..    VIEW header bytes 5+: loop offsets, 2 bytes each (also relative to view_offset + 5)
def get_view_data(vol_file_path, view_offset):
    with open(vol_file_path, mode='rb') as f:
        # Skip VOL chunk header (5 bytes) + VIEW version bytes (2 bytes) to land on num_loops.
        f.seek(view_offset + 7)

        i, num_loops, desc_bytes, loop_offsets = 0, int.from_bytes(f.read(1), 'big'), f.read(2), []
        desc_ls, desc_ms = desc_bytes
        # Offsets in the VIEW header are relative to the start of the VIEW payload,
        # which begins after the 5-byte VOL chunk header -- hence + view_offset + 5.
        desc_offset = (desc_ms << 8) + desc_ls + view_offset + 5

        while i < num_loops:
            ls, ms = f.read(2)
            loop_offsets.append((ms << 8) + ls + view_offset + 5)
            i += 1

        cels = get_cel_data(f, get_view_cels(f, loop_offsets))

    return desc_offset, cels


def get_view_cels(vol_file, loop_offsets):
    cel_offsets = []

    for loop_offset in loop_offsets:
        vol_file.seek(loop_offset)
        i, num_cells = 0, int.from_bytes(vol_file.read(1), 'big')

        while i < num_cells:
            ls, ms = vol_file.read(2)
            cel_offsets.append((ms << 8) + ls + loop_offset)
            i += 1

    return cel_offsets


def get_cel_data(vol_file, cel_offsets):
    cels = []

    for cel_offset in cel_offsets:
        vol_file.seek(cel_offset)

        width, height, alpha_mirroring = vol_file.read(3)
        # Cel header byte 2 layout (verified empirically against AGI Studio for SQ1):
        #   high nibble (bits 4-7) = mirror info
        #   low nibble  (bits 0-3) = transparent color index
        # Note: this is the OPPOSITE of what agidev's AGI spec page states. The empirical
        # behavior matches AGI Studio's renderer, so the spec page appears to be wrong
        # (or uses non-standard bit numbering).
        width, mirror, alpha = width * 2, nibble(alpha_mirroring, 'hi'), nibble(alpha_mirroring, 'lo')
        cel_data = []

        i = 0

        while i < height:
            b = vol_file.read(1)

            if not b:
                raise ValueError(f"Truncated cel data at {cel_offset}")

            b = b[0]

            if b == 0x00:
                i += 1

            cel_data.append((nibble(b, 'hi'), nibble(b, 'lo')))

        cels.append((width, height, mirror, alpha, cel_data))

    return cels
