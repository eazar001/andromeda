# PICTURE Rendering Algorithms

> **Verification status:** Audited against AGI 2.917. Everything here is read from the binary and describes 2.917 only. `[SQ1 emulation]` means the interpreter's own PICTURE routine was executed in an x86 emulator and compared with these rules: no differing pixel across all 73 SQ1 PICTUREs, 1,500 random synthetic pictures, 600 noisy fills, 2,000 random lines, 1,920 solid plots and 1,920 splatter plots. See [[entities/picture]] for the bytecode.

> [!conflict] `showpic.c` as the target (resolved)
> This page used to call `showpic.c` "the source of truth" and the byte-exact target. It is neither. Its fill test gives wrong priority in 8 of 73 SQ1 pictures, and its algorithms differ in the ways noted below. The target is the rules on this page.

## Writing a pixel

All drawing goes through one operation on one byte of the buffer [AGI 2.917 1000:5231]. The buffer byte holds priority in its high nibble and color in its low nibble ([[concepts/screen-layers]]). The operation is a mask: nibbles of enabled layers are replaced, and nibbles of disabled layers are kept. With both layers disabled nothing changes.

There is no priority arbitration during PICTURE rendering. A later draw simply overwrites earlier pixels.

The write values are kept separately for odd and even rows [AGI 2.917 1000:525B]. On EGA and most other displays the two are the same. They differ only for the dithered CGA colors; see [[concepts/ega-palette]] §"Other displays".

There's no bounds check at this level. Coordinates are clamped when read, but the pen can pass the right edge, as described below.

## Line drawing

Each segment starts at the current position, the last point drawn [AGI 2.917 1000:661A]:

- **Horizontal or vertical** segments are filled directly, endpoint to endpoint, including both ends. The position then moves to the end [AGI 2.917 1000:51A7, 1000:51E3].
- **Anything else** steps along the longer axis, using integer error terms rather than floating point. Call the larger of `|Δx|` and `|Δy|` the major length:
  - The error for the shorter axis starts at half the major length, rounded down. The error for the longer axis starts at 0.
  - Each of the major-length steps adds that axis's delta to each error. When an error reaches the major length, subtract the major length and move one pixel along that axis.
  - After both updates, plot the pixel. The start pixel is not plotted again.
  - When `|Δx| = |Δy|` both errors behave alike, so the choice of major axis doesn't matter.
  - The direction doesn't change the rounding, except that it mirrors the movement [AGI 2.917 1000:665B–1000:66AD].

The error terms are **8-bit**. If the major and minor lengths sum to more than 255, an addition can overflow and lose a step, so the line misses its endpoint [AGI 2.917 1000:667A, 1000:668A]. In a synthetic check, 278 of 293 such lines missed. Examples: a line by `(+104, +160)` ends at `(+45, +160)`, and one by `(+90, +167)` ends at `(+88, +167)`. The next segment starts from where the line really ended, because the position is the last pixel plotted rather than the requested endpoint [SQ1 emulation]. Only long diagonals can do this, since the major length is at most 167. No SQ1 diagonal comes near: none has a sum above 200 [SQ1 data check, picture audit].

> [!conflict] Line algorithm
> This page, following `showpic.c`, said the line "uses additive fixed-point arithmetic rather than classical Bresenham", with direction-sensitive rounding at thresholds of `0.501` and `0.499` [showpic.c:191-231]. 2.917 uses the integer method above. The two give the same pixels: all 97,292 start-to-end shapes checked in four directions with a sum of at most 255 had no differences [picture audit]. The rounding thresholds are therefore a way to reproduce the integer rule rather than something Sierra's code does, and only the overflow case tells them apart.

## Flood fill

Which pixels can be filled depends on the enable state; see the table in [[entities/picture]] §"Flood-fill target rule (`0xF8`)". The seed must itself qualify, or nothing happens [AGI 2.917 1000:52A5].

**Result.** The filled set is the 4-connected region of qualifying pixels containing the seed, limited to the 160×168 frame. That equals a plain 4-neighbor fill in every comparison run, including 600 fills through random noise [SQ1 emulation]. Filling writes a value that no longer qualifies, so the fill always terminates, except possibly for the unmasked color case in [[entities/picture]] §"Opcode catalogue".

**Mechanism.** It's a span fill rather than a pixel-at-a-time search [AGI 2.917 1000:52B6–1000:545C]. It fills left and right along a row from the current point, then moves up or down a row, walking along the span and looking for qualifying pixels. Saved work is pushed onto the machine stack, 8 bytes per record.

**Order doesn't matter.** Fill order can't be observed, because all of it happens inside one call and nothing reaches the display until a later `show.pic`.

**Stack depth.** Nothing bounds the depth of the records. The game stack is 2,560 bytes, and the timer interrupt checks a guard word at its low end and ends the game with "Stack blown." if the word has changed [AGI 2.917 1000:0086, 1000:00A8, 1000:84A2, 1000:84C1]. The deepest SQ1 picture uses 1,292 bytes from the routine's entry. Synthetic noise pictures went past 2,560 [SQ1 emulation]. A faithful fill needs no stack limit unless reproducing this failure matters.

> [!conflict] Fill algorithm
> This page, following `showpic.c`, described a breadth-first search over a 4,000-entry circular queue, sized "for the largest fillable region", and warned that games might rely on the BFS order "for animated water". 2.917 has no queue and no BFS, and the order can't be seen.

## Brush plotting

`0xFA` plots the pen at each argument coordinate [AGI 2.917 1000:6463]. With `size` from the pen style byte:

**Placement.** Left column `x0 = (2x − size) / 2` using integer division, after limiting `2x − size` to the range `0..(320 − 2·size)`. Top row `y0 = y − size`, limited to `0..(167 − 2·size)`.

**Footprint.** `size + 1` columns by `2·size + 1` rows. The last column can land on `x = 160`: for rectangles of size 2 and above plotted near `x = 159`, that writes the pixel in column 0 of the next row, because the buffer is simply linear [AGI 2.917 1000:6490; SQ1 emulation]. At the bottom row, the overrun writes past the end of the buffer [SQ1 emulation]. SQ1 never plots a pen there.

**Shape.** A rectangle draws every cell. A circle draws the cells set in a mask, with one 16-bit word per row, using every second bit from the top [AGI 2.917 DS:160F, DS:15EF, 1000:64E7]. In the masks below, `#` is a drawn cell:

| Size | Mask, rows top to bottom |
|---|---|
| 0 | `#` |
| 1 | `##` `##` `##` |
| 2 | `.#.` `###` `###` `###` `.#.` |
| 3 | `.##.` `.##.` `####` `####` `####` `.##.` `.##.` |

Sizes 4 to 7 follow in the table at `DS:160F`. The mask contents match `showpic.c`'s `circles` table in all eight sizes [picture audit].

> [!conflict] Brush shape claims
> This page said size 1 is "a 3×3 plus-sign" and masks are `(2·size + 1) × (2·size + 1)`. Size 1 is a 2×3 block, and masks are `size + 1` wide.

`showpic.c` agrees on interior plots but clamps differently near the edges: for example it moves a size 0 pen at `x = 0` to `x = 1`. All of its differences in a sweep of every `x` were close to the left and right edges or in the rows at the top and bottom [picture audit]. 2.917's rule above is the correct one.

## Splatter rendering

When the pen style has bit 5 set, the plot uses a shift register rather than a table [AGI 2.917 1000:64BF, 1000:64F5]:

1. At each plot, start the 8-bit register at the texture byte with its low bit forced to 1. So the bottom bit of the texture is ignored, which is the spec's "upper 7 bits".
2. For each cell of the footprint in row order, left to right, first apply the shape test. Cells that fail it do not advance the register.
3. For a cell that passes, shift the register right by one bit. If the bit shifted out was 1, XOR the register with `0xB8`.
4. Draw the cell only if the register's bit 0 is 0 and bit 1 is 1.

The register has a period of 255. The spec's two tables are a precomputed form of this; see [[entities/picture]] §"Splatter texture data", which also settles the table conflict and the "wrap at 255" claim.

Splatter was checked only on synthetic pictures, since SQ1 doesn't use it [SQ1 data check, picture audit].

## Implementation status

Not implemented in andromeda's `resource/` (no PICTURE decoder yet).

## See also

- [[entities/picture]] — bytecode-level opcode dispatch and per-opcode byte format.
- [[concepts/screen-layers]] — the buffer these algorithms write into.
- [[interpreter/control-lines]] — control-line semantics, including flood-fill interaction with priorities 0..3.
- [[sources/5-3-picture]] — chapter provenance for the reference C code.
