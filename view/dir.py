from util.byte import nibble


def read_view_dir(file):
    with open(file, mode='rb') as f:
        store, bs = [], []

        for i, b in enumerate(f.read(), start=1):
            if i % 3 == 0:
                store.append(b)
                vol, offset = read_view_byte_triplet(tuple(store))

                if (vol, offset) != (15, 1048575):
                    bs.append((vol, offset))
                store.clear()
            else:
                store.append(b)

    return bs


def read_view_byte_triplet(triplet):
    first, second, third = triplet
    vol = nibble(first, 'hi')
    offset = (nibble(first, 'lo') << 16) | ((second << 8) | third)

    return vol, offset
