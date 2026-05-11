# Screen Layers

> **Verification status:** The dual-screen model (dimensions, init colors, drawing-mode flags) is code-verified against Lance Ewing's reference PICTURE decoder at [`AGI_Specifications/Code/showpic.c`](../../AGI_Specifications/Code/showpic.c) — see the per-claim citations below. The per-pixel occlusion algorithm itself is NOT verified by showpic.c (which is a pic viewer, not a game runtime) and remains an open item.

A rendered AGI room consists of two parallel logical pixel grids — the **visual screen** and the **priority screen** — both written by PICTURE bytecode (see [[entities/picture]]). At runtime they share the same `(x, y)` coordinate space but encode different information [5-1-PICTURE.html §GENERAL GUIDELINES].

## Dimensions

Both screens are **160 pixels wide × 168 pixels tall** in logical AGI coordinates. The visible display doubles the horizontal resolution to 320×200 at render time (each AGI pixel painted twice horizontally; the bottom ~32 pixel rows below y=167 are reserved for the status line and input area outside the room frame). The 168-tall logical frame is the one used by the y → priority table in [[interpreter/priority-bands]].

## What each screen encodes

**Visual screen.** The image the player sees. Each pixel stores a 4-bit EGA color index (0..15) chosen from the standard 16-color palette (see `gfx/view_render.py`'s palette). Visual-screen content is purely cosmetic — color values carry no engine-side semantics.

**Priority screen.** Invisible to the player. Each pixel stores a 4-bit value used by two distinct subsystems:

- **Priority band** (values 4..14) — selects which of eleven depth bands the pixel belongs to. Drives per-pixel occlusion for screen-objects, per [[interpreter/priority-bands]].
- **Control line** (values 0..3) — encodes one of four control-line semantics: barrier, conditional barrier, alarm, water/surface. See [[interpreter/control-lines]].

Value 15 is unused on the priority screen.

The dual role of the priority screen (depth + control) is why colors 0..3 are reserved (control), 4..14 are bands, and 15 is unused. The reservation of 0..3 specifically follows from the EGA palette: black/blue/green/cyan are the four control colors precisely because their palette indices fall below the lowest band index.

## Initial state

When PICTURE drawing begins for a new room, both screens are cleared:

- Visual screen → all white (color 15).
- Priority screen → all red (priority 4, the topmost band).

This initialization is foundational for [[entities/picture]] §"Flood-fill target rule (`0xF8`)" correctness: fill boundaries are defined relative to the initial color (white on visual, red on priority), so any subsequent draw operation produces a stop-pixel. Independently corroborated by 5-2's AGDS translation [5-2-PICTURE.html §I.2.1.1]: "Initially all pixels of the background are white and priority 4."

## Drawing-mode flags

PICTURE bytecode maintains two independent enable flags:

- **Picture-draw enabled** — `0xF0` enables (and sets the color), `0xF1` disables. Subsequent draw opcodes touch the visual screen.
- **Priority-draw enabled** — `0xF2` enables (and sets the color), `0xF3` disables. Subsequent draw opcodes touch the priority screen.

A draw opcode writes to whichever screen(s) are currently enabled. Common patterns:

- Picture only: `0xF0 <color>` then `0xF3` (disable priority) then draw — visible scenery with no depth/control effect.
- Priority only: `0xF1` (disable picture) then `0xF2 <priority>` then draw — invisible bands or control lines.
- Both: `0xF0 <color>` then `0xF2 <priority>` then draw — coloured scenery that also writes the band beneath it.

## Composition with screen-objects

Screen-objects (ego, NPCs, props — sourced from VIEW resources) are composited on top of the rendered visual screen at frame time. Their visibility per pixel is determined by comparing the object's priority value against the priority-screen pixel at the same position: an object pixel with priority `p` is occluded by any priority-screen pixel with value `> p`. Object priority is set explicitly (`set.priority`) or assigned from the y → priority table when in release mode (`release.priority`); see [[interpreter/priority-bands]] for the band table and [[interpreter/command-semantics]] §`add.to.pic` for the related LOGIC-side composition opcode.

The full per-pixel occlusion algorithm — including how object cells interact with the search-downwards rule when a control-line pixel sits at the object's position — is **not yet pinned down**. 5-1 describes the screen structure and the search-downwards rule for *recovering* a priority value under a control-line pixel ([[interpreter/control-lines]]) but does not give the full object-vs-screen comparison procedure. Resolution is deferred to Group 5 (VIEW) or to ScummVM cross-check.

## SCI divergence

SCI splits this two-screen model into three independent layers (visual / priority / control), eliminating the control-vs-priority overload and the search-downwards complexity. AGI's two-screen design is a memory-era artifact preserved here for fidelity.

## Open items at this page's level

- **Per-pixel occlusion algorithm** — screen structure documented; full object-vs-screen comparison procedure deferred.
- **Object-vs-control-line interaction** — search-downwards recovers priority under a control pixel, but interaction with an object pixel that *is* a control color (rather than a band index) is unspecified.
- **Visual-screen masking by transparent cels** — VIEW cels have a transparent color (see `gfx/view_render.py`); how that interacts with priority comparison is a Group 5 concern.

## See also

- [[entities/picture]] — the PICTURE bytecode that writes both screens.
- [[interpreter/priority-bands]] — y → priority band assignment.
- [[interpreter/control-lines]] — black/blue/green/cyan color semantics on the priority screen.
- [[interpreter/command-semantics]] §`add.to.pic` — LOGIC-side composition of VIEW cels into the PICTURE buffers.
- [[sources/5-1-picture]] — chapter provenance.
