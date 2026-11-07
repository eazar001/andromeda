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
                bs.append((vol, offset))
                store.clear()
                count += 1
            else:
                store.append(b)

    return bs


def read_byte_triplet(triplet):
    first, second, third = triplet
    vol = nibble(first, 'hi')
    offset = (nibble(first, 'lo') << 16) | ((second << 8) | third)

    return vol, offset
