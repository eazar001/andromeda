from sdl2 import SDL_CreateTextureFromSurface, SDL_Texture, SDL_Renderer, SDL_CreateRGBSurfaceFrom

from gfx.screens import VisualScreen

# 4-bit, 16-color EGA palette
palette = [
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA), (0xAA, 0x00, 0x00),
    (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA), (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF),
    (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF), (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55),
    (0xFF, 0xFF, 0xFF)
]

def visual_screen_buffer_to_texture(screen: VisualScreen, renderer: SDL_Renderer) -> SDL_Texture:
    pixels = []

    for row in screen.screen:
        for color in row:
            r, g, b = palette[color]
            pixels.append(bytes([r, g, b, 0xFF]))
            pixels.append(bytes([r, g, b, 0xFF]))
    
    surface = SDL_CreateRGBSurfaceFrom(
        b''.join(pixels),
        320,              # width * 2 = 160 * 2 = 320
        168,              # height
        32,               # bytes per pixel = RGBA = 4 * 8 = 32
        1280,             # pitch = width * bytes_per_pixel
        Rmask=0x000000FF,
        Gmask=0x0000FF00,
        Bmask=0x00FF0000,
        Amask=0xFF000000

    )
    return SDL_CreateTextureFromSurface(renderer, surface)
