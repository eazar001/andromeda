import ctypes
from itertools import cycle

from sdl2 import SDL_PollEvent, SDL_Event
from sdl2.ext.renderer import Renderer
from sdl2.ext.window import Window
from sdl2.ext.color import Color
from sdl2 import SDL_Init, SDL_INIT_VIDEO, SDL_WINDOWPOS_CENTERED, SDL_WINDOW_SHOWN
from sdl2 import SDL_BLENDMODE_BLEND, SDL_Quit

# "key" item from inventory in SQ1
test_image = [
    0x4F, 0x4A, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00,
    0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08,
    0x41, 0x00, 0x41, 0x08, 0x81, 0x72, 0x81, 0x72, 0x09, 0x41, 0x00, 0x41, 0x08, 0x81, 0x72, 0x81, 0x72, 0x09,
    0x41, 0x00, 0x41, 0x08, 0x81, 0x71, 0x82, 0x71, 0x0A, 0x41, 0x00, 0x41, 0x08, 0x81, 0x72, 0x81, 0x72, 0x09,
    0x41, 0x00, 0x41, 0x09, 0x81, 0x71, 0x01, 0x81, 0x71, 0x09, 0x41, 0x00, 0x41, 0x08, 0x81, 0x72, 0x81, 0x72,
    0x09, 0x41, 0x00, 0x41, 0x08, 0x81, 0x71, 0x82, 0x71, 0x0A, 0x41, 0x00, 0x41, 0x08, 0x81, 0x72, 0x81, 0x72,
    0x09, 0x41, 0x00, 0x41, 0x09, 0x81, 0x71, 0x81, 0x72, 0x09, 0x41, 0x00, 0x41, 0x08, 0x81, 0x72, 0x81, 0x72,
    0x09, 0x41, 0x00, 0x41, 0x07, 0x82, 0x75, 0x09, 0x41, 0x00, 0x41, 0x06, 0x82, 0x77, 0x08, 0x41, 0x00, 0x41,
    0x05, 0x82, 0x73, 0x83, 0x73, 0x07, 0x41, 0x00, 0x41, 0x04, 0x82, 0x73, 0x03, 0x82, 0x73, 0x06, 0x41, 0x00,
    0x41, 0x03, 0x82, 0xF3, 0x05, 0x82, 0xF3, 0x05, 0x41, 0x00, 0x41, 0x03, 0x81, 0x73, 0x07, 0x82, 0x73, 0x04,
    0x41, 0x00, 0x41, 0x03, 0x81, 0x73, 0x08, 0x81, 0x73, 0x04, 0x41, 0x00, 0x41, 0x03, 0x84, 0x07, 0x85, 0x04,
    0x41, 0x00, 0x41, 0x04, 0x81, 0x73, 0x05, 0x82, 0x73, 0x05, 0x41, 0x00, 0x41, 0x05, 0x81, 0x73, 0x03, 0x82,
    0x73, 0x06, 0x41, 0x00, 0x41, 0x06, 0x81, 0x73, 0x83, 0x73, 0x07, 0x41, 0x00, 0x41, 0x07, 0x81, 0x71, 0xF1,
    0x72, 0x81, 0x72, 0x08, 0x41, 0x00, 0x41, 0x08, 0x81, 0xF1, 0x72, 0x81, 0x71, 0x09, 0x41, 0x00, 0x41, 0x0F,
    0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00, 0x41, 0x0F, 0x08, 0x41, 0x00,
    0x41, 0x0F, 0x08, 0x41, 0x00, 0x4F, 0x4A, 0x00
]

# 4-bit, 16 color EGA palette
palette = [
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA), (0xAA, 0x00, 0x00),
    (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA), (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF),
    (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF), (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55),
    (0xFF, 0xFF, 0xFF)
]


def draw_cel_data(renderer, x, y, pixels, alpha):
    for color, num_pixels in pixels:
        if color == 0 == num_pixels:
            x, y = 0, y + 1
            continue

        (r, g, b), n = palette[color], x + 2 * num_pixels
        renderer.color = Color(r, g, b, alpha)
        renderer.draw_point(points=[(x0, y) for x0 in range(x, n)])
        x = n


def read_cel_data(image):
    # returns a list of pairs of nibbles such that (color, num_pixels) is contained in each pair
    return map(lambda byte: (nibble(byte, 'hi'), nibble(byte, 'lo')), image)


def render_test():
    SDL_Init(SDL_INIT_VIDEO)
    window = Window(
        "Render test",
        (640, 480),
        (SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED),
        SDL_WINDOW_SHOWN
    )

    renderer = Renderer(window)
    renderer.blendmode = SDL_BLENDMODE_BLEND
    renderer.color = Color(0xFF, 0xFF, 0xFF, 0xFF)
    renderer.clear()

    draw_cel_data(renderer, 0, 0, read_cel_data(test_image), 0xFF)
    renderer.present()

    running, event = True, SDL_Event()

    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == 0x100:
                running = False
                break

    window.close()
    SDL_Quit()


class InventoryObject:
    def __init__(self, index, name, room):
        self.index = index
        self.name = name
        self.room = room

    @staticmethod
    def extract_inventory_objects(file):
        inventory_objects = list(map(lambda t: InventoryObject(index=t[0], room=t[1], name=t[2]),
                                     InventoryObject.extract_object_triplets(file)))

        return inventory_objects

    @staticmethod
    def extract_object_triplets(file):
        decrypted_bytes = decrypt_object_file(file)
        header_data = InventoryObject.extract_object_header_data(decrypted_bytes)
        max_animated_objects, inventory_data, meta_bytes, inventory_start = header_data
        object_rooms = InventoryObject.get_object_room_pairs(meta_bytes, inventory_start)

        return list(map(lambda t: (t[0][0], t[0][1], t[1]),
                        zip(object_rooms, InventoryObject.parse_object_codes(inventory_data))))

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


def nibble(byte, section, endian='big'):
    if endian == 'little':
        section = 'lo' if section == 'hi' else section

    return (240 & byte) >> 4 if section == 'hi' else 15 & byte


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


def decrypt_object_file(file):
    return decrypt_file("Avis Durgan", file)


def decrypt_file(key_string, file):
    with open(file, mode='rb') as f:
        return bytearray(map(lambda t: t[0] ^ t[1], zip(list(f.read()), cycle(map(ord, key_string)))))


def decrypt_object_to_file(file, new_file):
    with open(new_file, mode='wb') as f:
        f.write(decrypt_object_file(file))


if __name__ == '__main__':
    render_test()
