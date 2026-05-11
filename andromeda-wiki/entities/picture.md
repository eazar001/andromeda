# PICTURE Resource

> **Verification status:** Most byte-level claims on this page are corroborated by Lance Ewing's reference PICTURE decoder at [`AGI_Specifications/Code/showpic.c`](../../AGI_Specifications/Code/showpic.c) (referenced by the 5-3 "Sample Code" chapter). Per-claim citations distinguish code-verified claims from claims that remain `(agidev, unverified)`. Note that showpic.c is also agidev-corpus material (same source archive as the prose chapters); ScummVM cross-check is still the path to fully-external validation.

The PICTURE resource encodes a single room's background imagery as a sequence of drawing opcodes rather than a raw pixel grid. A bytecode interpreter walks the stream and writes pixels into two parallel framebuffers — the **visual screen** (what the player sees) and the **priority screen** (depth + control-line layer) — both in 160×168 logical coordinates per [[concepts/screen-layers]] [5-1-PICTURE.html §GENERAL GUIDELINES]. PICTURE composition is invoked from LOGIC via `$7A add.to.pic` / `$7B add.to.pic.v` (see [[interpreter/commands]] and [[interpreter/command-semantics]] §`add.to.pic`); the LOGIC opcodes are distinct from the PICTURE bytecode opcodes documented below.

## File framing

A PICTURE resource sits inside a [[entities/vol-file]] container behind the standard 5-byte v2 or 7-byte v3 resource header. v3 PICTURE payloads may use [[concepts/picture-compression]] (4-bit color-code packing of `0xF0`/`0xF2` arguments); the decompressor restores the v2-style expanded stream before bytecode dispatch begins. No other compression scheme (e.g. LZW) is applied to PICTURE [3-3-Files.html §PICTURE COMPRESSION].

## Bytecode dispatch

Interpretation is sequential, byte by byte. Drawing state (current visual color, current priority color, picture-draw-enabled, priority-draw-enabled, pen style) persists across opcodes. The stream is a sequence of commands where:

- Each command begins with an opcode byte in the range `0xF0..0xFF`.
- Bytes with values `< 0xF0` are arguments to the current opcode.
- A new opcode byte terminates the previous opcode's argument list (relevant for variable-length opcodes like `0xF6`, `0xF7`, `0xF8`, `0xFA`).
- `0xFF` terminates the resource.

## Opcode catalogue

| Opcode | Mnemonic | Args | Encoding | Semantics |
|--------|----------|------|----------|-----------|
| `0xF0` | Set visual color | 1 fixed byte | color index 0–15 | Sets current visual color and enables picture-draw. |
| `0xF1` | Disable visual draw | 0 | — | Subsequent drawing opcodes do not write to the visual screen. |
| `0xF2` | Set priority color | 1 fixed byte | priority index 0–15 | Sets current priority color and enables priority-draw. |
| `0xF3` | Disable priority draw | 0 | — | Subsequent drawing opcodes do not write to the priority screen. |
| `0xF4` | Y-corner | variable | `x y` then `[y₁ x₁ y₂ x₂ ...]` | Corner pattern starting at `(x,y)`; first axis changed is **Y**. Alternates Y, X, Y, X… until next opcode. |
| `0xF5` | X-corner | variable | `x y` then `[x₁ y₁ x₂ y₂ ...]` | Corner pattern starting at `(x,y)`; first axis changed is **X**. Alternates X, Y, X, Y… until next opcode. |
| `0xF6` | Absolute line | variable | `x₁ y₁` then `[x₂ y₂ ...]` | Polyline through absolute coordinates. Must have an even number of bytes after the initial pair. |
| `0xF7` | Relative line | variable | `x₀ y₀` then `[disp...]` | Polyline starting at absolute `(x₀,y₀)`, each subsequent byte encodes `(Δx, Δy)` per the sign-magnitude layout below. |
| `0xF8` | Flood fill | variable | `[x y ...]` (pairs) | Flood-fill at each `(x,y)`. Boundary rules and layer targeting in [[interpreter/control-lines]]. |
| `0xF9` | Set pen style | 1 fixed byte | style byte (see below) | Configures pen for subsequent `0xFA` plots. |
| `0xFA` | Plot with pen | variable | `[x y ...]` or `[t x y ...]` | Plot the pen at each position; argument grouping depends on pen splatter bit (see below). |
| `0xFB..0xFE` | — | — | — | Reserved / unused. Code-verified against [showpic.c:627] — switch default prints "Unknown picture code"; no implementation. |
| `0xFF` | End of PICTURE | — | — | Resource terminator. |

The corner opcodes (`0xF4`, `0xF5`) draw axis-aligned segments alternating between vertical and horizontal — equivalent to a polyline constrained so successive segments are perpendicular.

The AGDS manual (5-2-PICTURE.html) uses alternate terminology for the same opcodes: `0xF9` is called "dot parameters" and `0xFA` is called "dot plotting" rather than "set pen style" / "plot with pen". Same bytecode, different framing — this page follows 5-1's "pen" terminology.

## Flood-fill target rule (`0xF8`)

`0xF8` chooses what to fill based on the current draw-mode flags ([[concepts/screen-layers]] §"Drawing-mode flags") [5-2-PICTURE.html §I.2.1.7]:

- **Visual-draw enabled, color ≠ 15 (white):** Fill the closed white-pixel region containing the argument point on the visual screen. The fill stops at any non-white pixel.
- **Visual-draw disabled (cancelled):** Fill the closed priority-4 region containing the argument point on the priority screen. The fill stops at any pixel whose priority is not 4.
- **Both screens enabled:** Fill respects boundaries on both layers simultaneously.

Consequences: it is impossible to repaint non-white pixels on the visual screen via `0xF8`, and impossible to overwrite a priority value other than 4. These constraints are why the screen-init colors (white visual, red priority-4) are foundational — they define the "fillable" region for every subsequent `0xF8` call.

## Coordinate encoding

Coordinates are 8-bit unsigned bytes:

- **X**: 0..159 (left to right in the 160-wide logical frame; the visible screen is doubled to 320 pixels horizontally at render time).
- **Y**: 0..167 (top to bottom in the 168-tall logical frame, consistent with the y-bands in [[interpreter/priority-bands]]).

Within an opcode's argument run, `x` precedes `y` for absolute coordinates. Code-verified against [showpic.c:113-114] (x doubled at blit time; logical 160-wide).

## Relative-line displacement encoding (`0xF7`)

Each displacement byte after the initial absolute `(x₀, y₀)` packs both Δx and Δy as 4-bit sign-magnitude values:

```
bit:   7   6 5 4   3   2 1 0
       Sx  |Δx|    Sy  |Δy|
```

- Bit 7 (`Sx`): 0 = Δx positive, 1 = Δx negative.
- Bits 6–4 (`|Δx|`): magnitude 0..7.
- Bit 3 (`Sy`): 0 = Δy positive, 1 = Δy negative.
- Bits 2–0 (`|Δy|`): magnitude 0..7.

So each displacement spans `(−7..+7, −7..+7)`. Example: byte `0xCC` = `1100 1100` → `Δx = −4`, `Δy = −4`. Code-verified against [showpic.c:369-372] (sign extracted via `disp & 0x80` / `disp & 0x08`; magnitude via `disp & 0x70 >> 4` / `disp & 0x07`).

## Pen-style encoding (argument to `0xF9`)

```
bit:   7 6    5         4       3   2 1 0
       — —    splatter  shape   —   size
```

- Bits 7,6,3: unused.
- Bit 5: `0` = solid, `1` = splatter.
- Bit 4: `0` = circle, `1` = rectangle.
- Bits 2–0: size 0..7. The brush's visual extent is `(2·size + 1)` pixels in both dimensions [5-1-PICTURE.html §BRUSH STYLE].

## Plot grouping (`0xFA`)

If the current pen is **solid** (bit 5 of the style byte = 0), arguments to `0xFA` are coordinate pairs `(x, y)`. If the pen is **splatter** (bit 5 = 1), arguments are triples `(texture, x, y)` where `texture` selects a 256-bit splatter pattern from a fixed table indexed via a 128-entry offset array (see below).

## Splatter texture data

For splatter mode, the renderer maintains a 256-bit pattern source and a 128-entry start-offset table. Each splatter plot consumes a starting bit position from the offset table (keyed by the texture argument's upper 7 bits; bit 0 is unused) and reads consecutive bits of the pattern to mask the brush footprint [5-1-PICTURE.html §TEXTURE DATA]:

```c
uint8_t texture_bits[32] = {
  0x20, 0x94, 0x02, 0x24, 0x90, 0x82, 0xa4, 0xa2,
  0x82, 0x09, 0x0a, 0x22, 0x12, 0x10, 0x42, 0x14,
  0x91, 0x4a, 0x91, 0x11, 0x08, 0x12, 0x25, 0x10,
  0x22, 0xa8, 0x14, 0x24, 0x00, 0x50, 0x24, 0x04
};

uint16_t texture_offsets[128] = {
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

The chapter notes that bit-position wrap is at **255 rather than 256**, "possibly a bug in the picture drawing code" — implementations must replicate this off-by-one to match Sierra output. **Code-verified** against [showpic.c:428-429]: `if (bitPos == 0xff) bitPos = 0;` — the wrap-at-255 is real and intentional-or-not, must be replicated.

> [!conflict]
> **Splatter offset table: 5-1-PICTURE.html prose vs. showpic.c reference implementation disagree at four positions.** Both sources are authored by Lance Ewing.
>
> | Index | 5-1 prose (current wiki) | [showpic.c:459-475] | Diff type |
> |-------|-----------------|---|---|
> | 11  | `0x04` | `0x05` | 1-bit |
> | 15  | `0x6d` | `0x7d` | 1-bit |
> | 124 | `0x75` | `0xa4` | unrelated |
> | 125 | `0xa3` | `0x75` | unrelated |
>
> The wiki retains the 5-1 prose values pending ScummVM cross-check (post-Phase-B). Either reading produces a working decoder for *most* games; whether any shipped game exercises a splatter pattern that hits one of the four discrepant indices is unknown. If reproducing Sierra output pixel-for-pixel matters, plan to fingerprint both tables against `engines/agi/picture.cpp` in ScummVM before committing to one.

## Screen initialization

When PICTURE drawing begins, the visual screen initializes to white (color 15) and the priority screen initializes to red (priority 4 — the topmost band) [5-1-PICTURE.html §IMPLEMENTING ALL THIS]. Fill-boundary correctness depends on this initial state; see [[interpreter/control-lines]] §"Flood fill" for the rules.

## Version differences

In AGI v2, `0xF0` and `0xF2` consume a full byte for the color argument (high nibble unused). In AGI v3 the color is packed into 4 bits per [[concepts/picture-compression]], shifting subsequent bytes; the decompressor canonicalizes back to the v2 form before opcode dispatch, so the catalogue above applies uniformly. The 2-8 fingerprint note about v3 4-bit packing corroborates this [[sources/2-8-interpreter]].

## Implementation guidance

A faithful decoder needs four things to match Sierra output pixel-for-pixel:

1. The exact line-drawing rounding rule (Sierra's Bresenham variant — see [[concepts/picture-rendering]] §"Line drawing").
2. Flood-fill boundary tests that respect cross-screen masking when both picture-draw and priority-draw are enabled — see [[concepts/picture-rendering]] §"Flood fill".
3. Precomputed brush bitmaps for every `(shape, size)` combination matching the diagrams in [5-1-PICTURE.html §BRUSH STYLE].
4. The wrap-at-255 quirk of splatter texture indexing — see [[concepts/picture-rendering]] §"Splatter rendering".

## Reference implementation

Lance Ewing's [`AGI_Specifications/Code/showpic.c`](../../AGI_Specifications/Code/showpic.c) is a working Allegro-based PICTURE viewer (650 lines) that exercises every claim on this page. Key sections:

- **Opcode dispatch** — lines 610-628 (switch on opcode byte).
- **Line drawing** — lines 191-231 (additive fixed-point arithmetic + direction-sensitive rounding).
- **Flood fill** — lines 249-293 (BFS with a 4000-entry queue; boundary tests at lines 237-244).
- **Pen plotting** — lines 305-340 (circle/rectangle brush shapes; size = `2·n + 1` pixels).
- **Splatter** — lines 425-478 (texture table + offset lookup + wrap-at-255).

For v3 → v2 transcoding (the decompression that precedes opcode dispatch on v3 PICTUREs), see [`AGI_Specifications/Code/picv3-v2.c`](../../AGI_Specifications/Code/picv3-v2.c) — a 67-line two-state machine (NORMAL ↔ ALTERNATE mode) referenced from [[concepts/picture-compression]].

## See also

- [[concepts/screen-layers]] — visual / priority dual-screen model and per-screen init colors.
- [[interpreter/control-lines]] — color semantics for control-line pixels written by `0xF2`-mode drawing.
- [[interpreter/priority-bands]] — y → priority band assignment that drives per-pixel occlusion against the priority screen this resource writes.
- [[concepts/picture-compression]] — v3 PICTURE-only color-packing scheme.
- [[sources/5-1-picture]] — chapter provenance.
