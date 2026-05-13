# PCjr TI SN76496A Sound Encoding

Shared encoding primitives for AGI SOUND resources, derived from the TI SN76496A hardware voice interface and replicated in the note data stored on disk. Used by every 5-byte note in [[entities/sound]]'s four voice sections.

## Tone frequency encoding (10-bit divisor)

A 10-bit divisor is split across two bytes within each tone-voice note. In storage order (little-endian; reversed relative to the T1 chip's register-write sequence):

**Third byte of note (low 6 bits of divisor):**

```
bit:  7   6   5   4   3   2   1   0
      0   X   F0  F1  F2  F3  F4  F5
```
- Bit 7: always 0.
- Bit 6: ignored.
- Bits 5–0: F0–F5 (lower 6 bits of divisor) [7-1-SOUND.html §Appendix 1].

**Fourth byte of note (high 4 bits of divisor + register):**

```
bit:  7   6   5   4   3   2   1   0
      1   R0  R1  R2  F6  F7  F8  F9
```
- Bit 7: always 1.
- Bits 6–4: register address (R0R1R2 = `000`/`010`/`100` for voices 1/2/3).
- Bits 3–0: F6–F9 (upper 4 bits of divisor) [7-1-SOUND.html §Appendix 1].

**Reconstructed divisor and frequency** [7-1-SOUND.html §Appendix 1]:

```
divisor   = ((Byte-3 AND 0x3F) * 16) + (Byte-4 AND 0x0F)
frequency = 111860 / divisor
```

The base frequency 111,860 Hz is reported as 1/32 of the PCjr system clock (3.579 MHz) [7-1-SOUND.html §The Tone Generators]. (agidev, unverified — clock rate not independently corroborated.)

**Code corroboration and outlier.** `play.c:116` (vendored at `AGI_Specifications/Code/play.c`) uses `111860.0 / freq`, matching the spec. `oldplay.c:91` (same chapter, [[sources/7-2-sound]]) uses `99320 / fileData` instead — a ~12% lower constant, unexplained in either source. Two reference implementations in the same sample-code chapter disagree; the spec value is corroborated by `play.c` and is the recommended constant.

## Noise frequency encoding (2-bit selector)

The noise voice has no continuous frequency divisor; instead, a 2-bit field (NF0, NF1) selects among three pre-defined frequencies plus a fourth "borrow" mode that couples the noise generator to tone voice 3 [7-1-SOUND.html §The Noise Generator]:

| NF0 | NF1 | Frequency |
|---|---|---|
| 0 | 0 | 1,193,180 / 512 = 2330 Hz |
| 0 | 1 | 1,193,180 / 1024 = 1165 Hz |
| 1 | 0 | 1,193,180 / 2048 = 583 Hz |
| 1 | 1 | Voice 3 tone frequency (dynamic coupling) |

A separate FB bit selects noise mode: `1` = white noise (hiss), `0` = periodic noise (steady tone).

## Attenuation / volume encoding (4-bit)

Every voice's fifth byte holds 4 attenuation bits in positions 3–0 of the byte. **A0 is the MSB of the nibble (bit 3); A3 is the LSB (bit 0).**

| Bit name | Bit position in byte | dB contribution |
|---|---|---|
| A0 | 3 | 16 dB |
| A1 | 2 | 8 dB |
| A2 | 1 | 4 dB |
| A3 | 0 | 2 dB |

When all four bits are set (`1111`), the voice is muted ("Volume off") [7-1-SOUND.html §Appendix 1, lines 234–240].

The spec's table only lists single-bit-set rows plus the all-set mute row. Whether intermediate values combine additively (e.g., A1+A3 = 10 dB) is not stated explicitly. (agidev, unverified — additivity inferred from the table's structure but not corroborated by independent sources or working AGI sound code in this wiki.)

## See also

- [[entities/sound]] — SOUND resource layout; this concept page factors out the per-note encoding tables.
- [[sources/7-1-sound]] — Source chapter (Lance Ewing, 18 August 1997).
