# SOUND

SOUND resources hold musical scores and sound effects for PC-speaker (mono) and PCjr (polyphonic four-channel) playback. Each SOUND is structured as an 8-byte header pointing to four independent voice data sections — three tone generators and one noise channel — each played back simultaneously with individual frequency, duration, and attenuation control. This design matches the TI SN76496A hardware voice architecture of the IBM PCjr [7-1-SOUND.html §History, §Sound and the IBM PCjr].

## Hardware context: TI SN76496A voice model

The PCjr's sound chip implements four independent voices [7-1-SOUND.html §Sound and the IBM PCjr]:

- **Voices 1, 2, 3** — tone generators, each with independently selectable frequency (10-bit divisor) and volume (4-bit attenuation).
- **Voice 4 (noise)** — noise source with 4-bit attenuation, mode selection (periodic or white noise), and three pre-selected frequencies or frequency borrow from voice 3.

On IBM PC compatibles without the PCjr sound hardware, only voice 1 (the melody) is rendered to the PC speaker; the other three voices are still present in the resource but are discarded at playback time [7-1-SOUND.html §Introduction, §Playing the Sounds on a Sound Card].

## AGI v2+ SOUND format

The SOUND resource consists of an 8-byte header followed by four voice data sections [7-1-SOUND.html §AGI SOUND FILES, §Appendix 1].

### Header (8 bytes)

| Offset | Field | Meaning |
|---|---|---|
| 0–1 | Voice 1 offset | Little-endian (low byte then high byte) offset into the SOUND payload; points to the start of voice-1 note data. |
| 2–3 | Voice 2 offset | Offset to voice-2 note data. |
| 4–5 | Voice 3 offset | Offset to voice-3 note data. |
| 6–7 | Noise offset | Offset to noise-channel note data. |

All offsets are relative to the start of the SOUND payload [7-1-SOUND.html §AGI SOUND FILES].

### Voice note data (5-byte notes)

Each voice's data section is a sequence of 5-byte note entries, terminated by two consecutive `0xFF` bytes [7-1-SOUND.html §Appendix 1]. Byte positions below are 1-indexed to match the spec ("FIRST BYTE" through "FIFTH BYTE").

| Byte | Field |
|---|---|
| 1–2 | Duration (low byte then high byte) — 16-bit little-endian. (agidev, unverified — time-unit scale not specified in the chapter.) |
| 3 | Tone: low 6 bits of 10-bit frequency divisor. Noise: `0x00`. |
| 4 | Tone: register address + high 4 bits of frequency divisor. Noise: register address + FB + NF0/NF1. |
| 5 | Attenuation (register address + 4 attenuation bits) — same layout for all four voices. |

#### Third byte — tone voice

```
bit:  7   6   5   4   3   2   1   0
      0   X   F0  F1  F2  F3  F4  F5
```
- Bit 7: Always 0 [7-1-SOUND.html §Appendix 1].
- Bit 6: Unused, ignored.
- Bits 5–0: F0–F5, lower 6 bits of the 10-bit frequency divisor.

#### Third byte — noise voice

The third byte is `0x00` for all noise notes [7-1-SOUND.html §Appendix 1, line 196].

#### Fourth byte — tone voice

```
bit:  7   6   5   4   3   2   1   0
      1   R0  R1  R2  F6  F7  F8  F9
```
- Bit 7: Always 1 [7-1-SOUND.html §Appendix 1].
- Bits 6–4: R0–R2, 3-bit register address identifying the voice:
  - `000` → Voice 1 frequency
  - `010` → Voice 2 frequency
  - `100` → Voice 3 frequency
- Bits 3–0: F6–F9, upper 4 bits of the 10-bit frequency divisor.

**Frequency calculation** [7-1-SOUND.html §Appendix 1]:

```
F = 111860 / (((Byte-3 AND 0x3F) * 16) + (Byte-4 MOD 16))
```

The constant 111,860 Hz is reported as 1/32 of the PCjr system clock (3.579 MHz) [7-1-SOUND.html §The Tone Generators]. (agidev, unverified — hardware clock rate not independently corroborated in this wiki.)

#### Fourth byte — noise voice

```
bit:  7   6   5   4   3   2   1   0
      1   1   1   0   X   FB  NF0 NF1
```
- Bit 7: Always 1 [7-1-SOUND.html §Appendix 1].
- Bits 6–4: `110` — register address 6, identifying the noise voice.
- Bit 3: Unused, ignored.
- Bit 2 (FB): Noise mode — `1` = white noise (hissing), `0` = periodic noise (steady) [7-1-SOUND.html §The Noise Generator].
- Bits 1–0 (NF0, NF1): Noise frequency selection [7-1-SOUND.html §The Noise Generator]:

| NF0 | NF1 | Frequency |
|---|---|---|
| 0 | 0 | 1,193,180 / 512 = 2330 Hz |
| 0 | 1 | 1,193,180 / 1024 = 1165 Hz |
| 1 | 0 | 1,193,180 / 2048 = 583 Hz |
| 1 | 1 | Borrow tone voice 3's frequency |

The `(1, 1)` row is documented in §The Noise Generator prose but is omitted from Appendix 1's table; the wiki includes it for completeness.

#### Fifth byte — attenuation (all voices)

```
bit:  7   6   5   4   3   2   1   0
      1   R0  R1  R2  A0  A1  A2  A3
```
- Bit 7: Always 1, command-byte marker [7-1-SOUND.html §Attenuation].
- Bits 6–4 (R0, R1, R2): 3-bit register address identifying the voice's attenuation slot [7-1-SOUND.html §Appendix 1]:
  - `001` → Voice 1 attenuation
  - `011` → Voice 2 attenuation
  - `101` → Voice 3 attenuation
  - `111` → Noise voice attenuation
- Bits 3–0 (A0, A1, A2, A3): 4 attenuation bits. **A0 is bit 3 (MSB of the low nibble); A3 is bit 0 (LSB).**

**Attenuation bit weights** [7-1-SOUND.html §Appendix 1, lines 234–240]:

| Bit name | Bit position | dB contribution |
|---|---|---|
| A0 | 3 (MSB of nibble) | 16 dB |
| A1 | 2 | 8 dB |
| A2 | 1 | 4 dB |
| A3 | 0 (LSB of nibble) | 2 dB |

When all four bits are set (`1111`), the voice is muted ("Volume off"). The spec lists only the single-bit-set rows and the all-set row; whether intermediate values combine additively (e.g., A1+A3 → 8+2 = 10 dB) is not stated. (agidev, unverified — additivity inferred from the structure of the table but not explicitly claimed.)

## Byte-order note

The note data is stored in little-endian byte order in the SOUND resource: the 16-bit duration field is low-byte-first, and bytes 3–4 carry the frequency divisor in low-bits-first order. The chapter notes this is **reversed** relative to the sequential order in which bytes would be sent to the T1 chip's register interface [7-1-SOUND.html §Appendix 1, §Playing the Sounds on a Sound Card]. Lance Ewing's prose around this point is imprecise ("the two bytes are around the other way", "opposite from the order that would be output to the T1 sound chip"); Appendix 1's bit tables are unambiguous and authoritative.

## AGI v1.12 SOUND format (legacy)

AGI v1.12 used a different SOUND encoding — no separate per-voice sections, no discrete duration field. All four voices' note data is interleaved, and the format uses a delta-style scheme where each 3-unit time step is marked and only voices that change their note value are recorded [7-1-SOUND.html §Appendix 2: AGI v1.12 Sound Format].

The exact voice-identification and byte-selection algorithm for v1.12 is not fully understood; the spec calls it "a mystery" and recommends treating Appendix 2 as a historical reference rather than a decoding specification. (agidev, unverified — v1.12 format is incomplete and not independently corroborated in this wiki.)

## Playback

A playback routine maintains four independent pointers, one per voice, tracking the current note in each section. All four voices are played simultaneously; notes in each voice finish at independent times and are succeeded by the next note in that voice's stream [7-1-SOUND.html §Playing the Sounds on a Sound Card]. When all voices have consumed their data (each reaching the dual-`0xFF` terminator), playback stops.

On PC-speaker hardware (most IBM PC compatibles), only voice 1 is rendered. PCjr and some compatibles with the TI chip can render all four [7-1-SOUND.html §Introduction, §Playing the Sounds on a Sound Card].

## Reference implementations

Two playback programs are vendored under `AGI_Specifications/Code/` and indexed by [7.2-SOUND.html]: `oldplay.c` (Lance Ewing) does direct Adlib/PC-speaker playback; `play.c` (Jens Christian Restemeier, Lance Ewing edits) transcodes to MIDI. See [[sources/7-2-sound]] for detailed citations. Two findings from those sources flow into this entity page:

- **Duration field — time-unit clue.** `play.c:107` multiplies the 16-bit duration field by 6 before emitting a MIDI delta. This is the only concrete code-level clue to the duration field's time unit; the spec does not state it. (agidev, unverified — `* 6` is undocumented in the source.)
- **Multi-voice / volume-control vintage caveat.** `play.c:9-10` notes the program "was written before we worked out the details on the fourth voice and the volume control." Earlier reference code may not fully reflect the v2+ four-voice and `var(23)` volume semantics.

SOUND remains the AGI resource type with the weakest code-validation coverage; andromeda has no SOUND decoder yet, and cross-check against ScummVM `engines/agi/sound_pcjr.cpp` is recommended before treating any byte-level claim on this page as production-ready.

## Related runtime state

The interpreter reserves the following [[interpreter/variables-and-flags]] entries for sound:

- `var(22)` — Sound generator type: `1` = PC speaker, `3` = Tandy.
- `var(23)` — Sound volume (Tandy only), range `0x0`–`0xF`.
- `flag(9)` — Sound on/off state.

Three LOGIC commands control playback (see [[interpreter/commands]]):

- `load.sound` (`$62`, 1 arg) — Load a SOUND resource by number into a playback buffer.
- `sound` (`$63`, 2 args: `num`, `flag`) — Initiate playback of the loaded sound and signal the named flag at completion.
- `stop.sound` (`$64`, 0 args) — Halt the current sound.

Exact semantics of the `sound` command's flag argument (set on completion vs. cleared on start, interaction with `stop.sound`) are not detailed in 7-1-SOUND; they may be elaborated in 7.2-SOUND or remain an open item.

## See also

- [[concepts/pcjr-sound-encoding]] — Shared encoding primitives (tone divisor, noise selector, attenuation).
- [[sources/7-1-sound]] — Chapter source notes.
