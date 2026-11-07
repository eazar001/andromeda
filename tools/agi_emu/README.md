# Whole-interpreter harness

Runs the whole AGI 2.917 interpreter from SQ1 under Unicorn, with DOS and the BIOS emulated in Python. It's the runtime evidence for `andromeda-wiki/`: each scenario boots the real interpreter, often with a LOGIC 0 written for the test, and reports what the interpreter did. `tools/picture_emu/` runs the PICTURE routine alone; this runs everything.

No game data is stored here. Point `--game` or `AGI_GAME_DIR` at a directory holding the decoded interpreter and the game files, which defaults to `test_games/sq1`. Never commit its output.

## Spec

| Module | Input | Output |
|---|---|---|
| `image.py` | `AGI.decoded` bytes, a load segment | The relocated program image, entry `CS:IP` and `SS:SP` |
| `logic.py` | Bytecode and messages | A LOGIC payload in the 2.917 layout, messages encrypted |
| `gamefs.py` | A game directory, resource overrides | A file map, with overridden resources appended to `VOL.0` and their DIR entries repointed |
| `bios.py` | Interrupt number and registers | Register results for `10h`, `11h`, `12h`, `15h`, `16h`, `1Ah`; port reads |
| `dos.py` | `21h` and registers, the file map | File, memory, vector, drive and exit services. Writes go to an in-memory overlay |
| `machine.py` | Image, file map, switches, key script | A running machine: timer interrupts every fixed instruction count, port I/O log, address probes, memory reads |
| `opcodes.py` | Generated | Opcode and argument count per command, from `interpreter/commands`, checked against `AGIDATA.OVL` |
| `resources.py` | Opcode tuples, cel rows | PICTURE and VIEW payloads for test resources |
| `video.py` | Port writes, video memory | An EGA register and plane model; decoders for CGA, VGA, Hercules and PCjr memory |
| `session.py` | Overrides | `boot()`: a machine on the game's files with LOGIC, PICTURE, VIEW and SOUND overrides |
| `scenarios.py` | Nothing | One function per runtime item in `WIKI_AUDIT_PLAN.md`, each returning a dict of observations |

Rules:

- The machine is deterministic. The timer fires every `TICK_INSNS` instructions, not on wall time, and the BIOS clock is derived from the tick count.
- Hardware isn't emulated beyond what the interpreter reads back. Port writes are logged; port reads return fixed values, with no joystick and with retrace bits that toggle on every read.
- EGA is modelled at the register level, enough for write modes 0 and 2 with latches. Other adapters' memory is plain RAM.
- DOS places each memory block one paragraph after its MCB, as real DOS does, because the heap's base and its 16-bit wrap depend on it.
- Keys reach the interpreter two ways: BIOS key words through `int 16h`, and scan codes through `int 9` and port `60h`.
- A scenario states what it sets up, what it reads, and which claim it settles. Its result goes in the wiki, never this directory.

## What it can't show

- Analog output: composite CGA artifact colors, and how a monitor shows any palette. Scenarios report the registers and memory a driver wrote.
- Real timing of retrace waits, so durations that depend on vertical retrace are meaningless here.
- DOS's own behavior where the interpreter leaves it in charge: the divide-error handler, and a read whose buffer crosses a 64K offset boundary, which this DOS writes linearly.

## Running

From the repo root:

    uv run --with unicorn --with pytest python -m pytest tools/agi_emu -p no:faulthandler
    uv run --with unicorn python tools/agi_emu/scenarios.py [name ...]
