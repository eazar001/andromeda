# Control Lines

> **Audit status.** Checked against AGI 2.917 by static reading of the interpreter and of `IBM_OBJS.OVL`, the overlay holding the cel routines, which [[sources/agi-2917-binary]] places at `1000:9CF0`. Nothing was run. The Hercules overlay `HGC_OBJS.OVL` is unread.

Control lines are pixels on the **priority screen** with priority 0, 1, 2 or 3 (black, blue, green, cyan) that the interpreter tests when it places or moves a screen object [5-1-PICTURE.html §CONTROL LINES; 2-1-Interpreter.html §What are the priority bands?; AGI 2.917 1000:55F0]. They share the priority screen with the bands in [[interpreter/priority-bands]]: 4 to 14 are the y-derived bands and 15 is the band closest to the viewer.

The priority screen isn't a separate buffer in 2.917. One 160 by 168 byte buffer, in its own segment, holds the priority in the high nibble of each byte and the color in the low nibble [AGI 2.917 1000:424C, 1000:55F0, 1000:9D75].

## Color semantics

| Value | Color | Effect on the baseline test | Side effect for EGO |
|---|---|---|---|
| 0 | Black | Always fails | None |
| 1 | Blue | Fails unless the object has `ignore.blocks` set | None |
| 2 | Green | Passes | Sets `flag(3)` |
| 3 | Cyan | Passes, and counts toward "all water" | Sets `flag(0)` if the whole baseline is cyan |

[AGI 2.917 1000:5637–1000:5698]. The spec's names agree: "0 - unconditional barrier, 1 - conditional barrier, 2 - alarm barrier, 3 - water surface" [5-2-PICTURE.html §I.2.1].

**Blue is per object.** The condition is the object's own flag bit 1, set by `$58 ignore.blocks` and cleared by `$59 observe.blocks` [AGI 2.917 1000:5692, 1000:7AEF, 1000:7B14]. `ignore.blocks` has no effect on black.

**Green doesn't stop anything.** It only sets `flag(3)`, and only for object 0. Other objects pass over it with no effect, and LOGIC decides what happens by reading the flag [AGI 2.917 1000:5696, 1000:5663].

## The baseline test

The test reads one row: the object's `y`, from `x` to `x + width - 1`, left to right [AGI 2.917 1000:55F0]. The rules, in order:

1. If the object's priority isn't fixed, its priority is first reset from the y table. This is the routine that assigns automatic priority; see [[interpreter/priority-bands]].
2. An object at priority exactly 15 skips the row entirely and passes. For EGO this clears `flag(0)` and `flag(3)`.
3. The scan stops at the first pixel that fails: black, or blue without `ignore.blocks`.
4. If the scan finishes, the whole baseline being cyan fails an object with `object.on.land` set. Anything else fails an object with `object.on.water` set. Otherwise the test passes [AGI 2.917 1000:564C–1000:5660].
5. For object 0 only, `flag(3)` and `flag(0)` are written from what the scan saw, whether or not the test passed [AGI 2.917 1000:5663–1000:5682].

So `object.on.water` needs every baseline pixel to be cyan, and `object.on.land` is blocked only by a baseline that is entirely cyan. A partly cyan baseline satisfies land and fails water. `object.on.anything` clears both flag bits [AGI 2.917 1000:7DAA]. Object 0 also has both bits cleared at the end of any cycle's screen update in which at least one object was active, so on EGO these commands last one cycle unless LOGIC repeats them [AGI 2.917 1000:0610, 1000:0635–1000:0639].

Two consequences of the scan stopping early:

- `flag(3)` can't see a green pixel to the right of the pixel that failed.
- `flag(0)` starts true and is cleared by any pixel other than cyan or black. If EGO's scan stops on a black pixel with only cyan before it, `flag(0)` ends up set. A failed step is normally followed by another test, so this should be brief. Marked Runtime only.

> [!conflict] Priority 15 and conditional barriers
> The spec says an object at priority 15 without `ignore.blocks` cannot cross a conditional barrier [4-4-Logic.html §OBJECT CONTROL COMMANDS]. In 2.917 an object at priority 15 skips the baseline test altogether, so it crosses blue and black alike [AGI 2.917 1000:562A].

### When the test runs

- On each motion step of an updating object, after the object-overlap check. If the overlap check fails, this test is skipped for that attempt. On failure the object goes back to its old position and the placement search runs [AGI 2.917 1000:1609–1000:1631].
- In the placement search used by `draw`, `add.to.pic`, `reposition`, `reposition.to` and `reposition.to.v`. The search tries the position, then spirals outward until the bounds, overlap and baseline checks all pass [AGI 2.917 1000:5872, 1000:0A4E, 1000:2DF5, 1000:7CA2, 1000:7CE7, 1000:7D3A].

Motion runs after updating objects have been erased, so the test doesn't see their pixels. Objects in the static list stay in the buffer, so their priorities are what the test reads under them [AGI 2.917 1000:0614–1000:061E].

## Search-downwards rule

When a cel pixel lands on a control pixel, the interpreter looks down the same column for the priority to compare against [5-1-PICTURE.html §CONTROL LINES AND PRIORITY INFORMATION; AGI 2.917 1000:9E06]:

1. A pixel with priority 0, 1 or 2 starts the search. Priority 3 doesn't: cyan is compared directly, as an ordinary low priority.
2. The search moves down one row at a time and stops at the first pixel with priority 3 or higher.
3. If it reaches row 167 first, it uses the last value it read. An object at priority 2 or above therefore draws.
4. If the object's priority is at least the value found, the pixel is drawn.

A pixel drawn through this path **keeps its control value**. Only the color nibble changes, so black, blue and green lines survive cels drawn over them. A pixel drawn normally, including over cyan, takes the object's priority [AGI 2.917 1000:9DEF–1000:9DF3].

> [!conflict] Which values start the search
> The spec says a pixel of color 0..3 searches downward for a color of 4 or higher [5-1-PICTURE.html §CONTROL LINES AND PRIORITY INFORMATION]. In 2.917 only 0..2 search, and the search stops at 3 or higher [AGI 2.917 1000:9DE7, 1000:9E19].

> [!conflict] Reaching the bottom of the screen
> This page previously called this case undefined `(agidev, unverified)`. In 2.917 it is defined by the steps above [AGI 2.917 1000:9E09].

The spec cites KQ1 room 20, the blue line beside the left-hand tree, as a visual artifact of this rule [5-1-PICTURE.html]. That is another game and wasn't checked.

## Flood fill

`0xF8` flood fill (see [[entities/picture]] §"Opcode catalogue") interacts with control-line pixels through the same layer. This section wasn't part of this audit; the PICTURE pages own it.

- If only picture-draw is enabled, fill spreads on the visual screen, bounded by any non-white pixel.
- If only priority-draw is enabled, fill spreads on the priority screen, bounded by any non-red pixel (red = priority 4, the initial fill of the priority screen). Control-line colors 0..3 therefore act as fill boundaries.
- If both are enabled, the visual screen's white region decides where the fill goes; see [[entities/picture]] §"Flood-fill target rule (`0xF8`)".

The fill does nothing at all if the visual layer is enabled with color 15, even if priority is also enabled, or if only the priority layer is enabled with priority 4 [AGI 2.917 1000:5282–1000:529E]. A both-layers fill writes priority at every filled pixel, whatever was there [AGI 2.917 1000:52F4].

## Relation to the priority bands

The y table assigns only 4 to 14, so automatic priority can never produce a control value [AGI 2.917 1000:55DA].

> [!conflict] Where control values come from
> This page previously said control values come only from explicit drawing in PICTURE bytecode. In 2.917 LOGIC can write them too. The `add.to.pic` margin writes a rectangle of priority 0 to 3, and a cel drawn at a fixed priority from 1 to 3 writes that value into every pixel it draws [AGI 2.917 1000:5707, 1000:9DEF]. SQ1 uses margins 0 and 1 in 14 `add.to.pic` calls, and `set.priority(n, 2)` once [SQ1 data check, audit draw].

## SCI divergence

In SCI control lines move to a dedicated third screen, eliminating the priority/control overload and the search-downwards rule. Not audited.

## See also

- [[entities/picture]] §"Bytecode dispatch" — how `0xF2`-mode drawing writes these colors.
- [[interpreter/priority-bands]] — y → priority band assignment, and the draw comparison.
- [[interpreter/command-semantics]] §`add.to.pic` — the margin rectangle.
- [[interpreter/view-objects]] — the object flag bits this test reads.
- [[concepts/screen-layers]] — the visual and priority model.
- [[sources/5-1-picture]] — chapter provenance.
