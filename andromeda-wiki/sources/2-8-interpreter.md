# Source: 2-8-Interpreter.html

Chapter 2.8 from the AGI Specifications, "Interpreter Version Differences." Written by Lance Ewing <be@ihug.co.nz>, last updated 27 January 1998, "Retrived from the Internet Archive" (sic) per the chapter header. Vendored at `AGI_Specifications/Specifications/2-8-Interpreter.html`. Comprehensive version-metadata reference: 14-row interpreter fingerprint table plus four sections of post-table observations covering command argument-count discrepancies, v3-specific format differences, and string-allocation uncertainty.

## Scope

### Interpreter version fingerprint table (verbatim)

| Version | Interpreter file size | AGIDATA.OVL size | # Commands | OBJECT encrypted | LZW in VOL files |
|---|---|---|---|---|---|
| 2.089 | 34305 | 6656 | 155 | No | No |
| 2.272 | 34816 | 6656 | 161 | No | No |
| 2.411 | 38400 | 7680 | 169 | Yes | No |
| 2.435 | 38400 | 7680 | 169 | Yes | No |
| 2.439 | 38400 | 7680 | 169 | Yes | No |
| 2.440 | 38400 | 7680 | 169 | Yes | No |
| 2.915 | 39424 | 8192 | 173 | Yes | No |
| 2.917 | 39424 | 8192 | 173 | Yes | No |
| 2.936 | 39424 | 8192 | 175 | Yes | No |
| 3.002.086 | 40866 | 8064 | 177 | Yes | Yes |
| 3.002.098 | 40898 | 8080 | 181 | Yes | Yes |
| 3.002.102 | 40898 | 8080 | 181 | Yes | Yes |
| 3.002.107 | 40962 | 8080 | 181 | Yes | Yes |
| 3.002.149 | 40520 | 7488 | 181 | Yes | Yes |

This is the most authoritative version-by-version fingerprint of the AGI interpreter binaries known to exist. Useful for identifying an unknown interpreter EXE by file-size match.

### Post-table observations (verbatim)

1. The number of supported commands grew monotonically with the interpreter version; the last eleven commands have no documented names.
2. There are two main AGI versions, v2 and v3.
3. Early AGI v2 games (2.089, 2.272) did *not* encrypt the OBJECT file with the "Avis Durgan" string.
4. AGI v3 games use adaptive LZW to compress LOGIC, VIEW, and SOUND files.

### Command-argument discrepancies [§COMMAND ARGUMENT NUMBER DESCREPENCIES]

Four commands changed argument count across versions:

- `quit`: 0 args in 2.089; 1 arg in all later versions.
- `print.at`: 3 args in versions "2.089 - 2.400"; 4 args in later versions. (The spec's "2.400" is not a real version — see [[interpreter/command-evolution]] for the conflict callout.)
- `print.at.v`: same 3→4 transition at the same boundary.
- Unknown command #176: 1 arg in 3.002.086; 0 args in all later v3 versions.

### AGI version three differences [§AGI VERSION THREE]

Two v3-specific format changes beyond LZW adoption:

- **LOGIC text messages are not Avis-Durgan-encrypted in v3.** The spec rationalizes: "since there is no need to do this because it is compressed anyway." This *implicitly* establishes that **AGI v2 LOGIC files DO encrypt their text-message section with Avis Durgan** — a new wiki-relevant claim for Group 3 (Logic) ingest of the LOGIC entity. (Note: this is separate from the OBJECT-file XOR encryption documented in observation 3 above; both use the same "Avis Durgan" key but apply it to different resources at different lifecycle stages.)
- **PICTURE bytecode color encoding**: opcodes 0xF0 (set visual color) and 0xF2 (set priority color) use 4-bit values in v3, vs. 8-bit values in v2. Relevant to Group 4 (Picture) PICTURE-bytecode decoding.

### Number of strings [§NUMBER OF STRINGS]

The chapter states only: "All interpreters have at least 12 strings. Most interpreters have space for 24 strings but I don't know if the extra space is used for strings or not." This is *less specific* than the per-version mapping in [[concepts/agi-data-types]], which sources its detail from 2-3, not 2-8. No deltas to the data-types page from this ingest.

## Informs

### New page

- [[interpreter/command-evolution]] — version-conditional command-argument-count rules for LOGIC bytecode decoding, plus command-count summary by version.

### Forward breadcrumbs (no deltas applied, but future ingests should cite this chapter)

- [[entities/object]] (Group 7) — OBJECT encryption was introduced in v2.411 and applies to all v3; absent in 2.089 / 2.272. A decoder must conditionally apply Avis-Durgan XOR based on interpreter version.
- [[entities/logic]] (Group 3) — AGI v2 LOGIC files encrypt their text-message section with Avis Durgan; v3 LOGIC files do *not* (the per-resource LZW compression supersedes per-message encryption). This is implicit in the chapter's text but is the only direct evidence of v2 LOGIC encryption in the corpus so far.
- [[entities/picture]] (Group 4) — PICTURE bytecode opcodes 0xF0 (visual color) and 0xF2 (priority color) use 4-bit color values in v3 vs. 8-bit in v2.
- [[concepts/lzw-compression]] — already documents v3 adoption; 2-8 confirms LZW is *the* boundary between v2 and v3 for LOGIC/VIEW/SOUND resources (PICTURE has its own per-resource compression scheme, per 3-3).

## Notes

- **Authorship.** Lance Ewing <be@ihug.co.nz>, "Retrived from the Internet Archive" (sic). Last updated 27 January 1998. Same provenance pattern as 2-4 (Lance Ewing solo, IA, 31 August 1997). Lance Ewing is the most prolific Group-2 contributor: solo author of 2-4 and 2-8, primary author of 2-5.

- **Authorship snapshot for the corpus (Group 2 complete):**
  - 2-1, 2-2, 2-3: Peter Kelly (assumed; not directly verified against HTML).
  - 2-4: Lance Ewing solo, IA, 31 August 1997.
  - 2-5: Lance Ewing primary + Peter Kelly + Anders M Olsson, 3 March 1998.
  - 2-6: AGDS manual translated by Vassili Bykov, IA, 31 August 1997.
  - 2-7: hobbyist `mikeph@concentric.net`, IA, no date.
  - 2-8: Lance Ewing solo, IA, 27 January 1998.

  Five of eight Group-2 chapters are explicitly IA-provenance; five are non-Peter-Kelly contributions. The "Peter Kelly's AGI Specifications" framing in CLAUDE.md and elsewhere is more accurately "Peter Kelly's curated AGI specifications corpus."

- **Discrepancy with [[sources/2-7-interpreter]]'s version enumeration.** 2-7 includes 2.425 and 2.426 (per its game-cross-reference tables: KQ1 v2.0F-1987 uses 2.425; KQ2 v2.2 / SQ1 v2.2 use 2.426). 2-8's version table does NOT include either of these — only 2.411, 2.435, 2.439, 2.440 between 2.272 and 2.915. This is consistent with the two authors working from different evidence bases (Lance Ewing's personal interpreter collection vs. mikeph's community submissions). Where the two sources disagree, treat all enumerated versions as legitimately existing in the wild, but treat 2-8 as authoritative for binary fingerprints (file sizes, command counts) since 2-8 has fingerprint columns and 2-7 does not.

- **The "2.400" typo.** The chapter text states `print.at` has 3 args for "versions 2.089 - 2.400". `2.400` does not exist in either 2-7 or 2-8's enumeration. Most plausible reading: typo for `2.440`. [[interpreter/command-evolution]] flags this as a `> [!conflict]` callout pending Group 3 verification against ScummVM or AGI Studio.

- **Forward-refs not resolved.** This is the final Group-2 chapter. The five overview forward-refs (`commands`, `priority-bands`, `control-lines`, `view-objects`, `debug-modes`) remain dangling at Group-2 close. All five are deferred to Group 3 (Logic) and later groups. Phase C lint will need to either resolve them or accept them as legitimately-deferred placeholders.

- **No conflicts** observed against existing wiki pages. 2-8's claims either extend (string allocation, command count) or confirm (OBJECT encryption, LZW v3 adoption) existing pages without contradiction. The 2.400 typo and the 2-7/2-8 enumeration mismatch are flagged as `> [!conflict]` in command-evolution and as a Notes paragraph here.
