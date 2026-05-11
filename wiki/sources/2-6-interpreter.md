# Source: 2-6-Interpreter.html

Chapter 2.6 from the AGI Specifications, "Processing Parsing the Player Input." Sourced from the AGDS (Adventure Game Development Toolkit) Russian-language manual, translated by Vassili Bykov, retrieved from the Internet Archive. The chapter is excerpted from AGDS's description of the `said` LOGIC command (section 4.3 of that manual). Vendored at `AGI_Specifications/Specifications/2-6-Interpreter.html`.

## Scope

End-to-end specification of player-input processing:

- **Four-step preprocessing**: punctuation removal, lowercase normalization, multi-space collapsing, and word-by-word vocabulary lookup using "the longest character sequence matching the entered" (algorithm phrasing under-specified — see Notes).
- **Failure handling**: a vocabulary miss sets `var(9)` to the 1-indexed position of the failed word and aborts preprocessing; `flag(2)` is left unset.
- **Success post-processing**: zero-coded entries are discarded (vocabulary entries with code 0 are filler/ignored words); `flag(2) = 1`; `flag(4) = 0`.
- **The `said` test command**: pattern-matching predicate against the parsed code sequence `V(1)..V(m)`. Preconditions `flag(2) = 0` or `flag(4) = 1` short-circuit FALSE. Pattern wildcards: `W(i) = 1` matches any code, `W(i) = 9999` matches the remainder. Full match sets `flag(4) = 1` and returns TRUE; partial match returns FALSE with no flag mutation.

## Informs

- New: [[interpreter/input-parsing]] — the input-preprocessing pipeline and `said` test semantics on a single subsystem page.
- Updated: [[interpreter/variables-and-flags]] — refined `var(9)` (1-indexed unparsed-word position; the 2-2 phrasing oddity is resolved by 2-6), `flag(2)` (explicitly set only after *successful* preprocessing, not on raw input-entered), `flag(4)` (at-most-once-per-cycle `said` semantics made explicit).
- Updated: [[concepts/agi-data-types]] — the Word-type "to be added when later chapters cover input handling" forward-ref replaced with a concrete cross-link to [[interpreter/input-parsing]], with `read` / `get_string` explicitly deferred to Group 3.
- Updated: [[interpreter/overview]] — new "Input parsing" section between "The event loop" and "Debug modes", matching the existing one-paragraph-per-subsystem pattern.

## Notes

- Provenance: the chapter header credits "AGDS docs" with a footnote naming Vassili Bykov as Russian→English translator, and an italic "Retrived from the Internet Archive" (sic) annotation. Last updated 31 August 1997 — identical date to 2-4, which was also retrieved from the Internet Archive. Plausibly both chapters were extracted in the same archive-spelunking session.
- Per-chapter authorship snapshot: 2-1 / 2-2 / 2-3 are Peter Kelly (assumed); 2-4 is Lance Ewing solo (IA); 2-5 is Lance Ewing primary + Peter Kelly + Anders M Olsson; 2-6 is AGDS manual translated by Vassili Bykov (IA). Check the HTML header per-chapter rather than assume.
- The chapter's footer note explicitly states the content is "taken from the description of the `said` command from section 4.3" with a link to `4-3-Logic.html`. Group 3 (Logic) ingest of 4-3 should cross-check whether 4-3 repeats this content verbatim, paraphrases it, or expands with opcode-level details (bytecode parameter encoding, version-specific argument-count changes). Either way, 4-3's `said` documentation should cross-link to [[interpreter/input-parsing]] and vice versa.
- **Vocabulary-lookup algorithm under-specified.** The spec says "the interpreter looks up the vocabulary, trying to find the longest character sequence matching the entered." That phrasing could describe full-word longest-match, prefix matching, substring matching, or another strategy. ScummVM's AGI implementation uses a trie-based vocabulary; the Python prototype has no word-lookup code. Tagged `(agidev, unverified)` on [[interpreter/input-parsing]].
- **Reconciliation of the 2-2 `var(9)` phrasing oddity.** 2-2 described `var(9)` with apparently-inverted logic ("if = 0, it is the number of the word ... that was not found") and was tagged `(agidev, unverified)` at the 2-2 ingest. 2-6 makes the semantics unambiguous: `var(9)` is populated only when vocabulary lookup fails, so the implicit reading of 2-2's phrasing is "if non-zero, gives the unparsed-word position; if zero, all words parsed". The `(agidev, unverified)` tag on `var(9)` is dropped in this ingest.
- No conflicts observed against existing wiki pages or `resource/` code.
