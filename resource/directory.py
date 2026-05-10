from util.byte import nibble


def read_dir(file):
    with open(file, mode='rb') as f:
        store, bs, count, limit = [], [], 0, 256

        for i, b in enumerate(f.read(), start=1):
            if count >= limit:
                break

            if i % 3 == 0:
                store.append(b)
                vol, offset = read_byte_triplet(store)

                if (vol, offset) != (0xF, 0xFFFFF):
                    bs.append((vol, offset))
                    count += 1

                store.clear()
            else:
                store.append(b)

    return bs


def read_byte_triplet(triplet):
    first, second, third = triplet
    vol = nibble(first, 'hi')
    offset = (nibble(first, 'lo') << 16) | ((second << 8) | third)

    return vol, offset
