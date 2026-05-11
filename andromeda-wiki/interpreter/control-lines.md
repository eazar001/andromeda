# Control Lines

> **Page-level caveat:** No PICTURE / control-line decoder exists in `resource/`. The four-color semantics below come from 5-1's prose and are corroborated by 2-1's overview, but the conditional / alarm bindings to specific LOGIC opcodes are not yet pinned. `(agidev, unverified)` applies as a process tag.

Control lines are pixels drawn on the **priority screen** in one of four colors (black, blue, green, cyan) that the interpreter tests at runtime to drive screen-object motion, event triggers, and surface confinement [5-1-PICTURE.html §CONTROL LINES; 2-1-Interpreter.html §What are the priority bands?]. They share the priority screen with the eleven priority bands documented in [[interpreter/priority-bands]] — colors 0..3 are reserved for control-line semantics, colors 4..14 carry priority-band indices, color 15 is unused.

The four control colors correspond directly to EGA palette indices 0..3 (black, blue, green, cyan), which is why those particular four colors were chosen — they are exactly the priority values that fall below the lowest band index (4).

## Color semantics

| Color | EGA index | Semantics |
|-------|-----------|-----------|
| Black | 0 | **Unconditional barrier.** Screen-object motion is blocked at any black pixel. |
| Blue  | 1 | **Conditional barrier.** Motion is blocked only if a LOGIC-controlled condition is true; otherwise the pixel is passable. |
| Green | 2 | **Alarm.** Crossing a green pixel triggers a LOGIC-side event sequence (typical uses: drowning, falling, scene transition, trap activation). |
| Cyan  | 3 | **Surface confinement.** Screen-objects flagged `object.on.water` are confined to cyan regions; other objects ignore cyan. |

Independently corroborated by 5-2's AGDS translation [5-2-PICTURE.html §I.2.1]: "0 - unconditional barrier, 1 - conditional barrier, 2 - alarm barrier, 3 - water surface". The 5-2 wording differs from 5-1 only in calling green an "alarm barrier" rather than just "alarm" (same semantics).

The LOGIC-side binding — which flag controls a blue barrier's pass/block decision, which subroutine fires when ego crosses a green line, which command sets the `object.on.water` flag — surfaces in subsequent Group 4/5 chapters; this page documents only the PICTURE-side pixel semantics. Cross-reference [[interpreter/commands]] for the opcode catalogue and [[interpreter/command-semantics]] for behavioral notes once specific bindings are identified.

## Search-downwards algorithm

Because control lines and priority bands share the priority screen, a control-line pixel **overwrites** the priority-band value at that position. When the interpreter needs the priority for a pixel that happens to be a control color, it cannot read the underlying band directly. The recovery rule [5-1-PICTURE.html §CONTROL LINES AND PRIORITY INFORMATION]:

1. If the pixel at `(x, y)` has color 0..3, search downwards (increasing `y`) for the first pixel whose color is ≥ 4.
2. That pixel's priority is taken as the priority at the original `(x, y)`.
3. If the search reaches the bottom of the screen without finding a priority pixel, behavior is undefined `(agidev, unverified)`.

This search can span many pixels when a control line sits high in the room, and produces a small class of known visual artifacts where a screen-object renders at the priority of a band well below where it appears to stand. The spec cites **KQ1 room 20** — the blue control line beside the left-hand tree — as the canonical artifact case [5-1-PICTURE.html].

## Flood fill

`0xF8` flood-fill (see [[entities/picture]] §"Opcode catalogue") interacts with control-line pixels via the same priority-screen layer:

- If only picture-draw is enabled, fill spreads on the visual screen, bounded by any non-white pixel.
- If only priority-draw is enabled, fill spreads on the priority screen, bounded by any non-red pixel (red = priority 4, the initial fill of the priority screen). Control-line colors 0..3 therefore act as fill boundaries.
- If both are enabled, fill respects boundaries on both layers simultaneously.

## Relation to the priority bands

[[interpreter/priority-bands]] already documents that priorities 0..3 are reserved for "non-band uses"; this page is the resolution of that pointer. The y → priority auto-assignment table only assigns bands 4..14, never 0..3, so a control-line color can never be produced by `release.priority`/auto-assignment — only by explicit drawing in the PICTURE bytecode.

## SCI divergence

In SCI (Sierra's next-generation engine) control lines move to a dedicated third screen, eliminating the priority/control overload and the need for the search-downwards algorithm. AGI's shared-screen design is a memory-era constraint preserved here for completeness.

## See also

- [[entities/picture]] §"Bytecode dispatch" — how `0xF2`-mode drawing writes these colors.
- [[interpreter/priority-bands]] — y → priority band assignment for screen objects, separate from the control-line semantics here.
- [[concepts/screen-layers]] — the visual / priority dual-screen model.
- [[sources/5-1-picture]] — chapter provenance.
