# 8-2-WORDS_TOK: Vocabulary File Format

**Chapter:** §8.2 WORDS.TOK Format
**Source:** `AGI_Specifications/Specifications/8-2-WORDS_TOK.html`
**Author:** Lance Ewing
**Date:** 31 August 1997 (retrieved from Internet Archive)

## Scope

Complete specification of the WORDS.TOK vocabulary file: 26-entry alphabet index (Hi-Lo byte order — a deliberate departure from the system-wide Lo-Hi convention), variable-length word entries (prefix-share + `0x7F`-XOR character encoding + high-bit end-of-word marker), big-endian word numbers, and special codes `0` / `1` / `9999`.

## Pages informed

- [[entities/words-tok]] — created. Format, byte-order convention, decoding pseudocode, special word numbers.
- [[interpreter/input-parsing]] — added forward-reference to the vocabulary store (filling the existing "look up the vocabulary" gap).
- [[concepts/agi-data-types]] §Word — extended with a citation to the new entity page.
- [[entities/dir-file]], [[entities/vol-file]] — added a one-line note that WORDS.TOK is a standalone file, not indexed/contained by either.

## Notable findings

- **Non-standard byte order.** WORDS.TOK is the *only* AGI file documented in this corpus that uses Hi-Lo (big-endian) byte order. Spec line 50-51 calls it out explicitly: *"the normal Lo-Hi byte order convention used everywhere else in the AGI system is not used here ... This method is used later on for word numbers as well."*
- **Subagent draft had word numbers reversed.** Initial proposal pseudocode read `lo` first then `hi` and combined little-endian — opposite of what the spec states (Hi byte first, Lo byte second) and contradicted by the reference decoder `words.pas:104-106` (`msbyte*256 + lsbyte`). Corrected before apply.
- **Character encoding is `c XOR 0x7F`, end-marker is high-bit set.** Each suffix byte `b` decodes to `chr((b AND 0x7F) XOR 0x7F)`. The final suffix byte additionally has bit 7 set to mark end-of-word.
- **Special codes are parser-level, not storage-level.** Word codes `0`, `1`, and `9999` are stored exactly like normal entries in WORDS.TOK; their special meaning emerges only when the parser/`said`-test sees those values. See [[interpreter/input-parsing]].

## Validation

`AGI_Specifications/Code/words.pas` (Peter Kelly, indexed by [[sources/8-3-samplecode]]) is a working reference decoder that validates the byte-level layout. No andromeda decoder yet.

## See also

- [[entities/words-tok]] — on-disk format.
- [[interpreter/input-parsing]] — consumer side; how the parser uses the vocabulary.
- [[sources/2-6-interpreter]] — `said` semantics and the input pipeline.
- [[sources/8-3-samplecode]] — `words.pas` reference decoder.
