# EGA Palette

Every color index in AGI — VIEW cel chunks [[concepts/rle-encoding]], PICTURE drawing opcodes [[entities/picture]], visual-screen pixels [[concepts/screen-layers]] — is a value 0..15.

> **Verification status:** **The RGB values below are not in the interpreter.** AGI 2.917's EGA driver sets BIOS mode `0Dh` and loads no palette, so the colors are whatever the hardware's default palette produces [EGA_GRAF.OVL +0x15]. The values are the de-facto IBM EGA palette as used by the andromeda decoder [gfx/palette.py:6-11]. Confirming them on screen is a runtime item, and the display and its monitor determine the exact shades. Index 6 as brown, in particular, is a monitor and adapter behavior rather than anything in AGI.

The palette is not defined in `AGI_Specifications/` chapters; the AGI documentation references "color index 0..15" without enumerating RGB values.

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
| 15 | `FF FF FF` | White | Initial fill of visual screen by `draw.pic`; on the priority screen, the band closest to the viewer |

Source for RGB values: [gfx/palette.py:6-11]. AGI-role column is cross-cut from [[concepts/screen-layers]] and [[interpreter/control-lines]]. The names of priority values are only how they look under `show.pri.screen`, which displays priority through this palette [AGI 2.917 1000:549E]. In normal play the priority nibble never reaches the display.

## Why 0..3 are control colors on the priority screen

The priority screen overloads 4-bit pixel values as **either** a depth value (4..15) **or** a control-line semantic (0..3) [5-2-PICTURE.html; [[concepts/screen-layers]]]. This page used to say the reservation of 0..3 "follows from the EGA palette". Nothing in the code supports that: the priority nibble doesn't pass through the palette in normal play. Treat the color names as labels.

## Other displays

The interpreter picks a driver overlay from `var(26)` (monitor) and `var(20)` (machine), both set by detection or a command-line switch [AGI 2.917 1000:00C4, 1000:40B2, 1000:8160]:

| `var(26)` | Switch | `var(20)` | Driver | BIOS mode | Colors in the buffer |
|---|---|---|---|---|---|
| `3` | `-e` | any | `EGA_GRAF.OVL` | `0Dh`, 320×200×16 | As given |
| `4` | `-v`, or detected on machine type 8 | any | `VG_GRAF.OVL` | `13h`, 320×200×256 | As given on type 8. See below |
| `2` | `-h`, or detected | any | `HGC_GRAF.OVL` | Hercules graphics, programmed directly | As given |
| `0`, `1` | `0` is the default; `1` is `-r` | `0` | `CGA_GRAF.OVL` | `04h`, 320×200×4 | Remapped |
| `0`, `1` | | non-zero | `JR_GRAF.OVL` | `09h` without clearing, 320×200×16 | As given |

- **`var(26)` = 0 and 1.** Both are CGA mode `04h`, then differ. `0` writes the CGA mode register directly for high-resolution graphics with color burst on, which suggests composite artifact color. `1` uses the BIOS to select a background and palette, which suggests an RGB monitor [CGA_GRAF.OVL +0xDB]. The monitor names are inferences from those register values. At runtime, `-c` wrote `1Ah` to the mode register at `3D8h`, which is 640-dot graphics with color burst enabled, and `27h` to the color register at `3D9h`, with no BIOS palette call. `-r` made two BIOS `0Bh` calls instead, background 1 and palette 0. Both copies then write each buffer nibble straight out as two 2-bit CGA pixels, high pair first [2.917 runtime: other_display_paths]. The colors a composite monitor makes of those patterns can't be shown by the harness.
- **CGA color mapping.** When `var(20)` is 0 and `var(26)` isn't 2 or 3, `0xF0`'s color goes through a table of three bytes per color at `DS:1D2C`, so the buffer holds the mapped values [AGI 2.917 1000:55BD; CGA_GRAF.OVL +0x15]. Type `0` uses the first byte. Type `1` uses the other two, one for odd rows and one for even rows, which is a dither. Each mapped value is the 4 bits of one AGI pixel's share of a CGA display byte. White maps to `0x0F` either way, so the fill's white test still works.
- **CGA view colors.** On the CGA path, every VIEW is rewritten in place when it loads, so its cels hold the same mapped colors as the buffer [AGI 2.917 1000:5857; CGA_GRAF.OVL +0x37]. Each RLE byte's color nibble and each cel's transparent color go through a 16-entry table: `DS:1D5C` for monitor 0, or a copy of `DS:1D6C` at `DS:1D7C` for monitor 1. The monitor 0 table is a permutation, so transparency survives. The monitor 1 table merges colors, so the hook sets each cel's transparent color to map to 4, a value nothing else maps to. That entry stays changed for the rest of the view, so in a later cel of the same view, pixels of an earlier cel's transparent color also map to 4. If the later cel's transparent color differs, those pixels become 4 and draw as that color. A loop with the same offset as the loop before it is skipped, so a loop shared that way is converted once. Cels shared any other way would be converted twice. Neither case arises in SQ1: none of its 238 views shares a loop with a loop that isn't next to it, shares a cel between distinct loops, or uses more than one transparent color [SQ1 data check, log 2026-11-07].
- **Hercules.** After each full picture or buffer clear, a second routine converts the whole buffer to a double-height 1-bit image through dither patterns at `DS:1D9E`, and copies come from that image [AGI 2.917 1000:63A0; HGC_GRAF.OVL +0x99, +0x126]. The conversion walks the 168 rows of the buffer, two AGI pixels at a time, from the low nibbles. Each pair gives one byte, 8 Hercules pixels, on each of two output lines 80 bytes apart, so the image is 640 pixels wide and 336 lines tall. The patterns are 8 bytes per color: 2 bytes for each of 4 row phases, picked by the row number modulo 4, one byte per output line. A pair of equal colors takes the whole pattern byte. A mixed pair takes the high nibble from the first color's pattern and the low nibble from the second's. The image goes to the second half of the Hercules allocation, whose segment is at `DS:1369` [HGC_GRAF.OVL +0x99; AGI 2.917 1000:425C].
- **Hercules driver, the rest.** Entering graphics clears all 64 KB of video memory, enables graphics and the second page through port `3BFh`, loads the 16 CRTC registers from `DS:1D8E`, waits five vertical retraces with the display off, turns it on and does a full update [HGC_GRAF.OVL +0x15, +0x236]. Entries `9740` and `9746` are the same routine, and `9749` does nothing. Text mode homes and hides the cursor and clears 25 rows of 40 columns through the BIOS [HGC_GRAF.OVL +0x69]. The copy reads the converted image, two lines per AGI row, into Hercules memory's four interleaved banks, from a row table whose first entry is 5, a 40-pixel left margin that centers the 640-pixel image on the 720-pixel screen [HGC_GRAF.OVL +0x126, +0x214]. The window fill can only draw white, for color 15, or black, for any other color [HGC_GRAF.OVL +0x186]. The driver installs its own `int 10h` handler for writing characters and scrolling, and draws text from the `HGC_FONT` file, chaining every other BIOS video call to the old handler [HGC_GRAF.OVL +0x24A].
- **Hercules objects.** `HGC_OBJS.OVL` has the same three entries as `IBM_OBJS.OVL`. Its save and restore also copy the matching bytes of the converted image, two 80-byte lines per AGI row, which sit at `+0x6900` in the buffer segment. Its cel draw applies the same priority and control rules and the same `flag(1)` result, and also writes each pixel's dither pattern into the converted image [HGC_OBJS.OVL +0x09, +0x74, +0xDF]. The dither row phase comes from a countdown of the cel's remaining rows, not from the screen row the picture conversion uses, so an object's dither can be out of step with the background behind it. **Confirmed at runtime:** the Hercules image matched the conversion rule in every byte of a picture alone, and in all but one byte with an object drawn. A solid block of color 8, whose pattern repeats every two rows, came out with every row in the opposite phase from the background's rule [2.917 runtime: other_display_paths]. The countdown counts the cel's bottom row as 1, so a row's phase is its distance from the bottom plus 1, modulo 4.
- **`toggle.monitor`.** It flips the monitor word at `DS:1128` between 0 and 1. It works only when `var(20)` is 0, `var(0)` is non-zero, and the monitor isn't 2 or 3. It then re-initializes the display and rebuilds the screen by replaying the script log [AGI 2.917 1000:7885, 1000:6755]. At runtime, on `-c` in room 1, the monitor word went from 0 to 1, the direct register writes gave way to BIOS palette calls, and the buffer was rebuilt with the other color table [2.917 runtime: toggle_monitor_on_cga]. `var(26)` is only a copy of that word, made at startup and restore, so it doesn't change here [AGI 2.917 1000:1089, 1000:265A]. Monitor 4 would flip to 5, which no routine handles.
- **VGA with machine type 0.** The mapping guard above doesn't exclude monitor 4, and the VGA driver has no mapping routine in that slot. With `-v` on a machine detected as type 0, `0xF0` would jump into its mode-setting code instead [AGI 2.917 1000:55D7; VG_GRAF.OVL +0x15]. **Confirmed at runtime:** with `-v` on machine type 0, the screen ended in BIOS text mode 1 after the first picture, and the game kept running blind [2.917 runtime: other_display_paths]. Auto-detection doesn't reach it, because it sets type 8 with monitor 4.

All five copy routines use only the low nibble of each buffer byte [EGA_GRAF.OVL +0x85; CGA_GRAF.OVL +0x1B5; JR_GRAF.OVL +0xF5; VG_GRAF.OVL +0x86; HGC_GRAF.OVL +0x99].

**Every path, at runtime.** Each driver drew SQ1's picture 1 with an object on it, and the display was decoded and compared with the buffer [2.917 runtime: ega_display_matches_buffer, other_display_paths]. EGA, VGA on type 8, PCjr and Tandy showed every AGI pixel as two display pixels of its own color, with no exceptions. The PCjr driver takes its display segment from the BIOS page-register call, page × 16 KB, rather than from `B800` [JR_GRAF.OVL +0xA7].

## Palette changes at runtime

The live EGA path never changes palette registers. Its only related call is the one choosing intensity over blinking, in both graphics and text mode [EGA_GRAF.OVL +0x1A, +0x43]. The one palette program in any driver is VGA's `shake.screen`, which inverts the DAC colors repeatedly, an even number of times per pass [VG_GRAF.OVL +0x116; AGI 2.917 1000:7968]. On EGA, `shake.screen` flips display pages instead [EGA_GRAF.OVL +0x1B8].

## Usage in code

- **VIEW cel rendering:** [gfx/view_render.py:18] does `(r, g, b) = palette[color]` per RLE chunk; transparent pixels (matching `cel.alpha`) get alpha = 0 instead of being skipped at the index lookup [gfx/view_render.py:19].
- **Visual-screen blit:** [gfx/palette.py:13-34] iterates the visual screen, expands each color index to RGBA, and doubles every pixel horizontally to produce a 320-wide surface.

## Out-of-scope variants

- **CGA / Hercules / Tandy in AGI v1.** AGI v1 (KQ1–2) used CGA natively — a genuinely different graphics generation, not audited here. The on-disk resource format doesn't change across the 2.917 displays above. See [[interpreter/overview]] §"What is AGI?" for the version summary.

## See also

- [[concepts/screen-layers]] — the buffer and the path to the display.
- [[interpreter/control-lines]] — semantics of the four control colors.
- [[interpreter/priority-bands]] — y → priority band assignment table.
- [[concepts/rle-encoding]] — VIEW cel byte chunks use these indices for color.
- [[entities/picture]] — PICTURE drawing opcodes take palette indices as color arguments.
