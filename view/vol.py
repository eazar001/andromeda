from util.byte import nibble


# offset here is expected as the value provided by read_view_dir
def get_view_loops(vol_file, view_offset):
    with open(vol_file, mode='rb') as f:
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

        return desc_offset, loop_offsets


def get_view_cels(vol_file, loop_offsets):
    offset_pairs = []

    with open(vol_file, mode='rb') as f:
        for loop_offset in loop_offsets:
            f.seek(loop_offset)
            i, num_cells = 0, int.from_bytes(f.read(1), 'big')

            while i < num_cells:
                ls, ms = f.read(2)
                offset_pairs.append((loop_offset, (ms << 8) + ls))
                i += 1

    return offset_pairs


def get_cel_data(vol_file, offset_pairs):
    cels = []

    with open(vol_file, mode='rb') as f:
        for loop_offset, cel_offset in offset_pairs:
            f.seek(loop_offset + cel_offset)

            # make sure to call draw_cel_data and enforce that we only pass in the cel data as long as the number of
            # 0x00's <= height
            width, height, alpha_mirroring = f.read(3)
            width, mirror, alpha = width * 2, nibble(alpha_mirroring, 'lo'), nibble(alpha_mirroring, 'hi')
            cels.append((width, height, mirror, alpha))
