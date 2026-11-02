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

In 2.917 the draw routine counts `height` terminators and doesn't check row width, so a row that runs long spills into the next one [AGI 2.917 1000:9DFA]. In all 1,433 distinct SQ1 cels, no row is wider than its cel [SQ1 data check, audit draw].

Only the whole byte `0x00` ends a row when drawing. A chunk with `N = 0` and any other color is not a terminator, and the interpreter doesn't handle it safely:

- With the transparent color, it is skipped harmlessly [AGI 2.917 1000:9DD6].
- With any other color, the draw loop's counter starts at zero and wraps, repeating 65,536 times [AGI 2.917 1000:9DD8, 1000:9DF6].
- The mirror routine treats a zero low nibble as end of row once it has passed the leading transparent chunks, so the two routines disagree [AGI 2.917 1000:580D].

No SQ1 cel contains such a chunk [SQ1 data check, audit draw], so encoders must never emit one. The renderer at [gfx/view_render.py:9] treats `(color == 0 && num_pixels == 0)` as the sentinel after the parser splits the byte into a `(color, count)` tuple.

## Transparency padding

If a row's last run is the cel's transparent color (low nibble of cel header byte 2 — see [[entities/view]] §"Byte 2 layout"), the encoder may omit that final chunk: the `0x00` terminator implicitly pads transparent pixels to the right edge of the cel [6-1-VIEW.html §Cel data, "If the color of the last chunk on the line is the transparent color..."]. This is a space optimization. In SQ1 it is universal: no row in any cel ends in a transparent chunk [SQ1 data check, audit draw].

The renderer doesn't need to know about the omission specifically — the unwritten pixels simply aren't drawn, which is the same outcome as if they had been encoded as transparent. This is also how 2.917 behaves: a terminator moves straight to the next row [AGI 2.917 1000:9DFA].

The rule matters when a cel is mirrored, because the omitted run has to become a leading one. See [[entities/view]] §"Loop mirroring".

## Rendering steps

The andromeda compositor [gfx/view_render.py:composite_cel] implements:

1. Read next `(color, count)` tuple from the parsed cel data.
2. If `count == 0 && color == 0`: end of row — reset `x = 0`, increment `y`, continue.
3. Otherwise, cover `count` logical pixels starting at column `x`.
4. If `color == cel.alpha` (transparent), skip the actual pixel writes — the underlying screen content is preserved.
5. If the cel is mirrored relative to the current loop, flip the x coordinate: `cel.width - 1 - x` [gfx/view_render.py:18].
6. Advance `x` by `count`. Stop when `y >= cel.height`.

Compositing works in logical pixels. Horizontal doubling happens only when the finished screen is converted for SDL [gfx/palette.py:visual_screen_to_bytes].

These steps describe the project's compositor. The 2.917 draw routine reads the same stream the same way, and also applies the priority comparison, which the compositor doesn't yet do. It mirrors by rewriting the cel's data before drawing, rather than flipping `x` per pixel. See [[interpreter/priority-bands]] §"How a cel pixel is compared" [AGI 2.917 1000:9D75].

## Worked example

A 12-pixel-wide × 2-pixel-tall cel where:
- Row 0 = 3 red pixels, 9 transparent pixels (transparent color = 0)
- Row 1 = 12 blue pixels

With cel header byte 2's low nibble = 0 (transparency index 0), the encoded bytes are:

```
hex:  43 00 1C 00
```

- `0x43` → row 0: 3 pixels of color 4 (red)
- `0x00` → end of row 0; remaining 9 transparent pixels not encoded
- `0x1C` → row 1: 12 pixels of color 1 (blue)
- `0x00` → end of row 1

Total: 4 bytes for a 12-pixel-wide × 2-pixel-tall cel.

## See also

- [[entities/view]] — VIEW resource format; cel header byte 2 holds the transparency color.
- [[concepts/ega-palette]] — color index → RGB lookup.
- [[concepts/picture-compression]] — distinct compression scheme used by PICTURE resources (not RLE).
- [[sources/6-1-view]] — chapter provenance.
