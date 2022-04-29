# PICTURE Decoder Overview

> Sources: [[entities/picture]] · [[concepts/screen-layers]] · [[concepts/picture-rendering]] · [[concepts/picture-compression]]
> Confidence: **triangulated** (showpic.c + spec prose) except where noted.

---

## 1 — What a PICTURE resource is

A PICTURE is **a bytecode program, not a bitmap.** It's a variable-length stream of drawing opcodes that you run against two parallel 160×168 framebuffers. There are no raw pixels at rest; the pixels exist only after you've interpreted the stream.

```
VOL.* file
└── 5-byte v2 resource header (sig + vol + length)
    └── PICTURE payload — a stream of opcode bytes 0xF0..0xFF
                          interspersed with argument bytes < 0xF0
                          terminated by 0xFF
```

For AGI v3 games: the payload may be pre-compressed (see §6 below); you run a decompressor first, then dispatch the resulting v2-style stream identically.

---

## 2 — The dual-screen model

```
┌──────────────────────────────────────────────────┐
│           160 × 168 logical pixels               │
│                                                  │
│   VISUAL SCREEN          PRIORITY SCREEN         │
│   ─────────────          ─────────────           │
│   4-bit EGA color        4-bit value             │
│   index per pixel        per pixel               │
│                                                  │
│   What the player        Invisible depth +       │
│   sees. Init: white      control layer.          │
│   (color 15).            Init: red (value 4).    │
│                                                  │
│   Priority values:                               │
│     0..3  → control lines (barrier / alarm …)    │
│     4..14 → depth bands (4 = front, 14 = back)   │
│     15    → unused                               │
└──────────────────────────────────────────────────┘
        ↓ doubled horizontally at blit time
    320 × 200 display pixels
```

Both screens are written simultaneously by the same draw ops. Each drawing opcode checks two independent **enable flags** (one per screen) to decide where pixels land.

---

## 3 — Bytecode state machine

The interpreter carries a small piece of persistent state across opcode boundaries: current visual color, current priority color, whether picture-draw is enabled, whether priority-draw is enabled, and the current pen style. All of these survive from one opcode to the next — a later opcode inherits whatever the earlier opcodes left in place.

The dispatch rule is simple: any byte `>= 0xF0` is treated as the start of a new opcode; any byte `< 0xF0` is an argument to the current opcode. This means opcode argument lists have no explicit length — they end implicitly when the next `0xF0..0xFF` byte arrives, or when `0xFF` terminates the stream.

---

## 4 — Opcode catalogue

| Opcode | Mnemonic | Argument form | Notes |
|--------|----------|---------------|-------|
| `0xF0` | Set visual color | 1 fixed byte (0–15) | Enables picture-draw |
| `0xF1` | Disable visual | none | Turns off picture-draw |
| `0xF2` | Set priority color | 1 fixed byte (0–15) | Enables priority-draw |
| `0xF3` | Disable priority | none | Turns off priority-draw |
| `0xF4` | Y-corner | start `(x, y)` then alternating y, x, y, x… | Axis-locked polyline; Y axis changes first |
| `0xF5` | X-corner | start `(x, y)` then alternating x, y, x, y… | Axis-locked polyline; X axis changes first |
| `0xF6` | Absolute line | start pair, then further `(x, y)` pairs | Polyline through absolute coordinates |
| `0xF7` | Relative line | absolute start `(x, y)`, then displacement bytes | Each displacement byte packs Δx and Δy as 4-bit sign-magnitude values |
| `0xF8` | Flood fill | one or more `(x, y)` pairs | BFS fill; boundary rules depend on current draw-mode flags |
| `0xF9` | Set pen style | 1 fixed byte | Packs splatter flag, shape flag, and size into one byte |
| `0xFA` | Plot with pen | coordinate pairs (solid) or texture+coordinate triples (splatter) | Argument grouping changes based on pen-style splatter flag |
| `0xFB–0xFE` | Reserved | — | No-op; confirmed unused in showpic.c |
| `0xFF` | End | — | Resource terminator |

The corner opcodes (`0xF4`, `0xF5`) draw sequences of axis-aligned segments that alternate between horizontal and vertical — equivalent to a polyline where successive segments are always perpendicular.

---

## 5 — The four algorithms

### 5a — Line drawing (0xF4, 0xF5, 0xF6, 0xF7)

Sierra's line rasterizer is **not classical Bresenham.** It uses accumulated fixed-point arithmetic: it identifies whether a segment is "tall" (height dominates) or "wide" (width dominates), steps along the dominant axis one pixel at a time, and accumulates a fractional sub-pixel position on the minor axis, rounding to the nearest integer at each step.

The rounding rule is direction-sensitive — the threshold shifts slightly depending on which direction the line travels. This matters because flood fill correctness depends on every line being closed at the pixel level; a single rounding error that leaves a one-pixel gap will cause fill to bleed through.

### 5b — Flood fill (0xF8)

Implemented as a breadth-first search with a fixed 4000-entry circular queue. The "fillable" test depends on which screens are currently draw-enabled:

- If picture-draw is on (and the current visual color is not white): a pixel is fillable only if the visual screen holds white at that position. White is the init color — the only color that hasn't been explicitly drawn.
- If picture-draw is off: a pixel is fillable only if the priority screen holds the init color (red, priority 4) at that position.
- Both conditions must hold when both screens are active simultaneously.

This is why the screen init colors are foundational: they define the entire universe of fillable space before any drawing happens.

### 5c — Brush plotting (0xF9 / 0xFA)

The pen-style byte encodes three orthogonal properties: shape (circle or rectangle), size (0–7, producing a footprint of `2·size + 1` pixels per side), and whether splatter mode is active. The circle masks at each size are **precomputed constants** — Sierra's approximations have idiosyncrasies at small sizes that must be replicated exactly for pixel-exact output.

### 5d — Splatter mode

When splatter is active, each plot call takes a texture argument in addition to the coordinates. That texture argument selects a starting bit position from a 128-entry offset table, and the brush footprint is masked by reading consecutive bits from a global 256-bit pattern source. Only the bits that are set in the pattern cause a pixel to be written.

One important quirk: the bit-position counter wraps at 255 rather than 256 — bit 255 is never consumed before the wrap resets it to 0. This is believed to be a bug in the original Sierra interpreter, but must be replicated to match Sierra output.

There is also an open conflict: four entries in the splatter offset table differ between the spec prose and showpic.c (both authored by Lance Ewing). A ScummVM cross-check is needed to resolve which is authoritative.

---

## 6 — AGI v3: decompression pre-pass

AGI v3 PICTURE resources pack the color arguments of `0xF0` and `0xF2` into 4 bits instead of 8, saving space since only 16 colors exist. This creates a stream where bytes are no longer aligned to opcode boundaries. Before dispatching opcodes, a two-state machine re-expands the packed stream back into v2-style byte-aligned form. After that, the opcode dispatcher is identical for v2 and v3.

---

## 7 — Reference implementation

`AGI_Specifications/Code/showpic.c` — Lance Ewing's working Allegro-based PICTURE viewer (~650 lines). Every algorithm above is code-verified against it. For v3 decompression specifically, `AGI_Specifications/Code/picv3-v2.c` (67 lines) implements the two-state expander.

---

## 8 — Suggested implementation order

1. Resource loading — read PICTURE bytes from VOL at the offset from PICDIR (directory reader already exists).
2. Opcode dispatcher skeleton — loop and dispatch, maintaining the 5-field state struct.
3. Color set / disable ops (`0xF0–0xF3`) — needed before anything draws.
4. Absolute line (`0xF6`) — simplest draw op; tests the line algorithm in isolation.
5. Relative line (`0xF7`) — adds displacement decoding on top.
6. Corner opcodes (`0xF4`, `0xF5`) — axis-locked variant of the line algorithm.
7. Flood fill (`0xF8`) — needs correctly closed lines already in place.
8. Pen / plot solid (`0xF9` / `0xFA` without splatter) — circle and rectangle brushes.
9. Splatter (`0xFA` with splatter flag) — last and most fiddly.
10. v3 decompressor — only needed when targeting v3 games.

---

## 9 — Open items

- **Splatter offset table conflict** — indices 11, 15, 124, 125 differ between spec prose and showpic.c. Resolve via `engines/agi/picture.cpp` in ScummVM.
- **Per-pixel occlusion algorithm** — how screen-objects compose against the priority screen at frame time is not fully pinned. Deferred to GROUP 5 (VIEW) work or a ScummVM cross-check.
