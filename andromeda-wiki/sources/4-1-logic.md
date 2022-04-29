# Source: 4-1-Logic.html

**Chapter:** 4.1 LOGIC Resource Format
**Path:** `AGI_Specifications/Specifications/4-1-Logic.html`
**Author:** Lance Ewing (`be@ihug.co.nz`)
**Last updated:** 20 August 1997
**Provenance:** "Retrived from the Internet Archive" (sic, in HTML)

## Scope

LOGIC resource on-disk format (AGI v2 only):

- Seven-byte header: 5-byte universal VOL resource header (see [[entities/vol-file]]) + 2-byte little-endian text offset.
- Bytecode section: AGI commands (`$00..$B5`, with `$00` doubling as `return`), test condition codes (`$00..$12`, valid only inside `if`), and four control-flow opcodes (`$FF` `if` open/close with bracket distance, `$FE` `else`/`goto` with signed offset, `$FD` `not`, `$FC` `or` bracket).
- Detailed `if/else/not/or` examples (KQ1 Room 2 walkthroughs) including the 3-byte bracket-distance inflation rule when `else` follows `if`.
- Inner-loop encoding via `$FE` with negative offset (SQ2 example).
- Argument dispatch: per-command argument-count and per-argument variable-vs-number type byte (bits 7..1), stored in AGIDATA.OVL inside the interpreter binary, not in LOGIC resources.
- Entry-point control: `set.scan.start` / `reset.scan.start`.
- Text section layout: count byte, end pointer, offset table, null-terminated message bodies XOR'd with the 11-byte key `"Avis Durgan"`.
- `said` test command's variable argument encoding: count byte + N × 2-byte little-endian vocabulary word codes.
- Annotated x86 ASM from Manhunter: San Francisco showing the original interpreter's decode state machine.

Brief overview of AGI command categories (VIEW, PICTURE, SOUND, animation, inventory operations) is included but individual opcode semantics are deferred to later Logic chapters.

## Informs

- [[entities/logic]] — LOGIC resource format: header, bytecode section, control-flow opcodes and bracket-distance rules, condition codes, argument-dispatch via AGIDATA.OVL, text section structure and Avis Durgan encryption, `said` encoding, entry-point control, ASM-level decode loop.

Light deltas:

- [[interpreter/overview]] — §"The LOGIC virtual machine" cross-link to [[entities/logic]] for the on-disk bytecode format; §"Resource types" LOGIC entry updated now that the page exists.

Deferred to later groups:

- Full opcode catalogue (command names, argument signatures, semantics) → later Logic chapters (4-2..4-6). 4-1 only enumerates ranges and category labels.
- `said` matching algorithm (wildcards, longest-match vs prefix-match semantics) → 4-3-Logic.html per the 2-6 forward-pointer.
- `set.game.id` and the four version-conditional argument-count mutations (`quit`, `print.at`, `print.at.v`, unknown #176) → later Logic chapters.
- v3 LOGIC header layout and the relationship between LOGIC encryption and v3 LZW compression → later Logic chapters.
- PICTURE bytecode opcodes (`0xF0`, `0xF2`) for 4-bit vs 8-bit color encoding → [[entities/picture]] (Group 4); flagged in [[sources/2-8-interpreter]].

## Notes

**Direct v2 LOGIC encryption claim.** 4-1 states the text-section encryption directly (§THE TEXT SECTION line 302 of the HTML), with worked examples. This *confirms* the inference that was already preserved in [[sources/2-8-interpreter]] (derived contrapositively from 2-8's v3 "no need to encrypt because compressed" statement). Both sources now corroborate. The `(agidev, unverified)` tag remains on the page because the Python prototype has no LOGIC decoder to validate the byte-level XOR claim against working code, not because the source is unreliable. The same XOR key + primitive is already verified for OBJECT files in `resource/objects.py`.

**Decoder gap (overall).** Every bytecode-level claim on [[entities/logic]] is unverifiable against working code — `resource/` has no LOGIC parser. The first concrete decoder work in the future Rust rewrite will validate (or contradict) these claims. Implementation will need: 7-byte header parser, control-flow walker honoring `$FF/$FE/$FD/$FC`, argument-dispatch table equivalent to AGIDATA.OVL, and the text-section XOR loop.

**Cross-key clarification.** "Avis Durgan" is the 11-byte XOR key for both v2 LOGIC text sections and the OBJECT file. This is distinct from the 128-byte rolling-XOR-with-carry-feedback loader key documented in [[sources/2-5-interpreter]], which decrypts the interpreter binary itself. Two different keys, two different lifecycles, both surface under "AGI encryption".

**Authorship.** Lance Ewing is the primary author of 2-4, 2-5, 2-8, and 4-1. All four are Internet-Archive-provenance and date to 1997–1998. The 4-1 ingest is the fourth Lance-Ewing-primary chapter in the corpus.

**Section citations.** 4-1's `<h3><i>UPPERCASE</i></h3>` section headers are real HTML tags (verified). Citations like `[4-1-Logic.html §THE HEADER]` reference actual structure, unlike the 2-6 ingest where pseudo-section citations had to be stripped because the chapter had no real headers.
