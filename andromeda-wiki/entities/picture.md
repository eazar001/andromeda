# PICTURE Resource

> **Verification status:** Audited against the AGI 2.917 binary. Citations of the form `[AGI 2.917 …]` are statically read and describe 2.917 only. `[SQ1 emulation]` means the interpreter's own PICTURE routine, taken unmodified from the decoded binary, was executed in an x86 emulator on all 73 SQ1 PICTUREs and on synthetic pictures, and compared pixel for pixel with this page's rules (log, picture audit). That run exercises the routine alone, not the whole interpreter. The prose and rules on this page reproduced its output exactly: no differing pixel in the 73 pictures or in 1,500 random synthetic ones. v3 notes are not audited, because 2.917 is v2.

The PICTURE resource encodes a room's background as a sequence of drawing opcodes rather than a raw pixel grid. A bytecode interpreter walks the stream and writes pixels into one 160×168 buffer whose bytes hold a visual colour and a priority value side by side; see [[concepts/screen-layers]] [AGI 2.917 1000:5231]. LOGIC draws a PICTURE with `$19 draw.pic` or `$1C overlay.pic`; see [[interpreter/command-semantics]] §"PICTURE commands". These LOGIC opcodes are distinct from the PICTURE bytecode below.

## File framing

A PICTURE resource sits inside a [[entities/vol-file]] container behind the standard 5-byte v2 or 7-byte v3 resource header. v3 PICTURE payloads may use [[concepts/picture-compression]] (4-bit color-code packing of `0xF0`/`0xF2` arguments); the decompressor restores the v2-style expanded stream before bytecode dispatch begins. No other compression scheme (e.g. LZW) is applied to PICTURE [3-3-Files.html §PICTURE COMPRESSION].

## Bytecode dispatch

Interpretation is sequential, byte by byte, from the resource's first payload byte [AGI 2.917 1000:63AE]. At the top level:

- `0xFF` ends the picture. Nothing checks the resource's length, so a stream without `0xFF` runs on through memory.
- `0xF0..0xFA` dispatch through an 11-entry table [AGI 2.917 DS:15CC].
- Any other byte is skipped, so bytes below `0xF0` outside a command, and `0xFB..0xFE` with whatever follows them, are ignored until the next valid opcode [AGI 2.917 1000:63B9, 1000:63BD].

Variable-length commands read arguments until they see a byte of `0xF0` or above, and that byte becomes the next opcode [AGI 2.917 1000:65FD, 1000:660E]. A partly read group is dropped, so a lone `x` before an opcode draws nothing. Fixed arguments (`0xF0`, `0xF2`, `0xF9`) are not checked: the next byte is taken whatever it is, even `0xFF` [AGI 2.917 1000:63CD, 1000:6400, 1000:645D].

Every picture starts with both layers disabled, a pen of `0` (solid circle of size 0), and nothing to write [AGI 2.917 1000:6387]. Drawing before an enable opcode changes nothing [SQ1 emulation]. State does not carry over from an earlier picture, including for `overlay.pic`.

## Opcode catalogue

| Opcode | Mnemonic | Args | Encoding | Semantics |
|--------|----------|------|----------|-----------|
| `0xF0` | Set visual color | 1 fixed byte | color index 0–15 | Sets the visual color and enables the visual layer [AGI 2.917 1000:63CD]. |
| `0xF1` | Disable visual draw | 0 | — | Later drawing leaves the visual nibble alone [AGI 2.917 1000:63EE]. |
| `0xF2` | Set priority color | 1 fixed byte | priority index 0–15 | Sets the priority and enables the priority layer [AGI 2.917 1000:6400]. |
| `0xF3` | Disable priority draw | 0 | — | Later drawing leaves the priority nibble alone [AGI 2.917 1000:6426]. |
| `0xF4` | Y-corner | variable | `x y` then `[y₁ x₁ y₂ x₂ ...]` | Plots `(x,y)`, then draws segments alternating vertical and horizontal, vertical first [AGI 2.917 1000:654B]. |
| `0xF5` | X-corner | variable | `x y` then `[x₁ y₁ x₂ y₂ ...]` | The same, horizontal first [AGI 2.917 1000:653C]. |
| `0xF6` | Absolute line | variable | `x₁ y₁` then `[x₂ y₂ ...]` | Plots the first point, then draws a polyline through the rest [AGI 2.917 1000:657F]. |
| `0xF7` | Relative line | variable | `x₀ y₀` then `[disp...]` | Polyline from `(x₀,y₀)`; each byte packs `(Δx, Δy)` as below [AGI 2.917 1000:6597]. |
| `0xF8` | Flood fill | variable | `[x y ...]` (pairs) | Flood-fills from each point [AGI 2.917 1000:65E4]. |
| `0xF9` | Set pen style | 1 fixed byte | style byte (see below) | Sets the pen for `0xFA` [AGI 2.917 1000:645D]. |
| `0xFA` | Plot with pen | variable | `[x y ...]` or `[t x y ...]` | Plots the pen at each position [AGI 2.917 1000:6438]. |
| `0xFB..0xFE` | — | — | — | Skipped along with anything up to the next valid opcode [AGI 2.917 1000:63BD]. |
| `0xFF` | End of PICTURE | — | — | Resource terminator [AGI 2.917 1000:63B3]. |

> [!conflict] `0xFB..0xFE`
> showpic.c treats these as a fatal "Unknown picture code" [showpic.c:627]. 2.917 skips them silently [AGI 2.917 1000:63BD; SQ1 emulation]. SQ1 uses none of them [SQ1 data check, picture audit].

**Color arguments are not masked.** `0xF2` shifts its byte left by 4 within 8 bits, so its high nibble is lost [AGI 2.917 1000:6401]. `0xF0` stores its whole byte, and that byte's high bits are ORed into the priority half of the value it writes [AGI 2.917 1000:63DF]. So the common description of a v2 color byte as having an "unused high nibble" holds only for values games actually use. SQ1 never passes a value above 15 to either opcode [SQ1 data check, picture audit]. A visual color such as `0x1F`, whose low nibble is 15 but whose whole byte is not, passes the flood fill's white test; what that fill does is unread.

The AGDS manual (5-2-PICTURE.html) uses alternate terminology for the same opcodes: `0xF9` is called "dot parameters" and `0xFA` is called "dot plotting" rather than "set pen style" / "plot with pen". Same bytecode, different framing — this page follows 5-1's "pen" terminology.

## Flood-fill target rule (`0xF8`)

`0xF8` decides what to do from the enable state and color, then tests one nibble of each pixel [AGI 2.917 1000:5273]:

| Enabled | No fill at all if | A pixel can be filled if | Written at each filled pixel |
|---|---|---|---|
| Visual only | visual color is 15 | its color is 15 | Color |
| Visual and priority | visual color is 15 | its color is 15. Priority is not tested | Color and priority |
| Priority only | priority is 4 | its priority is 4 | Priority |
| Neither | always | — | — |

Note the "Visual and priority" row: drawing white with priority enabled fills nothing, not even priority [AGI 2.917 1000:5289; SQ1 emulation].

Requiring priority 4 as well in the both-layers case is wrong: it leaves SQ1's title screen white instead of black and changes 13 of 73 pictures [SQ1 data check, log 2026-11-01].

> [!conflict] Priority writes during a both-screens fill (resolved)
> [5-1-PICTURE.html §0xF8] says the priority fill "not only looks for its own boundary", which reads as writing priority only where it is still 4. `showpic.c` writes priority at every filled pixel. **2.917 agrees with `showpic.c`**: the write step applies both nibbles without looking at the old priority [AGI 2.917 1000:52F4, 1000:532C]. The literal reading differs from the running routine in 2 of 73 SQ1 pictures, by 183 and 11 priority pixels, and the `showpic.c` rule differs in none [SQ1 emulation].

> [!conflict] `showpic.c`'s white test on priority-only fills (resolved)
> `showpic.c` refuses to fill whenever the last visual color was 15, even with the visual layer disabled [showpic.c:okToFill]. **2.917 looks at the visual color only when the visual layer is enabled** [AGI 2.917 1000:5282]. So `showpic.c` skips priority-only fills that 2.917 performs, which gives wrong priority in 8 of 73 SQ1 pictures (7,592 pixels), and it also lacks 2.917's refusal of priority 4 [SQ1 emulation].

Consequences: `0xF8` can't repaint non-white pixels on the visual screen, and a priority-only fill can't overwrite a priority other than 4. These constraints are why the initial colors (white, priority 4) matter: they define the fillable region. See [[concepts/picture-rendering]] §"Flood fill" for the algorithm.

## Coordinate encoding

Coordinates are 8-bit unsigned bytes, `x` before `y`:

- **X**: bytes `0xA0..0xEF` are clamped to 159 [AGI 2.917 1000:6602].
- **Y**: bytes `0xA8..0xEF` are clamped to 167 [AGI 2.917 1000:6612].
- Bytes `0xF0` and above end the command, as above.

SQ1 never relies on the clamp [SQ1 data check, picture audit]. The 160-wide frame is doubled to 320 pixels on the way to the display; see [[concepts/screen-layers]] §"How pixels reach the display".

## Relative-line displacement encoding (`0xF7`)

Each displacement byte packs both Δx and Δy as 4-bit sign-magnitude values:

```
bit:   7   6 5 4   3   2 1 0
       Sx  |Δx|    Sy  |Δy|
```

- Bit 7 (`Sx`): 0 = Δx positive, 1 = Δx negative.
- Bits 6–4 (`|Δx|`): magnitude 0..7.
- Bit 3 (`Sy`): 0 = Δy positive, 1 = Δy negative.
- Bits 2–0 (`|Δy|`): magnitude 0..7.

Example: byte `0xCC` = `1100 1100` → `Δx = −4`, `Δy = −4` [AGI 2.917 1000:65A7–1000:65D4].

Two limits apply:

- **`Δx = −7` can't be encoded.** A byte with that value is `0xF0` or above, so it ends the command [AGI 2.917 1000:65A3].
- **Going off an edge clamps at the far side.** The sum is 8-bit, and anything above 159 or 167 becomes 159 or 167. So stepping right or down past the edge stops at the edge, but stepping left of 0 or above 0 wraps to a large value and lands on the *opposite* edge, drawing a long line across the picture [AGI 2.917 1000:65BE, 1000:65D4; SQ1 emulation]. showpic.c doesn't do this. SQ1 never goes off an edge this way [SQ1 data check, picture audit].

**SQ1 check.** All 73 SQ1 PICTUREs parse and render without out-of-range drawing. SQ1 has no `0xF9` and one `0xFA` (5 plots), so pen styles and splatter are checked only on synthetic pictures [SQ1 data check, picture audit].

## Pen-style encoding (argument to `0xF9`)

```
bit:   7 6    5         4       3   2 1 0
       — —    splatter  shape   —   size
```

- Bits 7, 6, 3: stored but never tested [AGI 2.917 1000:6438, 1000:6463, 1000:64DF].
- Bit 5: `0` = solid, `1` = splatter.
- Bit 4: `0` = circle, `1` = rectangle.
- Bits 2–0: size 0..7.

> [!conflict] Pen width
> [5-1-PICTURE.html §BRUSH STYLE], as the wiki first read it, gives a footprint of `2·size + 1` pixels in both dimensions. In 2.917 it is `2·size + 1` rows tall and only **`size + 1` columns wide** in the 160-wide frame [AGI 2.917 1000:64D0–1000:64D7, 1000:651F; SQ1 emulation]. The 2:1 pixel aspect makes that look roughly square on screen. `showpic.c` has the same width.

See [[concepts/picture-rendering]] §"Brush plotting" for placement and shapes.

## Plot grouping (`0xFA`)

If the current pen is **solid**, arguments to `0xFA` are pairs `(x, y)`. If it is **splatter**, they are triples `(texture, x, y)` [AGI 2.917 1000:6438]. The pen bit is tested again for each group. A texture byte of `0xF0` or above ends the command, so the texture is in the range `0x00..0xEF`.

## Splatter texture data

2.917 contains no splatter tables. It derives the pattern from an 8-bit shift register, seeded from the texture byte; see [[concepts/picture-rendering]] §"Splatter rendering" [AGI 2.917 1000:64BF, 1000:64F5]. The spec's tables are a precomputed form of that register's output, and a decoder can use either:

```c
uint8_t texture_bits[32] = {
  0x20, 0x94, 0x02, 0x24, 0x90, 0x82, 0xa4, 0xa2,
  0x82, 0x09, 0x0a, 0x22, 0x12, 0x10, 0x42, 0x14,
  0x91, 0x4a, 0x91, 0x11, 0x08, 0x12, 0x25, 0x10,
  0x22, 0xa8, 0x14, 0x24, 0x00, 0x50, 0x24, 0x04
};

uint8_t texture_offsets[120] = {
  0x00, 0x18, 0x30, 0xc4, 0xdc, 0x65, 0xeb, 0x48,
  0x60, 0xbd, 0x89, 0x04, 0x0a, 0xf4, 0x7d, 0x6d,
  0x85, 0xb0, 0x8e, 0x95, 0x1f, 0x22, 0x0d, 0xdf,
  0x2a, 0x78, 0xd5, 0x73, 0x1c, 0xb4, 0x40, 0xa1,
  0xb9, 0x3c, 0xca, 0x58, 0x92, 0x34, 0xcc, 0xce,
  0xd7, 0x42, 0x90, 0x0f, 0x8b, 0x7f, 0x32, 0xed,
  0x5c, 0x9d, 0xc8, 0x99, 0xad, 0x4e, 0x56, 0xa6,
  0xf7, 0x68, 0xb7, 0x25, 0x82, 0x37, 0x3a, 0x51,
  0x69, 0x26, 0x38, 0x52, 0x9e, 0x9a, 0x4f, 0xa7,
  0x43, 0x10, 0x80, 0xee, 0x3d, 0x59, 0x35, 0xcf,
  0x79, 0x74, 0xb5, 0xa2, 0xb1, 0x96, 0x23, 0xe0,
  0xbe, 0x05, 0xf5, 0x6e, 0x19, 0xc5, 0x66, 0x49,
  0xf0, 0xd1, 0x54, 0xa9, 0x70, 0x4b, 0xa4, 0xe2,
  0xe6, 0xe5, 0xab, 0xe4, 0xd2, 0xaa, 0x4c, 0xe3,
  0x06, 0x6f, 0xc6, 0x4a, 0x75, 0xa3, 0x97, 0xe1
};
```

Using the tables: index `texture_offsets` with the texture byte's upper 7 bits, read `texture_bits` most significant bit first from that position, and wrap from bit 254 to bit 0.

The table has 120 entries, not the 128 that was once stated here. Textures stop at `0xEF`, so the index stops at 119.

> [!conflict] Splatter offset table (resolved)
> 5-1-PICTURE.html prose and showpic.c disagree at four positions, and both are by Lance Ewing. Generating each texture's output from the register's rule and matching it against `texture_bits` gives one offset per texture. **The 5-1 prose values match at all 120 positions; showpic.c is wrong at these four** [check against AGI 2.917 1000:64F5, picture audit]:
>
> | Index | 5-1 prose (correct) | [showpic.c:459-475] |
> |-------|-----------|---|
> | 11  | `0x04` | `0x05` |
> | 15  | `0x6d` | `0x7d` |
> | 116 | `0x75` | `0xa4` |
> | 117 | `0xa3` | `0x75` |
>
> This page used to label the last two as indices 124 and 125.

> [!conflict] The "wrap at 255" bug
> 5-1 calls the wrap at 255 rather than 256 "possibly a bug in the picture drawing code", and showpic.c implements it as `if (bitPos == 0xff) bitPos = 0;`. It is not a bug and 2.917 has no such wrap. The register has a period of exactly 255, so any table holding its output repeats every 255 bits [AGI 2.917 1000:64F5; picture audit].

## Screen initialization

`draw.pic` first fills the whole buffer so that every pixel is color 15, priority 4; `overlay.pic` doesn't [AGI 2.917 1000:6381, 1000:6379; 5-1-PICTURE.html §IMPLEMENTING ALL THIS].

## Version differences

Not audited. In AGI v2, `0xF0` and `0xF2` consume a full byte for the color argument. In AGI v3 the color is packed into 4 bits per [[concepts/picture-compression]], shifting subsequent bytes; the decompressor canonicalizes back to the v2 form before opcode dispatch, so the catalogue above applies uniformly. The 2-8 fingerprint note about v3 4-bit packing corroborates this [[sources/2-8-interpreter]].

## Implementation guidance

To match 2.917 pixel for pixel, a decoder needs:

1. The integer line rule, including 8-bit overflow on very long diagonals — see [[concepts/picture-rendering]] §"Line drawing".
2. The fill table above.
3. The coordinate clamps and the wrap in `0xF7`.
4. The pen masks, placement, and right-edge overrun — see [[concepts/picture-rendering]] §"Brush plotting".
5. The splatter register or the tables above.

## Reference implementation

Lance Ewing's [`AGI_Specifications/Code/showpic.c`](../../AGI_Specifications/Code/showpic.c) is a working Allegro-based PICTURE viewer (650 lines), useful for reading but **not a byte-exact target**. It differs from 2.917 in:

- the fill's white test, which changes 8 of 73 SQ1 pictures;
- pen placement near the picture's edges;
- four splatter offsets;
- very long diagonal lines, relative lines off an edge, coordinate clamping, and `0xFB..0xFE`.

Its visual layer matched in all 73 SQ1 pictures, and with the fill test corrected it matched in full, priority included [SQ1 emulation].

For v3 → v2 transcoding, see [`AGI_Specifications/Code/picv3-v2.c`](../../AGI_Specifications/Code/picv3-v2.c), referenced from [[concepts/picture-compression]]. Not audited.

## See also

- [[concepts/screen-layers]] — the combined buffer and how pixels reach the display.
- [[concepts/picture-rendering]] — pixel-level algorithms.
- [[interpreter/control-lines]] — color semantics for control-line pixels written by `0xF2`-mode drawing.
- [[interpreter/priority-bands]] — y → priority band assignment that drives per-pixel occlusion against the priority screen this resource writes.
- [[concepts/picture-compression]] — v3 PICTURE-only color-packing scheme.
- [[sources/5-1-picture]] — chapter provenance.
- [[sources/agi-2917-binary]] — routine map.
