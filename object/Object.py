from itertools import cycle


class Object:
    def __init__(self, index, name, room):
        self.index = index
        self.name = name
        self.room = room

    @staticmethod
    def extract_inventory_objects(file):
        inventory_objects = list(map(lambda t: Object(index=t[0], room=t[1], name=t[2]),
                                     Object.extract_object_triplets(file)))

        return inventory_objects

    @staticmethod
    def extract_object_triplets(file):
        decrypted_bytes = decrypt_object_file(file)
        header_data = Object.extract_object_header_data(decrypted_bytes)
        max_animated_objects, inventory_data, meta_bytes, inventory_start = header_data
        object_rooms = Object.get_object_room_pairs(meta_bytes, inventory_start)

        return list(map(lambda t: (t[0][0], t[0][1], t[1]),
                        zip(object_rooms, Object.parse_object_codes(inventory_data))))

    @staticmethod
    def extract_object_header_data(bs):
        header = bs[:3]
        inventory_offset = header[0] + header[1]
        inventory_start = inventory_offset + 5
        inventory_metadata = bs[3:inventory_offset + 3]
        inventory_data = bs[inventory_start:]
        max_animated_objects = header[2]

        return max_animated_objects, inventory_data, inventory_metadata, inventory_start

    @staticmethod
    def parse_object_codes(bs):
        length, i, seq, seqs = len(bs), 0, bytearray([]), []

        while i < length:
            if bs[i] == 0:
                seqs.append(seq[:])
                seq.clear()
                i += 1
                continue

            seq.append(bs[i])
            i += 1

        return seqs

    @staticmethod
    def get_object_room_pairs(triplets, inventory_start):
        pairs, i, t, end = [], 0, 0, len(triplets)

        while t < end:
            a, b, c = triplets[t], triplets[t + 1], triplets[t + 2]

            if ((b << 8) | a) + 3 < inventory_start:
                t += 3
                continue

            pairs.append((i, c))

            i, t = i + 1, t + 3

        return pairs


def decrypt_object_file(file):
    return decrypt_file("Avis Durgan", file)


def decrypt_file(key_string, file):
    with open(file, mode='rb') as f:
        return bytearray(map(lambda t: t[0] ^ t[1], zip(list(f.read()), cycle(map(ord, key_string)))))


def decrypt_object_to_file(file, new_file):
    with open(new_file, mode='wb') as f:
        f.write(decrypt_object_file(file))
