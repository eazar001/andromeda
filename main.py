import ctypes

from gfx.palette import visual_screen_buffer_to_texture
from gfx.screens import VisualScreen
from gfx.view_render import composite_cel
from resource.view import get_view_data
from resource.directory import read_dir
from sdl2 import SDL_PollEvent, SDL_Event, SDL_RenderSetScale, SDL_Delay
from sdl2.ext.renderer import Renderer
from sdl2.ext.window import Window
from sdl2.ext.color import Color
from sdl2 import SDL_Init, SDL_INIT_VIDEO, SDL_WINDOWPOS_CENTERED, SDL_WINDOW_SHOWN
from sdl2 import SDL_BLENDMODE_BLEND, SDL_Quit

from resource.volume import VolumeReader


def animate_cels(loop_idx, cels, window, frame_delay_ms=120, infinite=False):
    renderer = Renderer(window)
    renderer.blendmode = SDL_BLENDMODE_BLEND
    SDL_RenderSetScale(renderer.sdlrenderer, 8.0, 8.0)

    running, event = True, SDL_Event()
    cel_idx = 0

    while running and cel_idx < len(cels):
        renderer.color = Color(0x00, 0x00, 0x00, 0x00)
        renderer.clear()
        visual_screen = VisualScreen(160, 168, default=0x00)
        composite_cel(visual_screen, loop_idx, cels[cel_idx])
        texture = visual_screen_buffer_to_texture(visual_screen, renderer)
        renderer.copy(texture, dstrect=(0, 0))
        renderer.present()
        texture.destroy()

        SDL_Delay(frame_delay_ms)

        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == 0x100:
                running = False
                break

        cel_idx = (cel_idx + 1) % len(cels) if infinite else cel_idx + 1

    renderer.destroy()

    return running


def main():
    """Open one window and cycle through all `cels`. Close the window to exit."""
    SDL_Init(SDL_INIT_VIDEO)
    window = Window(
        "Walk cycle",
        (1280, 1024),
        (SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED),
        SDL_WINDOW_SHOWN
    )

    stop = False

    for vol, view_offset in read_dir('test_games/sq1/VIEWDIR'):
        vol_reader = VolumeReader(f'test_games/sq1/VOL.{vol}')
        view = get_view_data(vol_reader, view_offset)
        vol_reader.close()

        for loop in view.loops:
            if not animate_cels(loop.loop_idx, loop.cels, window):
                stop = True

        if stop:
            break

    window.close()
    SDL_Quit()

    for vol, view_offset in read_dir('test_games/sq1/VIEWDIR'):
        print(vol, view_offset)

    for vol, logic_offset in read_dir('test_games/sq1/LOGDIR'):
        print(vol, logic_offset)

    for vol, pic_offset in read_dir('test_games/sq1/PICDIR'):
        print(vol, pic_offset)

    for vol, sound_offset in read_dir('test_games/sq1/SNDDIR'):
        print(vol, sound_offset)


if __name__ == '__main__':
    main()
