from util.byte import nibble
from sdl2.ext.color import Color


# 4-bit, 16 color EGA palette
palette = [
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA), (0xAA, 0x00, 0x00),
    (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA), (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF),
    (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF), (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55),
    (0xFF, 0xFF, 0xFF)
]


def draw_cel_data(renderer, width, height, pixels, alpha):
    x, y = width, height
    # using the width and height information from the cel header, we can stop here when y = n - 1,
    # or when number of pixels drawn = x * y
    for color, num_pixels in pixels:
        if color == 0 == num_pixels:
            # we've finished a line, so reset x to the beginning and move y down
            x, y = width, y + 1
            continue

        (r, g, b), n = palette[color], x + 2 * num_pixels
        renderer.color = Color(r, g, b, 0xFF) if color != alpha else Color(r, g, b, 0x00)
        renderer.draw_point(points=[(x0, y) for x0 in range(x, n)])
        # because we drew all the way to n, we need to set x to n here
        x = n


def read_cel_data(image):
    # returns a list of pairs of nibbles such that (color, num_pixels) is contained in each pair
    return map(lambda byte: (nibble(byte, 'hi'), nibble(byte, 'lo')), image)
