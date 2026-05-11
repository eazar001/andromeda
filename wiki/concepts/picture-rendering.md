# PICTURE Rendering Algorithms

> **Verification status:** Every algorithm on this page is **code-verified** against Lance Ewing's reference PICTURE decoder at [`AGI_Specifications/Code/showpic.c`](../../AGI_Specifications/Code/showpic.c) (650 lines, Allegro-based, vendored as part of the 5-3 "Sample Code" chapter). Where 5-1's prose punted to "chapter pseudocode is the source of truth", showpic.c IS the source of truth.

This page documents the *algorithms* the PICTURE bytecode opcodes invoke at the pixel level — line rasterization, flood fill, brush plotting, splatter masking. The bytecode-level dispatch and per-opcode byte format are in [[entities/picture]]; this page picks up where opcode interpretation ends and pixel writes begin.

## Line drawing

`0xF6` (absolute line) and `0xF7` (relative line) both reduce to a sequence of two-endpoint line segments, drawn into whichever screen(s) are currently draw-enabled per [[concepts/screen-layers]].

The line-drawing function uses additive fixed-point arithmetic rather than classical Bresenham [showpic.c:191-231]:

1. Compute `height = y1 − y0` and `width = x1 − x0`.
2. If `|height| > |width|`, the line is "tall" — step in y, derive x. Increment per step: `addX = width / |height|` (fractional, accumulated).
3. Else the line is "wide" — step in x, derive y. Increment per step: `addY = height / |width|` (fractional, accumulated).
4. At each step, the accumulated subpixel position is rounded to an integer pixel coordinate via a direction-sensitive `round()` [showpic.c:191-196]: ambiguous half-pixel positions are rounded *toward* the line direction using thresholds `0.501` (forward) and `0.499` (backward). This matters because flood-fill correctness depends on every line being closed at the pixel level — a single off-by-one rounding error opens a one-pixel gap and the fill leaks.

Implementation note: the spec characterizes this as a "Sierra Bresenham variant"; showpic.c shows it isn't classical Bresenham at all — it's accumulated subpixel arithmetic with direction-aware rounding. The distinction matters for any reimplementation hoping to be pixel-exact.

## Flood fill

`0xF8` (flood fill) is implemented as a breadth-first search with a fixed-size circular queue [showpic.c:249-293]:

- **Queue size**: 4000 entries (hard-coded). Each entry is an `(x, y)` pair. The queue wraps modulo 4000.
- **Algorithm**: starting at the argument `(x, y)`, push the seed onto the queue. While the queue is non-empty: pop an entry, test whether the pixel is "fillable" (see boundary rule below), if so write the current fill color and push the four cardinal neighbors. Stop when the queue is empty.
- **Boundary rule** [showpic.c:237-244] — determined by which draw layer is enabled, per [[entities/picture]] §"Flood-fill target rule (`0xF8`)":
  - Visual-draw enabled, color ≠ 15: fillable iff visual-screen pixel == 15 (white).
  - Visual-draw disabled: fillable iff priority-screen pixel == 4 (red, the init color).
  - Both: both conditions must hold.

The 4000-entry queue is sized for the largest fillable region in any shipped game; running out is treated as a fatal error in showpic.c (queue-overflow does not gracefully degrade). A defensive reimplementation could grow dynamically or use a stack-based DFS, but neither matches Sierra output bit-for-bit if the games depend on the BFS order producing a specific fill pattern (e.g., for animated water).

## Brush plotting

`0xFA` (plot with pen) renders the current pen at each argument coordinate. The pen has four orthogonal properties packed into the byte argument of `0xF9`: shape (circle/rectangle), splatter mode (on/off), size (0..7). See [[entities/picture]] §"Pen-style encoding".

**Shape and size** [showpic.c:305-340]:

- **Circle**: a precomputed `(2·size + 1) × (2·size + 1)` bitmap mask shaped as a filled circle of radius `size`. Plotted by AND-ing the mask with the brush footprint.
- **Rectangle**: a precomputed `(2·size + 1) × (2·size + 1)` square mask, fully set.

The per-`(shape, size)` masks are hard-coded in showpic.c, not algorithmically computed at render time. A reimplementation could compute them, but bit-exact matching to Sierra output requires using showpic.c's exact masks (which encode small idiosyncrasies in the circle approximations at small sizes — e.g., size 0 is a single pixel, size 1 is a 3×3 plus-sign, etc.).

**Splatter mode** is described in the next section.

## Splatter rendering

When the pen-style byte has bit 5 set, `0xFA` arguments become triples `(texture, x, y)` and each brush plot is masked by a bit pattern drawn from a global 256-bit splatter source.

**Texture argument decoding** [showpic.c:477-478]:
- Take the texture byte's upper 7 bits: `patNum = (texture >> 1) & 0x7f` (range 0..127).
- Look up `bitPos = splatterStart[patNum]` — the starting bit position in the 256-bit pattern source.

**Pattern source and offset table**: see [[entities/picture]] §"Splatter texture data" for the byte arrays. Note the open `> [!conflict]` callout on that section regarding the four-position discrepancy between 5-1 prose and showpic.c — affects which offsets are used for `patNum ∈ {11, 15, 124, 125}`.

**Per-pixel masking** [showpic.c:425-450]: for each pixel in the brush footprint, read bit `bitPos` of the 256-bit pattern; if 1, write the pen color, else skip; advance `bitPos`.

**Wrap-at-255 quirk** [showpic.c:428-429]:

```c
if (bitPos == 0xff) bitPos = 0;
```

This wraps at 255, not 256 — bit 255 of the pattern is never consumed before the wrap, and bit 0 is consumed twice when traversing past the boundary. 5-1 speculates this is a bug in the original Sierra interpreter and notes that reproducing pixel-exact Sierra output requires replicating it. showpic.c does replicate it. ScummVM behavior unverified at time of writing.

## Color writes

When a draw operation determines that pixel `(x, y)` should receive color `c`:

- If visual-draw is enabled, write `c` to the visual screen at `(x, y)`. The x-coordinate is doubled at blit time (write to columns `2x` and `2x + 1`) per [[concepts/screen-layers]] [showpic.c:113-114].
- If priority-draw is enabled, write the current priority color to the priority screen at `(x, y)`.

There is no priority arbitration during PICTURE rendering — a later draw simply overwrites earlier pixels. Priority arbitration applies only at screen-object composition time, which is a runtime LOGIC-VM concern and not part of PICTURE rendering itself.

## Implementation status

Not implemented in andromeda's `resource/` (no PICTURE decoder yet). Whenever one lands, [`AGI_Specifications/Code/showpic.c`](../../AGI_Specifications/Code/showpic.c) is the byte-exact target — every algorithm above must produce identical pixels.

## See also

- [[entities/picture]] — bytecode-level opcode dispatch and per-opcode byte format.
- [[concepts/screen-layers]] — visual / priority dual-screen model that these algorithms write into.
- [[interpreter/control-lines]] — control-line semantics, including flood-fill interaction with priorities 0..3.
- [[sources/5-3-picture]] — chapter provenance and the inline-citation strategy for reference C code.
