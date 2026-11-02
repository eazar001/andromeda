# PICTURE emulation harness

Runs the AGI 2.917 interpreter's own PICTURE routine under an x86 emulator and compares its output with two Python renderers. It's the evidence behind the PICTURE claims in `andromeda-wiki/`, and it covers the PICTURE routine alone, on machine 0 and monitor 3, never a display driver.

| Module | Role |
|---|---|
| `emulator.py` | Loads `AGI.decoded` and `AGIDATA.OVL`, and runs the real routine |
| `rules_model.py` | The rules as the wiki states them. This should match the real routine |
| `showpic_model.py` | A port of `AGI_Specifications/Code/showpic.c`, with switches, and its splatter tables |
| `checks.py` | Picture generators and comparisons |
| `audit.py` | Runs everything and exits non-zero if the rules model differs |

No game data is stored here. Point `--game` or `AGI_GAME_DIR` at a directory holding the decoded interpreter, which defaults to `test_games/sq1`. Never commit its output pictures.

## Running

From the repo root:

    uv run --with unicorn --with pytest python -m pytest tools/picture_emu
    uv run --with unicorn python tools/picture_emu/audit.py

Tests that need the interpreter skip when it's absent. On Windows, pytest's `faulthandler` prints an access violation from inside Unicorn's memory setup, which the library handles; add `-p no:faulthandler` to silence it. The full audit takes about a minute; `--line-step 8` shortens its last check.

The last full run found no rules-model difference on all 73 SQ1 pictures, 2,000 random lines, 279 overflow-capable lines, 1,920 solid and 1,920 splatter plots, 1,500 random pictures and 600 noisy fills. `showpic` as shipped differs in 8 pictures (7,592 priority pixels), and the literal 5-1 fill reading in 2 (194). Generated samples depend on `--seed`, so the count of overflow-capable lines varies.

The rules model's flood fill is a plain 4-connected search, not the interpreter's span fill. Their equivalence is empirical, from these comparisons.
