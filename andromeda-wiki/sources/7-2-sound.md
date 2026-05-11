# 7.2-SOUND: Sample Code

**Chapter:** §7.2 Sample Code
**Source:** `AGI_Specifications/Specifications/7.2-SOUND.html`
**Authors:** Kevin A. Lee (`adlib.c`/`adlib.h`), Lance Ewing (`oldplay.c`), Jens Christian Restemeier (`play.c`, adjusted by Lance Ewing).
**Date:** None in chapter HTML; retrieved from Internet Archive.

## Scope

Sample-code index page only. The chapter is a 4-row bibliographic table pointing at four files vendored at `AGI_Specifications/Code/`. No prose, no normative specification surface.

Bibliographically parallel to [[sources/3-4-files]], [[sources/4-6-logic]], [[sources/5-3-picture]], and [[sources/6-3-view]] — each "Sample Code" closer chapter is a pointer table rather than a specification.

## Reference implementations

- **`oldplay.c`** (Lance Ewing) — Direct PCjr-style player using Adlib/Sound Blaster FM (via `adlib.c`) or PC speaker. Parses the 8-byte `SNDHeader` and iterates 5-byte notes ([oldplay.c:22-29](../../AGI_Specifications/Code/oldplay.c)).
- **`play.c`** (Jens Christian Restemeier; Lance Ewing edits) — Converts AGI SOUND into MIDI, then plays back via Allegro. Reads the 8-byte header as four 16-bit little-endian voice offsets ([play.c:102-103](../../AGI_Specifications/Code/play.c)) and iterates 5-byte notes per voice ([play.c:105-140](../../AGI_Specifications/Code/play.c)).
- **`adlib.c`/`adlib.h`** (Kevin A. Lee) — Low-level Adlib FM-register interface used by `oldplay.c`; format-agnostic, not SOUND-specific.

## Notable findings

- **Duration time-unit is code-inferred, not spec-stated.** `play.c:107` computes `dur = (snddata[pos+0] | (snddata[pos+1]<<8)) * 6` before emitting a MIDI delta — the first concrete clue to the 16-bit duration field's units. The `* 6` is unexplained in the source, but is consistent with a duration unit of one playback tick at the interpreter's ~20 Hz frame rate scaled to MIDI's 192-PPQN convention. Resolves [[sources/7-1-sound]] open item only partially: the scale is now plausible but not authoritative.
- **Intra-chapter frequency-base discrepancy.** `play.c:116` uses `111860.0 / freq` (matching the spec's 1/32-of-3.579-MHz claim, [[concepts/pcjr-sound-encoding]]), but `oldplay.c:91` uses `return (99320 / fileData);` — a ~12% lower constant. Two reference programs in the *same* chapter disagree; play.c corroborates the spec, oldplay.c is the outlier. Unexplained in either source.
- **Volume-control and multi-voice handling were incomplete at sample-code vintage.** `play.c:9-10` header comment: *"This program was written before we worked out the details on the fourth voice and the volume control."* Contextualizes (but does not resolve) the [[sources/7-1-sound]] open item on `var(23)` ↔ per-note attenuation mapping.
- **`sound` command flag-signal semantics remain unvalidated.** Neither reference player implements LOGIC-level flag signaling on completion. Open item from 7-1 is not closed by 7-2.

## Validation outcome

No new format claims to validate; SOUND remains the resource type with the weakest code-validation coverage in the corpus. Among the two playback implementations vendored here, `play.c` is the better cross-reference for the spec's frequency formula; `oldplay.c` is suspect on its frequency constant and should not be trusted as a sole source. Recommended future cross-check: ScummVM `engines/agi/sound_pcjr.cpp`.

## See also

- [[entities/sound]] — SOUND resource format (the page this chapter informs by code reference).
- [[concepts/pcjr-sound-encoding]] — shared encoding primitives.
- [[sources/7-1-sound]] — opens Group 6.

**Closes Group 6 (Sound).**
