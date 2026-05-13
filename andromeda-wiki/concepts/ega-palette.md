# EGA Palette

AGI uses the standard 16-color IBM EGA palette. Every color index in the AGI engine — VIEW cel chunks [[concepts/rle-encoding]], PICTURE drawing opcodes [[entities/picture]], visual-screen pixels [[concepts/screen-layers]], and control-line semantics on the priority screen — refers to one of these 16 RGB values [gfx/palette.py:6-11].

The palette itself is not defined in `AGI_Specifications/` chapters; the AGI documentation references "color index 0..15" without enumerating RGB values, because EGA was the lingua franca of mid-1980s PC graphics. The values below are the de-facto IBM EGA palette as used by the andromeda decoder.

## Palette table

| Index | RGB (hex) | Common name | AGI role |
|---|---|---|---|
| 0 | `00 00 00` | Black | Control color: barrier (priority screen) |
| 1 | `00 00 AA` | Blue | Control color: conditional barrier (priority screen) |
| 2 | `00 AA 00` | Green | Control color: alarm trigger (priority screen) |
| 3 | `00 AA AA` | Cyan | Control color: water / surface (priority screen) |
| 4 | `AA 00 00` | Red | Priority band 4 (also: initial fill of priority screen) |
| 5 | `AA 00 AA` | Magenta | Priority band 5 |
| 6 | `AA 55 00` | Brown | Priority band 6 |
| 7 | `AA AA AA` | Light gray | Priority band 7 |
| 8 | `55 55 55` | Dark gray | Priority band 8 |
| 9 | `55 55 FF` | Light blue | Priority band 9 |
| 10 | `55 FF 55` | Light green | Priority band 10 |
| 11 | `55 FF FF` | Light cyan | Priority band 11 |
| 12 | `FF 55 55` | Light red | Priority band 12 |
| 13 | `FF 55 FF` | Light magenta | Priority band 13 |
| 14 | `FF FF 55` | Yellow | Priority band 14 |
| 15 | `FF FF FF` | White | Initial fill of visual screen; **unused on priority screen** |

Source for RGB values: [gfx/palette.py:6-11]. AGI-role column is cross-cut from [[concepts/screen-layers]] and [[interpreter/control-lines]].

## Why 0..3 are control colors on the priority screen

The priority screen overloads 4-bit pixel values as **either** a priority-band index (4..14) **or** a control-line semantic (0..3), with 15 unused [5-1-PICTURE.html §GENERAL GUIDELINES; [[concepts/screen-layers]]]. The reservation of 0..3 for control rather than depth follows from the EGA palette itself: black/blue/green/cyan have the lowest palette indices, so a single 4-bit value can encode either a control color or a depth band without collision (and the search-downwards rule at [[interpreter/control-lines]] recovers the underlying band when a pixel is a control color).

## Usage in code

- **VIEW cel rendering:** [gfx/view_render.py:18] does `(r, g, b) = palette[color]` per RLE chunk; transparent pixels (matching `cel.alpha`) get alpha = 0 instead of being skipped at the index lookup [gfx/view_render.py:19].
- **Visual-screen blit:** [gfx/palette.py:13-34] iterates the visual screen, expands each color index to RGBA, and doubles every pixel horizontally to produce a 320-wide surface.

## Out-of-scope variants

- **EGA hardware palette remapping.** Real EGA hardware allowed remapping the 16 displayed colors to any subset of a 64-color master palette. AGI did not exercise this; the 16 colors above are the fixed render palette. Not relevant to format decoding.
- **CGA / Hercules / Tandy fallback palettes.** Some AGI builds shipped renderer paths for older hardware that mapped these 16 indices to fewer-color outputs. The on-disk format is unchanged; only the runtime display path differs. Not relevant to this wiki.

## See also

- [[concepts/screen-layers]] — visual / priority dual-screen model; why indices 0..3 are control, 4..14 are bands.
- [[interpreter/control-lines]] — semantics of the four control colors.
- [[interpreter/priority-bands]] — y → priority band assignment table.
- [[concepts/rle-encoding]] — VIEW cel byte chunks use these indices for color.
- [[entities/picture]] — PICTURE drawing opcodes take palette indices as color arguments.
