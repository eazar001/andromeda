# Source: 5-2-PICTURE.html

The second chapter in Group 4 (PICTURE). An **independent corroborating source** for the PICTURE format already documented from 5-1: same opcode catalogue, same dual-screen model, same control-line semantics, drawn from a different canonical source (the Russian-language AGDS — Adventure Game Development Toolkit — manual, translated by Vassili Bykov).

## Scope

5-2 covers the same material as 5-1 but in a more compressed style with ASCII-diagram examples. It documents:

- Picture and priority concepts (16 colors visual; priorities 4..14 + control colors 0..3).
- Color/priority set/cancel commands (`0xF0..0xF3`).
- Polyline commands (Y-corner, X-corner, absolute) — `0xF4..0xF6`.
- Curve / relative-polyline (`0xF7`).
- Flood-fill (`0xF8`) with more specific target-selection rules than 5-1.
- Dot/pen drawing (`0xF9..0xFA`) — described as "dot parameters" / "dot plotting" rather than 5-1's "pen" terminology.
- The hex-format reference section A.2.1 (parallels 5-1's catalogue).

5-2 does NOT cover:

- Per-pixel occlusion algorithm.
- Splatter-texture mechanics (5-1's wrap-at-255 quirk, splatter texture table).
- Sign-bit polarity of `0xF7` displacements (5-2 describes relative offsets conceptually only; no bit-packing table).
- Brush-shape diagrams.
- Opcodes `0xFB..0xFE` (the A.2.1 hex reference ends at `0xFF`).

## Authorship and provenance

- **Translator** — Vassili Bykov `<vbykov@cam.org>` (visible byline line 20: "Translated from Russian by Vassili Bykov").
- **Original source** — AGDS (Adventure Game Development Toolkit) manual; Russian original author not named in the chapter header.
- **Last updated** — 27 January 1998. **Same date as [[sources/4-2-logic]]** (Peter Kelly's LOGIC source-language reference) and within the same IA-extraction window as [[sources/2-8-interpreter]] (Lance Ewing, 27 January 1998) — three chapters share that January-1998 date.
- **Provenance** — "Retrived from the Internet Archive" (line 17, original typo preserved).
- **Chapter note** (lines 20–22) — "This is from the manual of AGDS (Adventure Game Development Toolkit) which contains a good deal of information about the AGI interpreter and its data formats."
- **Meta-keywords trap** — HTML `<meta name="keywords">` lists "peter kelly" among the keywords; the visible byline is Vassili Bykov. The trap pattern is consistent across the corpus and confirmed live for the third time (after 4-5, 4-6, and 5-1).

## Informs

- [[entities/picture]] — Added a Notes paragraph on the AGDS "dot" / 5-1 "pen" terminology divergence for `0xF9`/`0xFA` (same bytecode, different framing). Added a new "Flood-fill target rule (`0xF8`)" subsection citing 5-2's more-specific wording on what `0xF8` chooses to fill (white-on-visual vs priority-4-on-priority, based on draw-mode flags).
- [[concepts/screen-layers]] §"Initial state" — Added 5-2 corroboration of the init-state colors.
- [[interpreter/control-lines]] §"Color semantics" — Added 5-2 corroboration of the four-color mapping (with "alarm barrier" wording note for green).

No new pages were created — 5-2 adds no specification surface beyond what 5-1 already covered.

## Conflicts / contradictions noticed

None of substance. The "dots" vs "pen" terminology divergence is a framing difference rather than a contradiction (both describe the same `0xF9`/`0xFA` bytecode); recorded in [[entities/picture]] as a Notes line rather than a `> [!conflict]` callout per reviewer judgment.

## Open items 5-2 resolves vs. leaves open

5-2 resolves **nothing** new — all 5-1 open items remain.

| Item | Status after 5-2 |
|------|-------------------|
| Per-pixel occlusion algorithm | NOT RESOLVED (runtime concern, not PICTURE format). |
| Object-vs-control-line interaction | NOT RESOLVED (same). |
| Wrap-at-255 splatter quirk | NOT RESOLVED (5-2 doesn't describe splatter mode). |
| `0xF7` sign-bit polarity | NOT RESOLVED (5-2 describes relative offsets but has no bit-packing table). |
| `0xFB..0xFE` reserved range | NOT RESOLVED (5-2's A.2.1 catalogue ends at `0xFF`). |
| Group-3 #3 (intra-4-4 base-point) | Not touched. |
| Group-3 #4 (`add.to.pic` margin = 4) | Not touched. |

## Notes

- **Fourth Bykov/AGDS chapter in the corpus.** Prior three: [[sources/2-6-interpreter]] (input preprocessing and `said` semantics, IA 31 August 1997); [[sources/4-4-logic]] (AGDS manual prose for the LOGIC command set, IA 4 December 1997, primary author with Lance Ewing annotation). The AGDS manual is shaping up as a parallel canonical source for Sierra-internal format details, distinct from Lance Ewing's English-original documentation (5-1, 2-4, 2-8, 4-1).
- **The 27 January 1998 IA-extraction window** is shared with [[sources/4-2-logic]] (Peter Kelly) and [[sources/2-8-interpreter]] (Lance Ewing). Three chapters from three different authors, all uploaded the same day to the Internet Archive, suggest a coordinated AGI-documentation-preservation effort by an unidentified curator in late January 1998.
- **Independent corroboration value.** 5-2's existence as an independent source for the same opcode catalogue strengthens confidence in 5-1's claims. Where the two agree (init colors, control-line colors, flood-fill behavior, opcode hex values), the `(agidev, unverified)` process tag on [[entities/picture]] could potentially be downgraded to per-claim tags during Phase C lint — but only if both sources still count as "agidev-corpus" rather than independent ground truth. Conservative reading: both are agidev-corpus regardless of authorship variety, so the process tag stays until a real PICTURE decoder is written.
