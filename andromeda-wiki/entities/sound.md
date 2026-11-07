# SOUND

SOUND resources hold musical scores and sound effects for PC-speaker (mono) and PCjr (polyphonic four-channel) playback. Each SOUND is structured as an 8-byte header pointing to four independent voice data sections — three tone generators and one noise channel — each played back simultaneously with individual frequency, duration, and attenuation control. This design matches the TI SN76496A hardware voice architecture of the IBM PCjr [7-1-SOUND.html §History, §Sound and the IBM PCjr].

## Hardware context: TI SN76496A voice model

The PCjr's sound chip implements four independent voices [7-1-SOUND.html §Sound and the IBM PCjr]:

- **Voices 1, 2, 3** — tone generators, each with independently selectable frequency (10-bit divisor) and volume (4-bit attenuation).
- **Voice 4 (noise)** — noise source with 4-bit attenuation, mode selection (periodic or white noise), and three pre-selected frequencies or frequency borrow from voice 3.

On a machine without the sound chip, only voice 1 (the melody) is played on the PC speaker, and the other three voices are never read [7-1-SOUND.html §Introduction, §Playing the Sounds on a Sound Card; AGI 2.917 1000:7F0E].

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
| 1–2 | Duration (low byte then high byte) — 16-bit little-endian, in ticks of the 60 Hz timer, so 1/60 second each [AGI 2.917 1000:7F77, 1000:8469]. `FF FF` here ends the voice. A duration of 0 wraps to 65,535 ticks; SQ1 has none. |
| 3 | Tone: high 6 bits of 10-bit frequency divisor. Noise: `0x00`. |
| 4 | Tone: register address + low 4 bits of frequency divisor. Noise: register address + FB + NF0/NF1. |
| 5 | Attenuation (register address + 4 attenuation bits) — same layout for all four voices. |

#### Third byte — tone voice

```
bit:  7   6   5   4   3   2   1   0
      0   X   F0  F1  F2  F3  F4  F5
```
- Bit 7: Always 0 [7-1-SOUND.html §Appendix 1]. Holds on all 3,534 SQ1 tone notes [SQ1 data check, log 2026-11-01].
- Bit 6: Unused, ignored. It is set on 1,449 SQ1 tone notes, so a decoder must mask it [SQ1 data check, log 2026-11-01; AGI 2.917 1000:811C].
- Bits 5–0: F0–F5, upper 6 bits of the 10-bit frequency divisor.

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
- Bits 3–0: F6–F9, lower 4 bits of the 10-bit frequency divisor.

**Frequency calculation** [7-1-SOUND.html §Appendix 1]:

```
F = 111860 / (((Byte-3 AND 0x3F) * 16) + (Byte-4 MOD 16))
```

The formula makes byte 3 the high-order part, and [play.c:108] agrees, as does 2.917's speaker path [AGI 2.917 1000:8115]. On SQ1 tone voices it gives a median of 254 Hz; the reverse reading gives 1,776 Hz with 16% of notes above 5 kHz [SQ1 data check, log 2026-11-01]. No audio has been produced yet. The speaker plays lower, by the different constant in [[concepts/pcjr-sound-encoding]].

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

The note data is stored in little-endian byte order in the SOUND resource: the 16-bit duration field is low-byte-first, and bytes 3–4 carry the frequency divisor as its high 6 bits, then its low 4 bits. On the sound chip, 2.917 writes byte 4 first and then byte 3, and writes only byte 4 for noise notes [AGI 2.917 1000:8044]. That is the reversal the chapter describes [7-1-SOUND.html §Appendix 1, §Playing the Sounds on a Sound Card].

## AGI v1.12 SOUND format (legacy)

AGI v1.12 used a different SOUND encoding — no separate per-voice sections, no discrete duration field. All four voices' note data is interleaved, and the format uses a delta-style scheme where each 3-unit time step is marked and only voices that change their note value are recorded [7-1-SOUND.html §Appendix 2: AGI v1.12 Sound Format].

The exact voice-identification and byte-selection algorithm for v1.12 is not fully understood; the spec calls it "a mystery" and recommends treating Appendix 2 as a historical reference rather than a decoding specification. (agidev, unverified — v1.12 format is incomplete and not independently corroborated in this wiki.)

## Playback

### Starting and stopping

- **`load.sound(n)`:** does nothing if the sound is loaded. Otherwise it reads the resource and records pointers to its voices; notes are not converted [AGI 2.917 1000:505E]. A missing directory entry is fatal.
- **`sound(n, f)`:** stops any sound already playing, which sets that sound's flag. It then clears `flag(f)`, and raises error 9 with `n` in `var(18)` if the sound isn't loaded [AGI 2.917 1000:510B]. This settles the earlier question: the flag is cleared at the start.
- **`stop.sound`:** if a sound is playing, sets its flag and silences the output. If none is playing, it changes nothing [AGI 2.917 1000:516C].
- **Finishing:** sets the flag from the timer interrupt, so a script sees it change between any two commands [AGI 2.917 1000:7FFA]. To silence output, the sound chip gets maximum attenuation on all four voices, and the speaker is turned off.

### The 60 Hz step

The timer interrupt steps a playing sound on every tick [AGI 2.917 1000:8462]. The step does the following [AGI 2.917 1000:7F55]:

1. **Check `flag(9)`.** If it's clear, the sound ends now, with its flag set. So with sound turned off, `sound` still completes, within one tick.
2. **Step each active voice.** Decrement its duration. Each duration starts at 1, so the first note loads on the first tick.
    - **Still counting:** update attenuation only.
    - **Reached 0:** read the next note. `FF FF` marks the voice finished, and it's muted. Otherwise write the new tone, then the attenuation.
3. **End the sound** when no active voices remain. That means all four on the sound chip, or just voice 1 on the speaker.

SQ1's sound 41 has no voice 1 notes, so on the speaker it ends at once [SQ1 data check, log 2026-11-01].

### Attenuation envelope

The spec doesn't mention this. On voices 1–3, a note's attenuation changes with time. Each new note restarts a 67-step table in `DS:17AE`, advanced once per tick, about 1.1 seconds in all [AGI 2.917 1000:80B7, 1000:7F82]:

`-2 -3 -2 -1 0 0 1 1 1 1`, then 2 ×8, 3 ×7, 4 ×4, 5 ×4, 6 ×5, 7 ×4, 8 ×4, 9 ×4, 10 ×4, 11 ×6, 12 ×6, 13 ×1.

While the table runs, the value sent to the chip is built as follows:

1. Add the table entry to the note's attenuation, and clamp to 0–15.
2. Add `var(23)`, and cap at 15.
3. On a Tandy only, add 2 if the result is below 8.

When the table ends, the last value from step 1 replaces the note's attenuation until the next note, and `var(23)` no longer applies. The Tandy step still applies. A note with attenuation 15 skips the table. The noise voice never uses the table, so it stays at its stored attenuation.

The high nibble of a note's fifth byte is not sent. The interpreter uses its own register values for each voice, so a stored voice number can't redirect the write [AGI 2.917 1000:810A, DS:17F2]. The tone byte is sent as stored, though. In SQ1 both match the voice on all 3,687 notes [SQ1 data check, log 2026-11-01].

### Machine types

Startup sets a machine type, from a command-line switch or by detecting the hardware [AGI 2.917 1000:00C4, 1000:40E5, 1000:4125]:

| Type | Machine | Switch | Detected by | Output |
|---|---|---|---|---|
| 0 | IBM PC and compatibles | `-p` | Default | Speaker, voice 1 |
| 1 | PCjr | | BIOS model byte `FD` | Sound chip, 4 voices |
| 2 | Tandy | `-t` | "Tandy" in the ROM at `C000:0000`–`C000:03FF` | Sound chip, 4 voices |
| 8 | Model byte `FA`, which is taken as a VGA machine | `-s` | BIOS system configuration call | Speaker, voice 1 |

### PC speaker

The speaker has one voice and no volume. A note's attenuation matters only at 15, which silences it [AGI 2.917 1000:8054, 1000:809B]. The speaker's frequency comes from the same tone bytes with a different constant; see [[concepts/pcjr-sound-encoding]].

One edge case on type 0: when the envelope table ends, the note's attenuation is replaced even though the speaker has no volume. A base of 2 or more becomes 15, which turns the speaker off for the rest of the note. That needs a note longer than 67 ticks, and SQ1 has none among its 1,068 audible voice 1 notes [SQ1 data check, log 2026-11-01]. **Confirmed at runtime:** a single 150-tick note at attenuation 4 turned the speaker gate on, and off again 68 ticks later [2.917 runtime: speaker_long_note_cutoff].


## Reference implementations

Two playback programs are vendored under `AGI_Specifications/Code/` and indexed by [7.2-SOUND.html]: `oldplay.c` (Lance Ewing) does direct Adlib/PC-speaker playback; `play.c` (Jens Christian Restemeier, Lance Ewing edits) transcodes to MIDI. See [[sources/7-2-sound]] for detailed citations. Two findings from those sources flow into this entity page:

- **Duration field.** `play.c:107` multiplies the 16-bit duration by 6 before emitting a MIDI delta, which is undocumented in the source. The binary gives the unit directly: 1/60 second.
- **Multi-voice / volume-control vintage caveat.** `play.c:9-10` notes the program "was written before we worked out the details on the fourth voice and the volume control." Earlier reference code may not fully reflect the v2+ four-voice and `var(23)` volume semantics.

All 50 SQ1 SOUNDs have voices whose 5-byte notes reach an `FF FF` terminator, with 3,687 notes in all. Voice 1 runs from 0 to 48 seconds at 60 Hz, with a median of about 1 second [SQ1 data check, log 2026-11-01]. Andromeda has no SOUND decoder yet. The timing is confirmed at runtime: on a Tandy, SOUND 1's voice 1 tone writes came every 3 ticks at 60 Hz, matching its 3-tick notes, with every divisor as stored, and its completion flag was set at the end [2.917 runtime: sound_chip_timing_on_tandy]. How it sounds is beyond the harness.

## Related runtime state

The interpreter reserves the following [[interpreter/variables-and-flags]] entries for sound:

- `var(22)` — Set to 1 on machine type 0, otherwise 3, at startup and after a restore. No read found in the interpreter, and SQ1 never tests it [AGI 2.917 1000:10AD; SQ1 data check, log 2026-11-01]. Type 8 gets 3 even though it uses the speaker.
- `var(23)` — Added to attenuation during the envelope, so higher is quieter. No effect on the speaker, and no range check beyond the cap at 15 [AGI 2.917 1000:80F3].
- `flag(9)` — Sound on. Set at startup, and restart keeps it [AGI 2.917 1000:0F97, 1000:24AB]. Clearing it ends a playing sound on the next tick.

Three LOGIC commands control playback (see [[interpreter/commands]]):

- `load.sound` (`$62`, 1 arg) — See "Starting and stopping".
- `sound` (`$63`, 2 args: `num`, `flag`) — See "Starting and stopping".
- `stop.sound` (`$64`, 0 args) — See "Starting and stopping".


## See also

- [[concepts/pcjr-sound-encoding]] — Shared encoding primitives (tone divisor, noise selector, attenuation).
- [[sources/7-1-sound]] — Chapter source notes.
