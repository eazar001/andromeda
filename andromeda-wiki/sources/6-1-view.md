# 6-1-VIEW.html

**Chapter:** 6.1 VIEW Resource Format
**Author:** Peter Kelly (`ptrkelly@ozemail.com.au`)
**Last updated:** 5 October 1997
**Provenance:** Retrieved from the Internet Archive; vendored at `AGI_Specifications/Specifications/6-1-VIEW.html`.

## Summary

Specifies the on-disk binary format of VIEW resources — RLE-compressed bitmap sprite/animation graphics. Covers the three-level container (view header → loop headers → cel headers + RLE pixel rows), cel-header transparency and mirror flag packing, the RLE chunk encoding, loop mirroring (one loop as a horizontal flip of another), and the optional inventory-close-up description string.

This is a Group 5 (VIEW) **validation-case** ingest: andromeda already has a working VIEW decoder ([`resource/view.py`](../../resource/view.py), [`gfx/view_render.py`](../../gfx/view_render.py)) that round-trips real Sierra game data (SQ1), so every byte-level claim from this chapter could be cross-checked against running code. All claims in [[entities/view]] are code-verified.

## Pages informed

- [[entities/view]] — full VIEW format spec with corrected, code-verified byte-2 bit layout.
- [[concepts/rle-encoding]] — VIEW-cel-specific RLE: chunk byte, row terminator, transparency padding rule.
- [[concepts/ega-palette]] — referenced (but not defined) by the chapter's "color index 0..15" language.
- [[concepts/screen-layers]] — closes the "Visual-screen masking by transparent cels" open item by documenting where transparency lives in the cel header.

## Notable findings

- **Cel header byte 2 wording is unreliable.** The spec describes the byte ambiguously ("first four bits / last four bits") and contains a typo in the mirroring section ("Bit 1" used for both the flag and a loop-index bit). The actually-correct layout — high nibble = mirror info, low nibble = transparency; within the high nibble, MSB = mirror flag, low 3 bits = non-mirror loop index — was taken from the andromeda decoder, which was verified empirically against AGI Studio's renderer and SQ1 game files [resource/view.py:83-90]. Documented at [[entities/view]] §"Byte 2 layout".
- **In-place cel mutation by the Sierra interpreter.** The spec explains why each cel stores a *loop index* rather than just a flip-or-not bit: the original interpreter mutates the cel data in memory as it renders different loops, repurposing the index field as a "currently-oriented-for" marker. Andromeda's read-only decoder does not perform this mutation. Documented at [[entities/view]] §"Loop mirroring" and §"Reserved-space requirement".
- **Spec is silent on the EGA palette itself.** The chapter (and the rest of `AGI_Specifications/`) uses "color index 0..15" without enumerating the RGB values. The new [[concepts/ega-palette]] page sources values from [gfx/palette.py].

## Related sources

- [[sources/5-1-picture]] / [[sources/5-3-picture]] — PICTURE format chapters; share the EGA palette and the screen-composition target but use a different (bytecode) encoding.
- [[sources/3-2-files]] — VOL chunk header that wraps every VIEW resource on disk.

## Open items

- VIEW description string parsing (offset is read; body is not).
- Per-pixel occlusion procedure when a cel pixel sits over a control-line pixel on the priority screen. Spec defines neither side completely; deferred to ScummVM cross-check or later VIEW chapters.
