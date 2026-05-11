# 6-3-VIEW: Sample Code

**Chapter:** §6.3 Sample Code
**Source:** `AGI_Specifications/Specifications/6-3-VIEW.html`
**Author:** Peter Kelly (chapter byline implicit; the single listed entry attributes the referenced code to Peter Kelly)
**Date:** None in chapter HTML.

## Scope

Sample-code index page only. The chapter contains a single one-row table pointing at [`AGI_Specifications/Code/viewview.pas`](../../AGI_Specifications/Code/viewview.pas), described as "Unit from AGI hack to display VIEWs". No normative specification content — no new byte-level layouts, no new runtime behavior, no new opcodes.

Bibliographically parallel to [[sources/3-4-files]], [[sources/4-6-logic]], and [[sources/5-3-picture]] — each "Sample Code" closer chapter is a pointer table rather than a specification.

## Reference implementation

`viewview.pas` is a Borland Pascal 7 unit from AGIhack 2.0 that implements an interactive VIEW viewer. It is the canonical reference parser for the VIEW on-disk format and was used to code-verify several byte-level claims on [[entities/view]] during Group 5 ingest.

Procedures of interest:

- `ReadViewInfo` ([viewview.pas:152-212](../../AGI_Specifications/Code/viewview.pas)) — view/loop/cel header parser. Lines 200-205 are the canonical reference for cel header byte 2 decomposition: `TransCol := curbyte AND $0F` (low nibble = transparency) and `if curbyte >= $80 then Cel.Mirror := TRUE` (bit 7 = mirror flag). Matches `resource/view.py:89-90`.
- `LoadCel` ([viewview.pas:91-142](../../AGI_Specifications/Code/viewview.pas)) — RLE row decoder. Lines 110-114 split each non-zero byte into `ChunkCol := (curbyte AND $F0) div $10` (high nibble = color) and `ChunkLength := curbyte AND $0F` (low nibble = count); line 111 treats `0x00` as the row terminator. Matches `resource/view.py:103-106`.
- `LoadCel` mirroring ([viewview.pas:127-137](../../AGI_Specifications/Code/viewview.pas)) — when `Cel.Mirror` is set *and* `LoopOccur[loopno] = 2` (i.e. this is the second loop sharing a single offset entry), the just-finished row is reversed in-place into the cel data buffer before advancing. This is the in-place-mutation rendering style noted on [[entities/view]] §Loop mirroring. Andromeda's read-only decoder defers the flip to render time instead ([`gfx/view_render.py:7`](../../gfx/view_render.py), `mirrored = cel.mirror and loop_idx != cel.non_mirror_idx`); both produce the same on-screen result.

## Validation outcome

All byte-level VIEW format claims on [[entities/view]] are now corroborated by two independent implementations (Peter Kelly's `viewview.pas` and andromeda's `resource/view.py` + `gfx/view_render.py`) plus empirical SQ1 round-trip. No conflicts introduced by 6-3. No 6-2 open items resolved by 6-3.

## See also

- [[entities/view]] — VIEW resource format (the page whose claims `viewview.pas` validates).
- [[concepts/rle-encoding]] — cel-data RLE specifics, also verified against `viewview.pas:110-114`.
- [[sources/6-1-view]] — opens Group 5.
- [[sources/6-2-view]] — second VIEW chapter.

**Closes Group 5 (VIEW).**
