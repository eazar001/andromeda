from sdl2 import SDL_CreateRGBSurfaceFrom, SDL_FreeSurface
from sdl2.ext.renderer import Renderer, Texture

from gfx.screens import VisualScreen

# 4-bit, 16-color EGA palette
palette = [
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA), (0xAA, 0x00, 0x00),
    (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA), (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF),
    (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF), (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55),
    (0xFF, 0xFF, 0xFF)
]

def visual_screen_buffer_to_texture(screen: VisualScreen, renderer: Renderer) -> Texture:
    bs = visual_screen_to_bytes(screen)

    surface = SDL_CreateRGBSurfaceFrom(
        bs,
        screen.width * 2, # width * 2 = 160 * 2 = 320
        screen.height,    # height
        32,               # bits per pixel = RGBA = 4 * 8 = 32
        screen.width * 8, # pitch = width * 2 * bytes per pixel
        0x000000FF,
        0x0000FF00,
        0x00FF0000,
        0xFF000000
    )

    texture = Texture(renderer, surface)
    SDL_FreeSurface(surface)

    return texture


def visual_screen_to_bytes(screen: VisualScreen) -> bytes:
    pixels = []

    for row in screen.buffer:
        for color in row:
            r, g, b = palette[color]
            pixels.append(bytes([r, g, b, 0xFF]))
            pixels.append(bytes([r, g, b, 0xFF]))

    return b''.join(pixels)
