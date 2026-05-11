# Wiki Index

Distilled AGI-format knowledge base. Start here for any byte-level format question. See `WIKI.md` (repo root) for schema and conventions.

## Quick refs

_(Highest-traffic pages will be promoted here once content lands.)_

## Entities

Resource types and on-disk file formats. One page per resource.

- [[entities/dir-file]] — VOL/DIR addressing: v2 and v3 directory file layouts, entry decoding, sparse-numbering sentinel.
- [[entities/vol-file]] — VOL container format: 5-byte resource header (signature, VOL number, length) and payload structure.
- [[entities/logic]] — LOGIC resource bytecode format: 7-byte header (5-byte VOL header + 2-byte text offset), `$FF/$FE/$FD/$FC` control-flow opcodes, AGIDATA.OVL argument dispatch, and Avis-Durgan-XOR'd text-message section.
- [[entities/picture]] — PICTURE resource bytecode format: drawing-opcode catalogue `0xF0..0xFF`, dual-screen dispatch, sign-magnitude `0xF7` displacements, pen-style and splatter-texture encoding.
- [[entities/view]] — VIEW resource format: loop/cel hierarchy, RLE-compressed bitmap cel data, code-verified byte-2 mirror/transparency packing, loop mirroring with in-place Sierra-runtime mutation note.
- [[entities/sound]] — SOUND resource format: 8-byte header of four voice offsets, 5-byte note encoding (duration, tone divisor / noise selector, attenuation), v2+ and legacy v1.12 variants, PCjr four-voice playback (PC speaker renders voice 1 only).
- [[entities/object]] — OBJECT inventory file: 3-byte header (name-section offset + max animated objects), 3-byte-per-item entries (name offset + starting room, `0xFF` = carried), null-terminated name section, optional Avis-Durgan XOR encryption from v2.411 onward.
- [[entities/words-tok]] — WORDS.TOK vocabulary file: 52-byte alphabet index + variable-length prefix-share-compressed entries with `0x7F`-XOR character obfuscation. Uses Hi-Lo byte order throughout — the one AGI file that bucks the system-wide little-endian convention. Special word codes `0`/`1`/`9999` are parser-level wildcards.

## Concepts

Shared primitives referenced by multiple entities: encoding schemes, palettes, encryption keys, common header layouts.

- [[concepts/offset-encoding]] — 3-byte triplet encoding combining VOL number and byte offset; used in every directory entry.
- [[concepts/lzw-compression]] — adaptive LZW (9-/10-/11-bit codes) applied to most AGI v3 non-PICTURE resources.
- [[concepts/picture-compression]] — 4-bit color-packing scheme specific to AGI v3 PICTURE resources.
- [[concepts/agi-data-types]] — semantic data types used as AGI command parameters: variables, flags, strings, words, objects, inventory items, messages, controllers.
- [[concepts/screen-layers]] — visual / priority dual-screen model: 160×168 logical pixel grid, init colors (white visual / red priority), per-pixel encoding of bands (4..14) and control colors (0..3), drawing-mode flags.
- [[concepts/picture-rendering]] — PICTURE rendering algorithms code-verified against Lance Ewing's reference decoder: additive-fixed-point line drawing with direction-sensitive rounding, BFS flood-fill (4000-entry queue), brush plotting, splatter texture masking with wrap-at-255.
- [[concepts/rle-encoding]] — VIEW-cel RLE: chunk byte (high nibble = color, low nibble = run length 1..15), `0x00` row terminator, trailing-transparency padding rule.
- [[concepts/ega-palette]] — IBM EGA 16-color palette table; explains why priority-screen 0..3 are control colors and 4..14 are depth bands.
- [[concepts/pcjr-sound-encoding]] — TI SN76496A voice primitives: 10-bit tone frequency divisor, 2-bit pre-selected noise frequencies (+ borrow-voice-3 mode), 4-bit attenuation (A0=bit3=16 dB → A3=bit0=2 dB). Shared by every 5-byte note in [[entities/sound]].

## Interpreter

The LOGIC VM and runtime model: opcode tables, event loop, priority bands, object state, screen state.

- [[interpreter/overview]] — high-level VM-model hub; one paragraph per subsystem with links into the detailed pages.
- [[interpreter/variables-and-flags]] — reserved `var(0)`–`var(26)` and `flag(0)`–`flag(15)`: complete assignment table, semantics, shared-namespace scoping.
- [[interpreter/event-loop]] — eleven-step per-frame cycle: input poll, LOGIC execution, post-LOGIC cleanup, rendering, room-transition check, with per-step variable/flag state management.
- [[interpreter/memory-layout]] — runtime heap organization: 256-byte variable region, 32-byte flag region, string buffers, jump table, encryption key, and loaded resources, in heap order.
- [[interpreter/input-parsing]] — player-input preprocessing (punctuation/case/space normalization, vocabulary lookup) and `said` test pattern matching (wildcards `1` and `9999`, equality, at-most-once-per-cycle semantics).
- [[interpreter/command-evolution]] — version-conditional command argument-count rules for LOGIC bytecode decoding (`quit`, `print.at`, `print.at.v`, unknown #176) plus command-count summary by interpreter version.
- [[interpreter/commands]] — full opcode catalogue: 18 test commands (`$01..$12`) and 182 action commands (`$00..$B5`) with argument counts and per-argument types.
- [[interpreter/command-semantics]] — selected behavioral semantics for high-value opcodes from 4-4: arithmetic edge cases, resource auto-discard rule, `new.room` eleven-step procedure, `release.loop` direction tables, `add.to.pic` margin gap, base-point and `set.upper.left` conflicts with 4-3, AGDS surface syntax, the `said` algorithm.
- [[interpreter/priority-bands]] — y → priority eleven-band auto-assignment table from `release.priority`. Resolves the long-dangling forward-ref from [[interpreter/overview]].
- [[interpreter/control-lines]] — black/blue/green/cyan control-line semantics on the priority screen (barrier / conditional barrier / alarm / surface) and the search-downwards algorithm that recovers a priority band under a control-line pixel. Resolves the [[interpreter/control-lines]] forward-ref from [[interpreter/overview]].
- [[interpreter/view-objects]] — runtime VIEW object table: 43-byte SQ2 entry structure (position, view/loop/cel pointers, size, step/cycle timing, direction, motion type, cycle type, priority, 16-bit flags), hot-spot reference point, and the four collision-test commands (`posn`, `right.posn`, `center.posn`, `obj.in.box`). Resolves forward-refs from [[interpreter/memory-layout]] and [[interpreter/event-loop]].
- [[interpreter/debug-modes]] — built-in interpreter debugger: ALT-D and per-game magic-phrase activation, debug command vocabulary, command-trace mode (Scroll-Lock), `flag(10)` activation flag.

## Sources

One page per ingested AGI Specification chapter, with a short summary and links to the entity/concept pages it informed.

- [[sources/3-1-files]] — Directory files and VOL/DIR addressing scheme (AGI v2 and v3).
- [[sources/3-2-files]] — VOL file container format and 5-byte resource header.
- [[sources/3-3-files]] — AGI v3 resource storage: 7-byte headers, LZW compression, PICTURE compression.
- [[sources/3-4-files]] — Sample-code reference table (Lance Ewing's historical decoders). Bibliographic only; no new format content.
- [[sources/2-1-interpreter]] — Interpreter overview chapter (VM model at headline depth; subsystem detail deferred).
- [[sources/2-2-interpreter]] — Reserved variables/flags assignment tables and the eleven-step interpreter work cycle.
- [[sources/2-3-interpreter]] — Semantic data types: variables, flags, strings, words, objects, inventory items, messages.
- [[sources/2-4-interpreter]] — Runtime heap layout (memory-resident debugger view). Single-arena memory model with code, fixed state, and dynamic resources sharing one heap.
- [[sources/2-5-interpreter]] — Game IDs, loaders, and interpreter-binary 128-byte rolling-XOR encryption. Out-of-scope reference (distribution layer, not game-data format); no entity or concept pages derived.
- [[sources/2-6-interpreter]] — Input preprocessing pipeline and `said` test semantics. Sourced from the AGDS Russian-language manual (translated by Vassili Bykov), retrieved from the Internet Archive.
- [[sources/2-7-interpreter]] — Hobbyist-compiled cross-reference of AGI games to interpreter versions (v2: 2.089–2.936; v3: 3.002.086–3.002.149). Out-of-scope reference; empirical anchor for version-conditional format claims.
- [[sources/2-8-interpreter]] — Interpreter-version fingerprint table (binary sizes, command counts, OBJECT/LZW flags) and post-table observations: command argument-count discrepancies, v3 LOGIC-message-no-encryption and 4-bit PICTURE color-codes, string allocation. Closes Group 2.
- [[sources/4-1-logic]] — LOGIC resource v2 format: 7-byte header, bytecode structure with `if/else/not/or` control flow, AGIDATA.OVL argument dispatch, `said` variable-argument encoding, Avis-Durgan-XOR'd text section, and the original Manhunter: SF ASM decode loop. Lance Ewing, IA, August 1997.
- [[sources/4-2-logic]] — LOGIC source-language syntax: action-command form, `if`/`else` and test commands, nine source-syntax argument types (with one-letter prefixes), `said` source form, labels/`goto`, comments, preprocessor directives. Authoring-side reference; Controller delta applied to [[concepts/agi-data-types]]. Peter Kelly, IA, January 1998.
- [[sources/4-3-logic]] — opcode catalogue: 18 test commands (`$01..$12`) and 182 action commands (`$00..$B5`) with argument counts and types. Resolves the long-standing [[interpreter/commands]] forward-ref originally created in the 2-1 ingest. Peter Kelly, IA, March 1998.
- [[sources/4-4-logic]] — AGDS-manual prose for the command set: arithmetic edge cases, resource auto-discard, `new.room` procedure, priority-band y-boundaries (resolves [[interpreter/priority-bands]]), `release.loop` direction tables, `said` algorithm corroborating 2-6, and two surfaced conflicts (intra-chapter base-point inconsistency; `$9B` argument-count disagreement with 4-3). AGDS / Vassili Bykov / Lance Ewing, IA, December 1997.
- [[sources/4-5-logic]] — KQ4 Room 7 sample LOGIC code: five side-by-side BOOK-pseudo-code vs. GAME-bytecode samples with commentary on author-vs-compiler differences. Sources-only ingest (validation case, not format spec). Anonymous, IA, August 1997.
- [[sources/4-6-logic]] — Bibliographic reference table for five Lance Ewing / Peter Kelly source files at `AGI_Specifications/Code/` (`logic.c`/`.h`, `agifiles.c`/`.h`, `agicommands.pas`). Sources-only ingest; **closes Group 3 (Logic)**.
- [[sources/5-1-picture]] — PICTURE resource bytecode format chapter: drawing opcodes `0xF0..0xFF`, dual-screen model, control-line color semantics, search-downwards priority recovery, sign-magnitude `0xF7` displacements, pen-style and splatter-texture encodings. **Opens Group 4 (PICTURE)**. Lance Ewing, IA, 5 December 1997.
- [[sources/5-2-picture]] — AGDS-manual translation covering the same PICTURE format from a Russian-language source. Corroborates 5-1's init colors, control-line color mapping, and opcode catalogue; refines `0xF8` flood-fill target rule. Independent source, no new specification surface. Vassili Bykov (translator), AGDS, IA, 27 January 1998. **Fourth Bykov/AGDS chapter in the corpus.**
- [[sources/5-3-picture]] — "Sample Code" chapter pointing at two reference C implementations vendored at `AGI_Specifications/Code/`: `showpic.c` (working PICTURE viewer, ~650 lines) and `picv3-v2.c` (v3→v2 transcoder, 67 lines). Resolves `0xF7` sign-bit polarity, wrap-at-255 splatter quirk, `0xFB..0xFE` reserved-range; surfaces a 4-position conflict in the splatter offset table between 5-1 prose and showpic.c. Page-level `(agidev, unverified)` tags downgraded across PICTURE pages — showpic.c is now the validation surface. Lance Ewing, IA. **Closes Group 4 (PICTURE).**
- [[sources/6-1-view]] — VIEW resource format chapter: three-level container, RLE cel encoding, loop mirroring, optional close-up descriptions. Validation-case ingest cross-checked against `resource/view.py` and `gfx/view_render.py`; spec's cel-header byte-2 wording (ambiguous nibble ordering + a "Bit 1" typo) was overridden by the code-verified layout. Peter Kelly, IA, 5 October 1997. **Opens Group 5 (VIEW).**
- [[sources/6-2-view]] — VIEW *object* table and runtime sprite state: 43-byte SQ2 entry structure (per-object position, animation, motion, priority, 16-bit flags) and four collision-test commands (`posn`, `right.posn`, `center.posn`, `obj.in.box`) referencing the object hot-spot pixel. Entry size is interpreter-version-specific; many bytes and flag bits marked "??" in the spec (unknown purpose). Lance Ewing, IA, 31 August 1997. **Second of three VIEW chapters.**
- [[sources/6-3-view]] — "Sample Code" chapter: single-row pointer at `viewview.pas` (Peter Kelly, Borland Pascal 7, from AGIhack 2.0) vendored at `AGI_Specifications/Code/`. No new specification surface; the code independently verifies cel-header byte-2 nibble layout, RLE chunk structure, `0x00` row termination, and horizontal-doubling display width as documented on [[entities/view]]. Mirroring style differs (in-place mutation in `viewview.pas` vs. deferred per-render in andromeda); both spec-conformant. **Closes Group 5 (VIEW).**
- [[sources/7-1-sound]] — SOUND resource format chapter: PCjr TI SN76496A four-voice model, 8-byte header of per-voice offsets, 5-byte note encoding (duration + tone-divisor-or-noise-selector + attenuation), v2+ format with sketch of legacy v1.12. Authoritative bit layouts live in Appendix 1; main-text byte-order prose is imprecise. **Opens Group 6 (SOUND).** Lance Ewing, IA, 18 August 1997.
- [[sources/7-2-sound]] — "Sample Code" closer: four-row bibliographic table indexing `oldplay.c` (Lance Ewing), `play.c` (Jens Christian Restemeier + Lance Ewing edits), `adlib.c`/`adlib.h` (Kevin A. Lee). No new format claims; code-level findings: (1) `play.c:107` `* 6` duration scaling is the first concrete clue to the 16-bit duration field's time unit; (2) intra-chapter frequency-base disagreement — `play.c:116` uses 111860 (matching spec) but `oldplay.c:91` uses 99320 (~12% lower, unexplained); (3) `play.c:9-10` notes the sample "was written before we worked out the details on the fourth voice and the volume control." Flag-signal semantics for `$63 sound` remain unvalidated. **Closes Group 6 (SOUND).**
- [[sources/8-1-otherdata]] — OBJECT inventory file specification: 3-byte header + 3-byte-per-item entries + null-terminated name section, with version-conditional Avis-Durgan XOR (added v2.411). Shared key with v2 LOGIC text encryption. Flags a code-vs-spec offset discrepancy: `resource/objects.py:31` uses `+ 5` where spec and `object.pas` use `+ 3`. **Opens Group 7 (Other).** Lance Ewing, IA, 31 August 1997.
- [[sources/8-2-words-tok]] — WORDS.TOK vocabulary-file specification: 26-entry alphabet index + variable-length prefix-share entries + `0x7F`-XOR character obfuscation + high-bit end-of-word marker + 2-byte big-endian word numbers. Notable: the only AGI file using Hi-Lo (big-endian) byte order, called out explicitly by the spec. Caught a draft error where the subagent reversed the word-number bytes — fixed pre-apply. Lance Ewing, IA, 31 August 1997.
- [[sources/8-3-samplecode]] — Sample-code closer: bibliographic pointers at `object.pas` and `words.pas` (both Peter Kelly). Validates the 8-1 and 8-2 entity pages with concrete line citations; surfaces the `resource/objects.py:31` `+ 5` vs spec `+ 3` discrepancy as an open item rather than treating code as authoritative. **Closes Group 7 (Other).**
- [[sources/1-1-introduction]] — Cover-page / manifesto for the AGI Specifications corpus (Peter Kelly, IA 27 January 1998). Bibliographic only. **Opens Group 8 (Intro/Info).**
- [[sources/1-2-whatsnew]] — Changelog of edits to the Specifications document itself, Aug 1997 – Jul 1998. Editorial only; no new format claims. Notable entry: 27 January 1998 AGDS-deduplication restructuring is the provenance anchor for several wiki source pages with that IA date.
- [[sources/9-1-info]] — Contributor roll (13 hobbyist developers with email + website + activity summary). Bibliographic; provenance anchor for authorship questions. Last updated 27 January 1998.
- [[sources/9-2-agds]] — Historical narrative of the AGDS (Adventure Game Development System) toolkit by Alex Simkin and Serge Lapin (~1990–91); Vassili Bykov as English translator. Provenance anchor for the three previously-ingested AGDS-sourced chapters (2-6, 4-4, 5-2). No new format claims.
- [[sources/9-3-making-of-thunderstorm]] — Fan postmortem of *Thunderstorm* by A. V. Horev (~1991, Bykov-translated). Anecdotal workflow narrative; corroborates existing event-loop, flag(5)/flag(6), and `new.room` semantics without adding new format surface. **Closes Group 8 (Intro/Info) and Phase B (Bootstrap ingest).**
