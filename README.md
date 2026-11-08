# Andromeda

A re-implementation of Sierra On-Line's AGI (Adventure Game Interpreter) v2, the engine behind *Space Quest 1*, *King's Quest 1/2*, *Leisure Suit Larry 1*, and other early Sierra adventure games. This Python codebase is the prototype, rendering through PySDL2; a Rust rewrite is planned. The first playable milestone targets Space Quest 1, room 1.

## Status

Pre-alpha. `VIEW` decoding, cel compositing, `OBJECT` parsing, and the `*DIR` index files work on all of Space Quest 1. `LOGDIR`, `PICDIR`, and `SNDDIR` are only read as indexes: the LOGIC, PICTURE, and SOUND resources themselves are not decoded, and nothing runs game logic yet. See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for the detailed roadmap and design notes.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
uv sync
```

Place an AGI v2 game's data files under `test_games/<game>/` — for example `test_games/sq1/` containing `VIEWDIR`, `LOGDIR`, `PICDIR`, `SNDDIR`, `OBJECT`, and `VOL.0` (plus any higher-numbered `VOL.*` files). Then run:

```bash
uv run python -m main
```

This opens a window that plays through every VIEW cel, then prints the directory listings. It does not play the game.

To run the unit tests:

```bash
uv run pytest
```

They check OBJECT and DIR decoding against expected values for each game in `tests/games/<game>.toml`, and skip any game whose data isn't in `test_games/<game>/`. Only Space Quest 1 is covered so far. To add a game, run `uv run python tests/make_golden.py test_games/<game> > tests/games/<game>.toml`.

## Project layout

```
main.py               # Entry point
resource/             # AGI resource decoders (DIR, VOL, VIEW, OBJECT, ...)
gfx/                  # SDL2-backed rendering
util/                 # Byte/crypto helpers
AGI_Specifications/   # Vendored copy of Peter Kelly's AGI spec (reference)
andromeda-wiki/       # Distilled, cited AGI format notes; start at index.md
```

## References

Andromeda is built from public specifications, checked against analysis of Sierra's AGI 2.917 interpreter.

- Peter Kelly, *AGI Specifications* — primary format reference (vendored in `AGI_Specifications/`)
- [Wiki audit plan](WIKI_AUDIT_PLAN.md) — how wiki claims are being checked against the interpreter
- [ScummVM AGI engine](https://github.com/scummvm/scummvm/tree/master/engines/agi) — secondary behavioral cross-check
- [NAGI](https://github.com/sonneveld/nagi) — Nick Sonneveld's cleanroom AGI reimplementation
- [AGI Wiki](http://agiwiki.sierrahelp.com/)

## License

MIT — see [LICENSE](LICENSE).
