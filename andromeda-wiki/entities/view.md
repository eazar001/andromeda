# VIEW

VIEW resources hold the bitmap sprite graphics used for animated objects, NPCs, and inventory close-ups — every on-screen actor in an AGI room is a cel from a VIEW. Unlike PICTURE resources (vector-drawn full-screen backgrounds at [[entities/picture]]), VIEWs are stored as RLE-compressed bitmaps and composited on top of the rendered visual screen at frame time. A VIEW is a three-level container: **loops** (animation cycles, e.g. walk-north) → **cels** (frames) → **RLE-encoded pixel rows**. Maximum 255 loops and 255 cels per loop [6-1-VIEW.html §Overview].

This page is code-verified against [`resource/view.py`](../../resource/view.py) and [`gfx/view_render.py`](../../gfx/view_render.py), which round-trip real Sierra game data (SQ1).

## On-disk layout

```
+0  view header     (variable length; loop offset table)
+?  loop headers    (one per loop; cel offset tables, each relative to its loop start)
+?  cel headers     (3 bytes each; width, height, mirror+transparency byte)
+?  cel pixel data  (RLE rows, terminated by 0x00; one block per cel)
+?  description     (optional; null-terminated ASCII, 0x0A-separated lines)
```

All multi-byte words are little-endian (`ls,ms` in agidev's notation) [6-1-VIEW.html §View header note]. Loop offsets in the view header are relative to the **payload start** (byte 0 of the VIEW data after the 5-byte VOL chunk header is stripped) [resource/view.py:46-50]. Cel offsets in the loop header are relative to the **loop start**, not the payload start [6-1-VIEW.html §Loop header; resource/view.py:68].

## View header (7+ bytes)

| Offset | Field | Notes |
|---|---|---|
| 0 | Marker | Always 1 or 2; purpose undocumented [6-1-VIEW.html §View header] |
| 1 | Marker | Always 1; purpose undocumented [6-1-VIEW.html §View header] |
| 2 | Number of loops | 0..254 [6-1-VIEW.html §Overview] |
| 3-4 | Description offset (ls,ms) | Relative to payload start. `00 00` if no description [6-1-VIEW.html §View header] |
| 5-6 | Loop 0 offset (ls,ms) | Relative to payload start |
| 7-8 | Loop 1 offset (if loops ≥ 2) | |
| ... | ... | One 2-byte word per loop |

Two loop entries are allowed to point at the same data — this is the mechanism for loop mirroring (below) [6-1-VIEW.html §View header note]. The andromeda decoder skips the first two marker bytes unconditionally and reads num_loops at +2 [resource/view.py:41-43].

## Loop header (3+ bytes)

| Offset | Field | Notes |
|---|---|---|
| 0 | Number of cels | 0..254 [6-1-VIEW.html §Loop header] |
| 1-2 | Cel 0 offset (ls,ms) | Relative to **loop start** |
| 3-4 | Cel 1 offset (if cels ≥ 2) | |
| ... | ... | One 2-byte word per cel |

Cel offsets are converted to absolute file positions by adding the loop's start offset [resource/view.py:67-68].

## Cel header (3 bytes)

| Offset | Field | Notes |
|---|---|---|
| 0 | Width | In AGI logical pixels. Screen width = `width × 2` because AGI pixels are 2 EGA pixels wide [6-1-VIEW.html §Cel header; resource/view.py:89] |
| 1 | Height | In logical pixels (no doubling on the vertical axis) |
| 2 | Mirror info + transparent color | Packed; see below |

### Byte 2 layout (code-verified)

```
bit:  7   6   5   4   3   2   1   0
     [M] [---L---]  [-----T-----]
```

| Bits | Field | Meaning |
|---|---|---|
| 7 | Mirror flag (M) | `1` = this cel is part of a mirrored loop; `0` = standalone |
| 6,5,4 | Non-mirror loop index (L) | 0..7. When M=1, identifies which loop holds the canonical (non-flipped) cel data |
| 3..0 | Transparent color (T) | 0..15 EGA palette index. Pixels of this color are not drawn — the background shows through [resource/view.py:89; gfx/view_render.py:19] |

**Decoding:** the andromeda code extracts the high nibble, then splits it: `flag = nibble_hi >> 3`, `loop_idx = nibble_hi & 7` [resource/view.py:89-90; util/byte.py]. The transparent color is just `nibble_lo` [resource/view.py:89].

> **Spec wording note.** 6-1-VIEW.html §Cel header and §Mirroring describe this byte ambiguously: "The first four bits... handle mirroring; the last four bits... transparent color" can be read either way depending on bit-numbering convention, and the §Mirroring text contains an apparent typo — "Bit 1 specifies whether or not this cel is mirrored" overlaps with the immediately following "Bits 1, 2 and 3 specify the number of the loop". The layout documented above is the empirical one used by the andromeda decoder and AGI Studio's renderer, verified against SQ1 game files [resource/view.py:83-88]. Both the nibble assignment (high = mirror, low = transparency) and the within-high-nibble assignment (MSB = flag, low 3 bits = loop index) are taken from the working code, not from the spec prose.

## Cel data (RLE rows)

Pixel data for each cel follows its 3-byte header. The encoding is row-major, RLE-compressed; full details at [[concepts/rle-encoding]]. Short version:

- Each non-zero byte is a **chunk**: high nibble = color index (0..15), low nibble = run length (1..15 pixels) [6-1-VIEW.html §Cel data].
- A `0x00` byte terminates the current row; the next byte begins the next row [6-1-VIEW.html §Cel data; resource/view.py:103-104].
- If the last run on a row is the transparent color, the encoder may omit it — the `0x00` terminator implicitly pads to the right edge [6-1-VIEW.html §Cel data, transparency optimization].

Row count = cel height. Pixel rendering doubles each chunk's pixel count horizontally to convert AGI logical width to EGA screen width [gfx/view_render.py:18, 21, 39].

## Loop mirroring

A loop can be declared as a horizontal flip of another loop, so the artist only draws one direction and the runtime flips at composition time. This is how walk-left / walk-right animations are typically encoded [6-1-VIEW.html §Mirroring].

**Mechanism:**

1. Two entries in the view-header loop-offset table point at the same byte offset (shared cel data) [6-1-VIEW.html §View header note].
2. Each cel header's byte 2 has the mirror flag set (bit 7) and the non-mirror-loop-index field (bits 4-6) identifying which of the two sharing loops is the *canonical* (un-flipped) one.
3. When rendering, the runtime compares the current loop index against the non-mirror loop index. If they differ, the cel is drawn horizontally flipped [gfx/view_render.py:7, 21].

**Sierra runtime quirk (not in andromeda).** The original Sierra interpreter mutates the cel header in-place as it renders: when it flips a cel for display in loop L, it overwrites the non-mirror-loop-index field with L itself, so subsequent renders see the cel as "already correctly oriented for loop L" and only re-flip on loop changes [6-1-VIEW.html §Mirroring, "Mirroring is done by..."]. This is why the byte stores a *loop index* rather than just a flip-or-not bit. The andromeda decoder does not perform this mutation — it parses the original byte once and re-evaluates the flip per frame [gfx/view_render.py:7].

**Reserved-space requirement.** Because the Sierra interpreter mutates cel data in place, mirrored cels must be allocated enough VOL-file space to hold both their original and flipped RLE encodings (the flipped version can be longer if it shifts trailing transparency to the start). Spec notes this constraint is enforced by interpreter 2.917 but not 2.440 [6-1-VIEW.html §Mirroring, "Leaving enough room..."]. Andromeda's read-only decoder is unaffected by either.

## Description (optional)

If a VIEW is used as an inventory close-up (selected via the `show.obj` LOGIC opcode — see [[interpreter/command-semantics]]), it carries a human-readable description: null-terminated ASCII, with `0x0A` separating lines [6-1-VIEW.html §Description]. The view header's description offset (bytes 3-4) points to it. `00 00` in those bytes means no description.

The andromeda decoder reads the description offset into `View.desc_offset` [resource/view.py:46, 55] but does not yet parse the string itself — open item.

## Composition with screens

VIEW cels are composited on top of the rendered visual screen at frame time. Their visibility per pixel is mediated by the priority screen — see [[concepts/screen-layers]] for the dual-screen model and [[interpreter/priority-bands]] for the y → priority band table. The transparent color from the cel header byte 2 is the alpha channel: pixels of that color are skipped during compositing [gfx/view_render.py:19; gfx/view_render.py:42].

The per-pixel object-vs-priority comparison rule itself is still an open item at [[concepts/screen-layers]] §"Open items at this page's level" — 6-1 documents the cel format but not the runtime occlusion procedure.

## Runtime object state

Each loaded VIEW resource is bound to one or more VIEW *objects* — runtime instances that track animation and motion state. The interpreter maintains a heap-resident table of active objects, with one 43-byte entry per object in SQ2 (size may vary by interpreter version). See [[interpreter/view-objects]] for the full table entry structure, including position, animation cel index, direction, flags, and priority [6-2-VIEW.html §VIEW TABLE ENTRY].

At each interpreter cycle, step 10 (rendering) updates all resident objects: advancing animation cels per `cycle_time`, repositioning per motion state, and compositing visible cels to the visual screen — see [[interpreter/event-loop]] [6-2-VIEW.html §overview].

## Open items

- Description string parsing (offset is read; string body is not).
- Per-pixel occlusion algorithm when a VIEW cel pixel falls on a control-line pixel (priority colors 0..3); deferred to a later ingest or ScummVM cross-check.

## Reference implementation

Peter Kelly's `viewview.pas` (vendored at `AGI_Specifications/Code/viewview.pas`, listed by [[sources/6-3-view]]) is the canonical reference parser for this format. It independently corroborates every byte-level claim above:

| Claim on this page | viewview.pas | andromeda |
|---|---|---|
| Cel header byte 2 low nibble = transparency | `viewview.pas:203` (`TransCol := curbyte AND $0F`) | `resource/view.py:89` |
| Cel header byte 2 bit 7 = mirror flag | `viewview.pas:204` (`if curbyte >= $80 then ... Mirror := TRUE`) | `resource/view.py:90` |
| RLE chunk: high nibble = color, low nibble = run length | `viewview.pas:113-114` | `resource/view.py:106` |
| `0x00` byte terminates row | `viewview.pas:111` | `resource/view.py:103-104` |
| Screen width = cel width × 2 (horizontal doubling) | `viewview.pas:104-105` (`Width*2` buffer allocation) | `gfx/view_render.py:18, 39` |

`viewview.pas` also exhibits the Sierra-runtime in-place mutation style of mirroring at lines 127-137: when `Cel.Mirror` is set and the loop is the second occurrence of a shared loop offset (`LoopOccur[loopno] = 2`), the just-finished row is reversed in-place before advancing. Andromeda defers the flip to render time at `gfx/view_render.py:7` (`mirrored = cel.mirror and loop_idx != cel.non_mirror_idx`) — both implementations are spec-conformant; the choice is read-only vs. mutating.

## See also

- [[concepts/rle-encoding]] — chunk byte structure, row termination, transparency padding rule.
- [[concepts/ega-palette]] — 16-color palette used by the color and transparency indices.
- [[concepts/screen-layers]] — visual and priority screens; cel composition target.
- [[interpreter/priority-bands]] — y → priority band table used to occlude cel pixels.
- [[interpreter/command-semantics]] — `show.obj`, `set.view`, `set.cel`, `set.loop`, and `add.to.pic` opcodes that operate on VIEWs.
- [[sources/6-1-view]] — chapter provenance.
- [[sources/6-3-view]] — sample-code pointer at `viewview.pas`, the canonical reference parser used for cross-validation above.
