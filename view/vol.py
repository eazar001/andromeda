from util.byte import nibble


# offset here is expected as the value provided by read_dir
def get_view_data(vol_file_path, view_offset):
    with open(vol_file_path, mode='rb') as f:
        # seek past the offset and 5 additional bytes from the header and two additional unused bytes from the view
        # header
        f.seek(view_offset + 7)

        i, num_loops, desc_bytes, loop_offsets = 0, int.from_bytes(f.read(1), 'big'), f.read(2), []
        desc_ls, desc_ms = desc_bytes
        desc_offset = (desc_ms << 8) + desc_ls

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
    cels, cel_data = [], bytearray([])

    for cel_offset in cel_offsets:
        vol_file.seek(cel_offset)

        width, height, alpha_mirroring = vol_file.read(3)
        width, mirror, alpha = width * 2, nibble(alpha_mirroring, 'lo'), nibble(alpha_mirroring, 'hi')

        i = 0

        while i < height:
            b = vol_file.read(1)[0]

            if b == 0x00:
                i += 1

            cel_data.append(b)

        cels.append((width, height, mirror, alpha, cel_data))

    return cels
