# Source: 2-7-Interpreter.html

Chapter 2.7 from the AGI Specifications, "Version Control." A hobbyist-maintained release/version cross-reference compiled by `mikeph@concentric.net` ("Version 4.0" of the document, with "What's New" sections going back to v2.0). "Retrived from the Internet Archive" annotation per the chapter header; no formal author byline. Vendored at `AGI_Specifications/Specifications/2-7-Interpreter.html`. Bibliographic for this wiki's scope — no format or VM specification content.

## Scope

Three redundant tables (sorted by game / by interpreter version / by date) plus a "Known Int. Ver." summary cataloging which AGI games shipped with which interpreter versions. No byte-level facts, no opcode tables, no event-loop semantics. What the chapter does establish, distilled for use as an empirical anchor for the wiki's version-conditional claims:

- **AGI v2 interpreter versions seen in the wild**: 2.089, 2.272, 2.411, 2.425, 2.426, 2.435, 2.439, 2.440, 2.915, 2.917, 2.936.
- **AGI v3 interpreter versions seen in the wild**: 3.002.086, 3.002.098, 3.002.102, 3.002.107, 3.002.149.
- **Game coverage**: King's Quest 1–4 (+KQ4 Demo), Black Cauldron, Gold Rush, Leisure Suit Larry 1, Mixed-Up Mother Goose, Manhunter 1–2, Police Quest 1, Space Quest 1–2, Christmas 1986 (XM86), AGI Demo.
- **Chronological span**: 1986-11-08 (King's Quest 3 v1.01) through 1989-08-17 (Manhunter 2 v3.03), per each game's about-menu dates [2-7-Interpreter.html, "Note: Dates are from about menu, and not the file date on the files"].
- **Multi-version re-releases**: many games shipped under more than one interpreter version. Examples: KQ1 under 2.272 and 2.425/2.917; KQ2 under 2.411, 2.426, and 2.917; SQ1 under 2.089, 2.426, and 2.917; SQ2 under 2.915, 2.917, and 2.936. Implication for the wiki: a single game's resource data may be paired with different interpreter binaries across distributions, so "game = single AGI version" is not safe to assume.

## Informs

No wiki entity or concept pages. This source page serves as an empirical anchor for the wiki's existing version-conditional claims:

- [[concepts/agi-data-types]] — per-version string-allocation table (12 buffers for 2.089/2.411 and 3.002.107/3.002.149; 24 for "intermediate versions"). 2-7 makes "intermediate" concrete: {2.272, 2.425, 2.426, 2.435, 2.439, 2.440, 2.915, 2.917, 2.936, 3.002.086, 3.002.098, 3.002.102}. The string-allocation paragraph in `agi-data-types` cross-links here.
- [[entities/vol-file]] — v2 (5-byte resource header) vs. v3 (7-byte resource header with PICTURE flag). 2-7's enumeration structurally confirms the split: every `3.002.xxx` is v3; every `2.xxx` is v2.

Forward breadcrumb: Group 3 (Logic) will need this enumeration when documenting the "about four AGI commands have changed argument count as the interpreter developed" hint from [[sources/2-5-interpreter]] — that change-of-argument-count is presumably indexed by some subset of the versions listed here.

## Notes

- **Provenance.** No formal byline; the chapter is signed only by `mikeph@concentric.net` ("If you have a game that is AT ALL different from the ones listed, e-mail me"). The document was actively maintained as a community submission ("Please summit a copy for the Version Control archive"). "Retrived from the Internet Archive" annotation matches the pattern seen on 2-4 and 2-6.
- **Authorship snapshot for the corpus so far**: 2-1, 2-2, 2-3 are Peter Kelly (assumed); 2-4 is Lance Ewing solo (IA); 2-5 is Lance Ewing primary + Peter Kelly + Anders M Olsson; 2-6 is AGDS manual translated by Vassili Bykov (IA); 2-7 is hobbyist `mikeph@concentric.net` (IA). Four of seven Group-2 chapters are non-Kelly contributions; three are explicitly retrieved from the Internet Archive.
- **Out-of-scope for this wiki's mission.** The chapter contains no byte-level format details and no VM specification. The subagent recommended *no ingest at all*; main session diverged and kept a source page because (a) consistency with the 2-5 source-page-only precedent for out-of-scope chapters and (b) the version enumeration is referentially useful — it grounds the abstract "intermediate versions" phrasing in [[concepts/agi-data-types]] and supplies the Group-3 reviewer with concrete versions to index per-opcode-argument-count differences against.
- **Date notation note.** Dates are MM/DD/YY US format taken from each game's about-menu, not file modification time [2-7-Interpreter.html, header note]. About-menu dates may post-date file modification by some interval for late patches. Many rows have `Unknown` or `??/??/??`; some games have `?.??` for game version. This is hobbyist-compiled data, not exhaustive Sierra release records.
- **Mailing-list/contact info** in the chapter is 1990s-era and almost certainly defunct; ignore.
- No conflicts observed against existing pages.
