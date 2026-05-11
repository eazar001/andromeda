# 7-1-SOUND.html

**Chapter:** 7.1 SOUND Resource Format
**Author:** Lance Ewing
**Last updated:** 18 August 1997
**Provenance:** Vendored at `AGI_Specifications/Specifications/7-1-SOUND.html`.

## Summary

Specifies the AGI v2+ SOUND resource format as a four-voice container designed to feed the IBM PCjr's TI SN76496A sound generator. Covers the PCjr hardware context (three tone voices + one noise voice with independent frequency, duration, and attenuation), the 8-byte header of voice offsets, the 5-byte note encoding (duration, tone divisor or noise selector, attenuation), the dual-`0xFF` terminator, and a partial sketch of the older v1.12 delta-style format (which the chapter itself describes as not fully understood). Appendix 1 holds the authoritative bit-level layout; the main prose is imprecise around byte-order language.

## Pages informed

- [[entities/sound]] — created. v2+ format, 5-byte note layout (tone and noise variants), v1.12 sketch.
- [[concepts/pcjr-sound-encoding]] — created. Shared encoding primitives: 10-bit tone divisor, 2-bit noise selector, 4-bit attenuation.
- [[interpreter/variables-and-flags]] — extended `var(23)` entry with sound-volume context.
- [[interpreter/commands]] — extended `$62..$64` Sound subsection with cross-refs to the new entity.
- [[interpreter/overview]] — promoted the SOUND stub paragraph to a real description with links.
- [[index]] — added entries for the new entity and concept.

## Notable findings

- **Format mirrors the T1 chip's register interface.** Tone-voice byte 4 directly encodes a T1 register address (R0R1R2) plus 4 bits of the frequency divisor, in the same bit positions the chip expects, except that the on-disk byte order is reversed relative to the T1 wire order. This explains why the spec keeps using the word "reversed" around byte 3 / byte 4.
- **Attenuation is bit-position-weighted, not bit-count-weighted.** A0 (bit 3 of the nibble) contributes 16 dB; A3 (bit 0) contributes 2 dB. Initial subagent draft had this reversed — caught and corrected during review.
- **Attenuation additivity is not stated by the spec.** The table only shows single-bit-set rows and a mute row. Wiki claims additive combination but flags it `(agidev, unverified)`.
- **AGI v1.12 format is underdocumented.** The chapter calls it "a mystery" and gives only a partial example; treated as historical reference, not a decode specification.
- **Hardware clock rate (3.579 MHz) and derived 111,860 Hz base are not independently corroborated** in this wiki; flagged for cross-check against ScummVM's `engines/agi/sound_pcjr.cpp` or AGI Studio source if a SOUND decoder is implemented.

## Open items

- Time-unit scale of the 16-bit duration field (per-frame? milliseconds? interpreter ticks?).
- AGI v1.12 voice-identification and selective-byte-recording algorithm.
- Mapping between `var(23)` (sound volume, 0x0–0xF) and the per-note attenuation byte sent to the T1 chip — are they multiplied, OR'd, or independent layers?
- Exact semantics of the `sound` command's flag argument (set-on-completion vs. clear-on-start; interaction with `stop.sound`). May be addressed in 7.2-SOUND.

## Related sources

- [[sources/2-2-interpreter]] — first defined `var(22)`, `var(23)`, `flag(9)` (sound runtime state).
- [[sources/4-3-logic]] — opcode catalogue including `load.sound` (`$62`), `sound` (`$63`), `stop.sound` (`$64`).
