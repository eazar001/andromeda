# VIEW

VIEW resources hold the bitmap sprite graphics used for animated objects, NPCs, and inventory close-ups — every on-screen actor in an AGI room is a cel from a VIEW. Unlike PICTURE resources (vector-drawn full-screen backgrounds at [[entities/picture]]), VIEWs are stored as RLE-compressed bitmaps and composited on top of the rendered visual screen at frame time. A VIEW is a three-level container: **loops** (animation cycles, e.g. walk-north) → **cels** (frames) → **RLE-encoded pixel rows**. Maximum 255 loops and 255 cels per loop [6-1-VIEW.html §Overview].

This page is code-verified against [`resource/view.py`](../../resource/view.py) and [`gfx/view_render.py`](../../gfx/view_render.py), which round-trip real Sierra game data (SQ1). A separate throwaway decoder matches them on all 238 SQ1 views and all 1,652 cels, pixel for pixel, and all 216 mirrored cels are exact flips of their source cels [SQ1 data check, log 2026-11-01]. Those 1,652 references come to 1,433 distinct cels, once shared loops are counted once [SQ1 data check, audit draw].

The layout and draw rules were also checked against AGI 2.917 by static reading. The cel routines live in `IBM_OBJS.OVL`, which [[sources/agi-2917-binary]] places at `1000:9CF0`. The Hercules overlay `HGC_OBJS.OVL` is unread.

## On-disk layout

```
+0  view header     (variable length; loop offset table)
+?  loop headers    (one per loop; cel offset tables, each relative to its loop start)
+?  cel headers     (3 bytes each; width, height, mirror+transparency byte)
+?  cel pixel data  (RLE rows, terminated by 0x00; one block per cel)
+?  description     (optional; null-terminated ASCII, 0x0A-separated lines)
```

All multi-byte words are little-endian (`ls,ms` in agidev's notation) [6-1-VIEW.html §View header note]. Loop offsets in the view header are relative to the **payload start** (byte 0 of the VIEW data after the 5-byte VOL chunk header is stripped) [resource/view.py:46-50; AGI 2.917 1000:3C34]. Cel offsets in the loop header are relative to the **loop start**, not the payload start [6-1-VIEW.html §Loop header; resource/view.py:68; AGI 2.917 1000:3D81].

## View header (7+ bytes)

| Offset | Field | Notes |
|---|---|---|
| 0 | Marker | Purpose undocumented; see the conflict below [6-1-VIEW.html §View header] |
| 1 | Marker | Purpose undocumented; see the conflict below [6-1-VIEW.html §View header] |
| 2 | Number of loops | A byte [AGI 2.917 1000:3B22]. SQ1's largest is 4 [SQ1 data check, audit draw] |
| 3-4 | Description offset (ls,ms) | Relative to payload start. `00 00` if no description [6-1-VIEW.html §View header] |
| 5-6 | Loop 0 offset (ls,ms) | Relative to payload start |
| 7-8 | Loop 1 offset (if loops ≥ 2) | |
| ... | ... | One 2-byte word per loop |

> [!conflict] Marker bytes
> The spec says byte 0 is always 1 or 2 and byte 1 is always 1 [6-1-VIEW.html §View header]. In SQ1, 237 views have `1, 1` and VIEW 104 has `0, 2` [SQ1 data check, audit draw]. None of the 2.917 routines read in this audit use these two bytes, so a decoder shouldn't validate them. The driver routine reached from the view-load hook at `1000:5857` is unread, so this isn't proof that nothing does.

The spec's limit of 255 loops and 255 cels follows from these being byte fields, and wasn't tested further. SQ1's largest cel count is 10 [SQ1 data check, audit draw].

Two loop entries are allowed to point at the same data [6-1-VIEW.html §View header note]; 35 SQ1 views do this [SQ1 data check, audit draw]. The andromeda decoder skips the first two marker bytes unconditionally and reads num_loops at +2 [resource/view.py:41-43].

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
| 3..0 | Transparent color (T) | 0..15 EGA palette index. Pixels of this color are not drawn — the background shows through [resource/view.py:89; gfx/view_render.py:17] |

**Decoding:** the andromeda code extracts the high nibble, then splits it: `flag = nibble_hi >> 3`, `loop_idx = nibble_hi & 7` [resource/view.py:89-90; util/byte.py]. The transparent color is just `nibble_lo` [resource/view.py:89].

> **Spec wording note.** 6-1-VIEW.html §Cel header and §Mirroring describe this byte ambiguously: "The first four bits... handle mirroring; the last four bits... transparent color" can be read either way depending on bit-numbering convention, and the §Mirroring text contains an apparent typo — "Bit 1 specifies whether or not this cel is mirrored" overlaps with the immediately following "Bits 1, 2 and 3 specify the number of the loop". The layout documented above is the empirical one used by the andromeda decoder and AGI Studio's renderer, verified against SQ1 game files [resource/view.py:83-88]. Both the nibble assignment (high = mirror, low = transparency) and the within-high-nibble assignment (MSB = flag, low 3 bits = loop index) are taken from the working code, not from the spec prose. **Confirmed** by 2.917, which tests bit 7, masks bits 6-4 as the loop index, and shifts the low nibble up for the transparent color [AGI 2.917 1000:9D87, 1000:57C5, 1000:9DA6].

## Cel data (RLE rows)

Pixel data for each cel follows its 3-byte header. The encoding is row-major, RLE-compressed; full details at [[concepts/rle-encoding]]. Short version:

- Each non-zero byte is a **chunk**: high nibble = color index (0..15), low nibble = run length (1..15 pixels) [6-1-VIEW.html §Cel data].
- A `0x00` byte terminates the current row; the next byte begins the next row [6-1-VIEW.html §Cel data; resource/view.py:103-104].
- If the last run on a row is the transparent color, the encoder may omit it — the `0x00` terminator implicitly pads to the right edge [6-1-VIEW.html §Cel data, transparency optimization].

Row count = cel height. Cels are composited in logical pixels; horizontal doubling happens when the screen is converted for display [gfx/palette.py:visual_screen_to_bytes].

## Loop mirroring

A loop can be declared as a horizontal flip of another loop, so the artist only draws one direction and the runtime flips at composition time. This is how walk-left / walk-right animations are typically encoded [6-1-VIEW.html §Mirroring].

**Mechanism:**

1. Two entries in the view-header loop-offset table point at the same byte offset (shared cel data) [6-1-VIEW.html §View header note].
2. Each cel header's byte 2 has the mirror flag set (bit 7) and the non-mirror-loop-index field (bits 4-6) identifying which of the two sharing loops is the *canonical* (un-flipped) one.
3. When rendering, the runtime compares the current loop index against the non-mirror loop index. If they differ, the cel is drawn horizontally flipped [gfx/view_render.py:3, 18; AGI 2.917 1000:9D87, 1000:57CE].

Refined: in 2.917 only the cel's own byte 2 matters. The interpreter never looks at whether loop offsets are shared. A cel with bit 7 clear is never flipped, even when it's shared. SQ1 has one such cel. All 216 cels with bit 7 set are shared across loops, and their stored index is always one of those loops [SQ1 data check, audit draw].

**Sierra runtime quirk (not in andromeda).** **Confirmed** for 2.917. The interpreter rewrites the cel in memory just before drawing: it stores the current loop in the index field and rewrites every row reversed, so later draws in that loop need no work [6-1-VIEW.html §Mirroring, "Mirroring is done by..."; AGI 2.917 1000:57B5]. This is why the byte stores a *loop index* rather than just a flip-or-not bit. The andromeda decoder does not perform this mutation — it parses the original byte once and re-evaluates the flip per frame [gfx/view_render.py:3].

For each row the rewrite does the following [AGI 2.917 1000:57F9–1000:5841]:

1. Leading chunks of the transparent color are dropped, and the row's width is totalled from the rest.
2. The blank space on the right, `width` minus that total, becomes leading transparent chunks of up to 15 pixels each.
3. The remaining chunks are copied in reverse order. Transparent chunks inside the row stay, as they are part of the reversed data.
4. A row holding nothing but transparent chunks becomes a bare terminator.

The result is built in a 2,048-byte stack buffer, then copied over the original [AGI 2.917 1000:57DF, 1000:584A]. Modeling this on all 216 mirrored SQ1 cels gives an exact pixel flip every time [SQ1 data check, audit draw].

The stored index holds only 3 bits, but it's compared with the whole loop number. A mirrored cel used in loop 8 or above would never match and would be flipped again on every draw. This is read from the code, and SQ1 has no such loops [AGI 2.917 1000:57C5–1000:57D0].

**Reserved-space requirement.** Refined. Because the interpreter mutates cel data in place, mirrored cels need room for both their original and flipped RLE encodings; the flipped version can be longer if it shifts trailing transparency to the start. The spec says this constraint is enforced by interpreter 2.917 but not 2.440 [6-1-VIEW.html §Mirroring, "Leaving enough room..."]. Nothing in 2.917 checks it: the rewrite copies back whatever length it produced, and a longer result overwrites the bytes after the cel [AGI 2.917 1000:5845–1000:584A]. The rule binds resource authors rather than the interpreter. In SQ1, 32 of the 216 mirrored cels grow when flipped, and none exceeds the space before the next cel, loop or description [SQ1 data check, audit draw]. 2.440 wasn't checked. Andromeda's read-only decoder is unaffected by either.

## Description (optional)

If a VIEW is used as an inventory close-up (selected via the `show.obj` LOGIC opcode — see [[interpreter/command-semantics]]), it carries a human-readable description: null-terminated ASCII, with `0x0A` separating lines [6-1-VIEW.html §Description]. The view header's description offset (bytes 3-4) points to it. `00 00` in those bytes means no description. 20 SQ1 views have one, including all four that SQ1's literal `show.obj` calls name [SQ1 data check, audit draw].

Refined: `show.obj` doesn't test for zero. It adds the offset to the view's address and prints, so a view with no description would print its own header bytes as text. The string goes through the normal message window [AGI 2.917 1000:5F1F–1000:5F25].

The andromeda decoder reads the description offset into `View.desc_offset` [resource/view.py:46, 55] but does not yet parse the string itself — open item.

## Composition with screens

VIEW cels are composited on top of the rendered visual screen at frame time. Their visibility per pixel is mediated by the priority screen — see [[concepts/screen-layers]] for the dual-screen model and [[interpreter/priority-bands]] for the y → priority band table. The transparent color from the cel header byte 2 is the alpha channel: pixels of that color are skipped during compositing [gfx/view_render.py:17].

The per-pixel comparison is now settled for 2.917; see [[interpreter/priority-bands]] §"How a cel pixel is compared" and [[interpreter/control-lines]] §"Search-downwards rule".

In 2.917 a cel's top-left corner is at `(x, y - height + 1)`, so `(x, y)` is its bottom-left pixel. Row and column are computed from the low bytes of these values [AGI 2.917 1000:9D99–1000:9DA3, 1000:559E].

Drawing isn't layered at display time. Each cel is written straight into the shared 160 by 168 buffer, which holds priority in the high nibble and color in the low nibble of each byte. The interpreter keeps it clean by saving what's underneath [AGI 2.917 1000:9D75]:

1. For each object it allocates a 16-byte record holding the links, the object pointer and the rectangle, plus a save area of width times height bytes [AGI 2.917 1000:8FD0].
2. Going back to front, it copies the rectangle from the buffer to the save area, then draws the cel [AGI 2.917 1000:045E, 1000:9CF9].
3. To erase, it goes front to back, copying each save area back over the buffer, both nibbles together, then frees the records [AGI 2.917 1000:0307, 1000:9D38].

Two lists exist, static objects and updating objects, and the updating list is the one rebuilt each cycle [AGI 2.917 1000:0614, 1000:6976, 1000:695F]. The draw order is in [[interpreter/priority-bands]] §"Draw order". After drawing, the rectangle covering a cel's old and new positions is sent to the display, unless `DS:120E` is zero [AGI 2.917 1000:569A].

## Runtime object state

Each loaded VIEW resource is bound to one or more VIEW *objects* — runtime instances that track animation and motion state. The interpreter maintains a heap-resident table of active objects, with one 43-byte entry per object in SQ2 (size may vary by interpreter version). 2.917 also uses 43 bytes [AGI 2.917 1000:0573, 1000:0B34]. See [[interpreter/view-objects]] for the full table entry structure, including position, animation cel index, direction, flags, and priority [6-2-VIEW.html §VIEW TABLE ENTRY].

At each interpreter cycle, step 10 (rendering) updates all resident objects: advancing animation cels per `cycle_time`, repositioning per motion state, and compositing visible cels to the visual screen — see [[interpreter/event-loop]] [6-2-VIEW.html §overview].

## Open items

- Description string parsing in the project's decoder (offset is read; string body is not).
- `1000:5857`, called when a view loads, passes the view to the graphics-driver entry at `1000:9777`. It does this only when `DS:1126` is 0 and `DS:1128` is neither 2 nor 3. The driver entry is unread.
- Horizontal doubling in 2.917 happens in the graphics driver, which this audit didn't read.
- The comparison with `viewview.pas` below is carried over and wasn't repeated.

## Reference implementation

Peter Kelly's `viewview.pas` (vendored at `AGI_Specifications/Code/viewview.pas`, listed by [[sources/6-3-view]]) is the canonical reference parser for this format. It independently corroborates every byte-level claim above:

| Claim on this page | viewview.pas | andromeda |
|---|---|---|
| Cel header byte 2 low nibble = transparency | `viewview.pas:203` (`TransCol := curbyte AND $0F`) | `resource/view.py:89` |
| Cel header byte 2 bit 7 = mirror flag | `viewview.pas:204` (`if curbyte >= $80 then ... Mirror := TRUE`) | `resource/view.py:90` |
| RLE chunk: high nibble = color, low nibble = run length | `viewview.pas:113-114` | `resource/view.py:106` |
| `0x00` byte terminates row | `viewview.pas:111` | `resource/view.py:103-104` |
| Screen width = cel width × 2 (horizontal doubling) | `viewview.pas:104-105` (`Width*2` buffer allocation) | `gfx/palette.py:visual_screen_to_bytes` |

`viewview.pas` also exhibits the Sierra-runtime in-place mutation style of mirroring at lines 127-137: when `Cel.Mirror` is set and the loop is the second occurrence of a shared loop offset (`LoopOccur[loopno] = 2`), the just-finished row is reversed in-place before advancing. Andromeda defers the flip to render time at `gfx/view_render.py:3` (`mirrored = cel.mirror and loop_idx != cel.non_mirror_idx`) — both implementations are spec-conformant; the choice is read-only vs. mutating.

## See also

- [[concepts/rle-encoding]] — chunk byte structure, row termination, transparency padding rule.
- [[concepts/ega-palette]] — 16-color palette used by the color and transparency indices.
- [[concepts/screen-layers]] — visual and priority screens; cel composition target.
- [[interpreter/priority-bands]] — y → priority band table used to occlude cel pixels.
- [[interpreter/command-semantics]] — `show.obj`, `set.view`, `set.cel`, `set.loop`, and `add.to.pic` opcodes that operate on VIEWs.
- [[sources/6-1-view]] — chapter provenance.
- [[sources/6-3-view]] — sample-code pointer at `viewview.pas`, the canonical reference parser used for cross-validation above.
