from util.crypto import xor_cycle


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
        max_animated_objects, meta_bytes = header_data
        object_name_rooms = Object.get_object_name_room_triplets(meta_bytes)

        return [(item, room, Object.parse_object_name(decrypted_bytes, name)) for item, name, room in object_name_rooms]

    @staticmethod
    def extract_object_header_data(bs):
        header = bs[:3]
        inventory_offset = int.from_bytes(header[:2], 'little')
        inventory_metadata = bs[3:inventory_offset + 3]
        max_animated_objects = header[2]

        return max_animated_objects, inventory_metadata

    @staticmethod
    def parse_object_name(bs, name):
        i, seq = name, bytearray([])

        while bs[i] != 0:
            seq.append(bs[i])
            i += 1

        return seq

    @staticmethod
    def get_object_name_room_triplets(triplets):
        object_name_rooms, i, t, end = [], 0, 0, len(triplets)

        while t < end:
            a, b, c = triplets[t], triplets[t + 1], triplets[t + 2]
            name = ((b << 8) | a) + 3
            object_name_rooms.append((i, name, c))
            i, t = i + 1, t + 3

        return object_name_rooms


def decrypt_object_file(file):
    return xor_cycle("Avis Durgan", file)


def decrypt_object_to_file(file, new_file):
    with open(new_file, mode='wb') as f:
        f.write(decrypt_object_file(file))
