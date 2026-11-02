# Screen Layers

> **Verification status:** Buffer layout, initial state, enable flags, and the path to the display are read from AGI 2.917 and its driver overlays, and describe 2.917 only. The rules for how screen objects are drawn are on [[interpreter/priority-bands]] and [[interpreter/control-lines]]. Nothing about the actual picture on a monitor has been observed; see "Open items".

A rendered AGI room consists of two logical layers, the **visual screen** and the **priority screen**. They share the same `(x, y)` coordinates [5-1-PICTURE.html §GENERAL GUIDELINES].

## One buffer

> [!conflict] Two framebuffers
> The spec, `showpic.c`, and earlier versions of this page describe two parallel framebuffers. In 2.917 they are **one buffer**, in which each byte holds both layers [AGI 2.917 1000:5231, 1000:54A5].

- **Layout:** one byte per pixel, 160 bytes per row, 168 rows, top row first: 26,880 bytes. The offset of a pixel is `y * 160 + x` [AGI 2.917 1000:559E].
- **Low nibble:** visual color.
- **High nibble:** priority.
- **Location:** its own segment, allocated from DOS at startup, with the segment number at `DS:1365` [AGI 2.917 1000:4243, 1000:424C]. It's not video memory. Hercules allocates twice that, with the second half holding a converted image.

Screen-object pixels are written into this same buffer [AGI 2.917 1000:5631].

## Dimensions

*(Applies to AGI v2/v3. AGI v1 used a CGA-native display model; see [[concepts/ega-palette]] §"Out-of-scope variants".)*

Both layers are **160 × 168**. EGA displays them at 320×200, with each pixel doubled horizontally [AGI 2.917 EGA_GRAF.OVL +0x15, +0x85].

> [!conflict] Where the spare rows are
> This page said the bottom ~32 rows are reserved below `y = 167`. The display has 32 spare rows in total, and the first `configure.screen` value decides where they go. The picture's top row appears at display row `top * 8`, with `top` initially 0 until the game sets it [AGI 2.917 1000:5560, 1000:7861, DS:05DD]. For a game that keeps the status line on row 0, the picture starts at display row 8, leaving 24 rows below it.

## What each screen encodes

**Visual screen.** The image the player sees. Each pixel stores a 4-bit color index ([[concepts/ega-palette]]). On the IBM PC with CGA, the stored values are already remapped; see that page.

**Priority screen.** Invisible except through `show.pri.screen`. Each pixel stores a 4-bit value used by two distinct subsystems:

- **Priority band** (values 4..15) — the pixel's depth, from 4 (farthest back) to 15 (closest to the viewer). Values 4..14 are the eleven y-derived bands. Drives per-pixel occlusion for screen-objects, per [[interpreter/priority-bands]].
- **Control line** (values 0..3) — encodes one of four control-line semantics: barrier, conditional barrier, alarm, water/surface. See [[interpreter/control-lines]]. Cel drawing treats only 0..2 as special, and compares 3 like any other priority [AGI 2.917 1000:9DE7].

Value 15 is the band closest to the viewer: objects cannot move in front of it [5-2-PICTURE.html]. It sits outside the y-derived table, because EGO can never walk low enough to reach it [5-1-PICTURE.html]. It is in real use: SQ1 draws it in 45 of 73 pictures (15.5% of all priority pixels), and its scripts call `set.priority(n, 15)` 32 times [SQ1 data check, log 2026-11-01].

The priority nibble doesn't pass through the palette in normal play, so nothing in the code ties the reservation of 0..3 to the palette. This page used to say the reservation follows from the EGA palette. Those values merely appear as black, blue, green and cyan when `show.pri.screen` displays them. See [[concepts/ega-palette]].

## Initial state

- **At startup,** and when `toggle.monitor` re-initializes the display, every byte is set to `0x40`: color 0, priority 4 [AGI 2.917 1000:5468].
- **`draw.pic`** sets every byte to `0x4F`: color 15, priority 4 [AGI 2.917 1000:6381; 5-2-PICTURE.html §I.2.1.1 "Initially all pixels of the background are white and priority 4"].
- **`overlay.pic`** keeps what's there [AGI 2.917 1000:6379].

Neither `draw.pic` nor `overlay.pic` touches the display itself.

## Drawing-mode flags

PICTURE bytecode maintains two independent enables, each set by giving that layer a color and cleared by its disable opcode. Both start off in every picture [AGI 2.917 1000:6387]. They are a single mask with one nibble per layer [AGI 2.917 DS:135F]. A disabled layer's write value also has that nibble set to all ones, which is how it's preserved.

- **Visual** — `0xF0` enables and sets the color, `0xF1` disables.
- **Priority** — `0xF2` enables and sets the priority, `0xF3` disables.

A draw opcode writes to whichever layers are enabled. Common patterns:

- Picture only: `0xF0 <color>` then `0xF3` — visible scenery with no depth/control effect.
- Priority only: `0xF1` then `0xF2 <priority>` — invisible bands or control lines.
- Both: `0xF0 <color>` then `0xF2 <priority>` — colored scenery that also writes the band beneath it.

## How pixels reach the display

`draw.pic` draws only into the buffer. The display changes when one of these runs:

- **Full update.** One routine sends the whole buffer to the display. `show.pic` uses it, as do `show.pri.screen` and the return to graphics after text mode [AGI 2.917 1000:547E].
- **Rectangle update.** Windows and the screen-object update send a rectangle through the same driver entry [AGI 2.917 1000:5552, 1000:56FD]. The object path does nothing while `DS:120E` is 0 [AGI 2.917 1000:56A2]. `draw.pic` and `overlay.pic` clear that word and `show.pic` sets it, as does the end of the script replay [AGI 2.917 1000:4B0D, 1000:4B78, 1000:4B9D, 1000:67A5, 1000:690A]. So moving objects don't reach the display between `draw.pic` and `show.pic`.

### The driver overlay

One graphics overlay is loaded at startup to `1000:9740`, chosen from `var(26)` and `var(20)`, and it starts with seven jump entries [AGI 2.917 1000:8160, 1000:66FC]. Their meanings are consistent across the five drivers:

| Entry | Role |
|---|---|
| `1000:9740` | Enter graphics mode |
| `1000:9743` | Enter text mode: on EGA, 40-column text with the cursor hidden and homed and the screen cleared [called from AGI 2.917 1000:7621] |
| `1000:9746` | Return to graphics: enter graphics mode, then do a full update [called from AGI 2.917 1000:781C] |
| `1000:9749` | Apply a horizontal display adjustment on CGA and PCjr. Does nothing on EGA, VGA and Hercules [called from AGI 2.917 1000:5FD0] |
| `1000:974C` | Copy a buffer rectangle to the display. Takes bottom row, left column, width and height |
| `1000:974F` | Build the table of display-row addresses |
| `1000:9752` | Fill a display rectangle with a color, for window boxes |

### EGA

The EGA driver, `EGA_GRAF.OVL`, sets BIOS mode `0Dh` (320×200, 16 colors) at segment `A000` and selects intensity rather than blinking for the top color bit [EGA_GRAF.OVL +0x15]. To copy, it uses graphics controller write mode 2, with the bit mask selecting two display pixels at a time. Each buffer byte writes its low 4 bits to the planes, so the priority nibble is ignored by the hardware, and each pixel covers two display pixels. It draws rows from bottom to top [EGA_GRAF.OVL +0x85, +0x214].

Other displays are in [[concepts/ega-palette]] §"Other displays".

### `show.pri.screen`

It doesn't use a separate priority image. It swaps the two nibbles of every byte in the buffer, does a full update, waits, then swaps back and updates again [AGI 2.917 1000:7254, 1000:549E]. So what appears is priority values shown as colors, and any screen objects in the buffer appear too. See [[interpreter/command-semantics]] §"PICTURE commands".

## Composition with screen-objects

Screen-objects (ego, NPCs, props, sourced from VIEW resources) share the one buffer. Each cel pixel is compared with the priority already there: see [[interpreter/priority-bands]] §"How a cel pixel is compared" and [[interpreter/control-lines]] §"Search-downwards rule". An object's priority is set explicitly or assigned from the y table, and [[interpreter/command-semantics]] §`add.to.pic` covers the LOGIC-side composition.

`draw.pic` and `overlay.pic` take objects out of the buffer before drawing and put them back after [AGI 2.917 1000:698D, 1000:69C7].

## SCI divergence

SCI splits this two-screen model into three independent layers (visual / priority / control), eliminating the control-vs-priority overload and the search-downwards complexity. AGI's two-screen design is a memory-era artifact preserved here for fidelity.

## Open items at this page's level

- **On-screen result** — the display path above comes from reading code only. Runtime pass: capture each display type's output for one picture, including `show.pri.screen`.

## See also

- [[entities/picture]] — the PICTURE bytecode that writes both screens.
- [[concepts/picture-rendering]] — the pixel-writing operation and the algorithms using it.
- [[entities/view]] — VIEW cels composited on top of the visual screen.
- [[concepts/rle-encoding]] — VIEW cel pixel encoding.
- [[concepts/ega-palette]] — palette and non-EGA displays.
- [[interpreter/priority-bands]] — y → priority band assignment.
- [[interpreter/control-lines]] — black/blue/green/cyan color semantics on the priority screen.
- [[interpreter/command-semantics]] §`add.to.pic` — LOGIC-side composition of VIEW cels into the PICTURE buffers.
- [[sources/5-1-picture]] — chapter provenance.
