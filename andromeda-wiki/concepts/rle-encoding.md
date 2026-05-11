# RLE Encoding (VIEW cel data)

AGI VIEW cels store their pixel data as a row-major RLE (run-length encoded) byte stream. Each byte is a **chunk** packing a color index and a run length into one nibble each; rows are terminated by a sentinel byte. The encoding is shared by every VIEW cel and is **specific to VIEWs** — PICTURE resources use a different bytecode-based scheme (see [[entities/picture]] and [[concepts/picture-compression]]). [6-1-VIEW.html §Cel data]

## Chunk byte layout

```
bit:  7   6   5   4   3   2   1   0
     [---C---]   [---N---]

C = color index (high nibble, 0..15) — EGA palette index, see [[concepts/ega-palette]]
N = run length (low nibble, 1..15)   — number of consecutive pixels of color C
```

Examples [6-1-VIEW.html §Cel data]:
- `0xA5` → 5 pixels of color 10 (light green)
- `0xF3` → 3 pixels of color 15 (white)
- `0x00` → row terminator (see below)

The andromeda decoder extracts both nibbles in one pass via the `nibble()` helper [resource/view.py:106; util/byte.py].

## Row termination

A `0x00` byte marks end-of-row. The next byte begins the next row. Total rows per cel = cel header byte 1 (height) [6-1-VIEW.html §Cel data; resource/view.py:103-104].

Note that `0x00` is unambiguous as a terminator because a chunk with `N = 0` (zero-length run) carries no information and would never be emitted — every real chunk has `N ≥ 1`. The renderer at [gfx/view_render.py:13] treats `(color == 0 && num_pixels == 0)` as the sentinel after the parser splits the byte into a `(color, count)` tuple.

## Transparency padding

If a row's last run is the cel's transparent color (low nibble of cel header byte 2 — see [[entities/view]] §"Byte 2 layout"), the encoder may omit that final chunk: the `0x00` terminator implicitly pads transparent pixels to the right edge of the cel [6-1-VIEW.html §Cel data, "If the color of the last chunk on the line is the transparent color..."]. This is a space optimization; sparse sprites with large transparent margins save 1-2 bytes per row.

The renderer doesn't need to know about the omission specifically — the unwritten pixels simply aren't drawn, which is the same outcome as if they had been encoded as transparent.

## Rendering steps

The andromeda renderer at [gfx/view_render.py:5-22] (SDL draw) and [gfx/view_render.py:26-46] (visual-screen composite) implements:

1. Read next `(color, count)` tuple from the parsed cel data.
2. If `count == 0 && color == 0`: end of row — reset `x = 0`, increment `y`, continue.
3. Otherwise, draw `count × 2` screen pixels starting at column `x`. The ×2 doubles AGI logical-pixel width to EGA screen-pixel width.
4. If `color == cel.alpha` (transparent), skip the actual pixel writes — the underlying screen content is preserved.
5. If the cel is mirrored relative to the current loop, flip the x coordinate: `cel.width - 1 - x` [gfx/view_render.py:21, 43].
6. Advance `x` by `count × 2`. Loop until `y >= cel.height`.

The horizontal ×2 doubling is shared with the visual-screen renderer at [gfx/palette.py:13-34] (`visual_screen_buffer_to_texture`), which doubles every visual-screen pixel column when blitting to the 320-wide SDL surface.

## Worked example

A 12-pixel-wide × 2-pixel-tall cel where:
- Row 0 = 3 red pixels, 9 transparent pixels (transparent color = 0)
- Row 1 = 12 blue pixels

With cel header byte 2's low nibble = 0 (transparency index 0), the encoded bytes are:

```
hex:  43 00 19 00
```

- `0x43` → row 0: 3 pixels of color 4 (red)
- `0x00` → end of row 0; remaining 9 transparent pixels not encoded
- `0x19` → row 1: 9 pixels of color 1 (blue)? — no, wait

Correction: width = 12 logical AGI pixels, and each chunk's N is 1..15, so 12 blue pixels fits in one chunk: `0x1C` (12 pixels of color 1, since 0xC = 12). Then:

```
hex:  43 00 1C 00
```

- `0x43` → 3 red
- `0x00` → end row 0
- `0x1C` → 12 blue
- `0x00` → end row 1

Total: 4 bytes for a 24 EGA-pixel-wide × 2-pixel-tall cel.

## See also

- [[entities/view]] — VIEW resource format; cel header byte 2 holds the transparency color.
- [[concepts/ega-palette]] — color index → RGB lookup.
- [[concepts/picture-compression]] — distinct compression scheme used by PICTURE resources (not RLE).
- [[sources/6-1-view]] — chapter provenance.
