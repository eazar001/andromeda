# Source: AGI 2.917 at runtime

The whole SQ1 interpreter, run unmodified under an x86 emulator with DOS and the BIOS emulated in Python, by the harness in `tools/agi_emu/`. It settles the claims that [[sources/agi-2917-binary]] could only read, and it outranks static reading where they disagree, for 2.917 only [WIKI.md §Source-reliability rules].

Citations look like `[2.917 runtime: scenario]`, where `scenario` is a function in `tools/agi_emu/scenarios.py`. Running it reproduces the result.

## How a scenario works

Most scenarios replace LOGIC 0 with bytecode written for the test, and some replace a PICTURE, VIEW or SOUND too. The overrides are appended to `VOL.0` with their directory entries repointed, so the interpreter loads them the normal way. Every other file is the game's own. A test LOGIC 0 enters room 0 on its first cycle, as games do, because `new.room` is what gives objects their timings. Results are read from interpreter memory, from video memory and from port writes. Some scenarios drive the real SQ1 instead, by typing keys.

## What it models, and what it doesn't

- The timer interrupt fires every 20,000 instructions, so runs are deterministic. Ticks are counted at the interpreter's own 60 Hz.
- DOS file, memory and vector services, with memory blocks placed after an MCB paragraph as real DOS places them. The heap's base depends on that.
- BIOS video, keyboard, clock and equipment calls, and the PCjr page-register call.
- Keys as BIOS words through `int 16h`, and as scan codes through `int 9` and port `60h`.
- EGA at the register level: map mask, graphics controller, latches, write modes 0 and 2. CGA, VGA, Hercules and PCjr memory are decoded from RAM.
- Not modelled: analog display output, including composite CGA color; real retrace timing; DOS's own divide-error handler; and how DOS handles a read whose buffer crosses a 64K offset boundary.

## Informs

[[interpreter/view-objects]], [[interpreter/command-semantics]], [[interpreter/control-lines]], [[interpreter/priority-bands]], [[interpreter/variables-and-flags]], [[interpreter/memory-layout]], [[interpreter/save-restore]], [[interpreter/debug-modes]], [[entities/logic]], [[entities/sound]], [[concepts/pcjr-sound-encoding]], [[concepts/picture-rendering]], [[concepts/ega-palette]], [[concepts/screen-layers]].
