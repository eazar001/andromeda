# Andromeda

A cleanroom Python re-implementation of Sierra On-Line's AGI (Adventure Game Interpreter) v2, the engine behind *Space Quest 1*, *King's Quest 1/2*, *Leisure Suit Larry 1*, and other early Sierra adventure games. Rendering is prototyped against PySDL2. The first playable milestone targets Space Quest 1, room 1.

## Status

Pre-alpha. Resource decoders for `OBJECT`, `VIEWDIR`/`VIEW`, `LOGDIR`, `PICDIR`, and `SNDDIR` are working; the LOG bytecode interpreter, PIC renderer, and sound engine are not yet implemented. See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for the detailed roadmap and design notes.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
uv sync
```

Place an AGI v2 game's data files under `test_games/<game>/` — for example `test_games/sq1/` containing `VIEWDIR`, `LOGDIR`, `PICDIR`, `SNDDIR`, `OBJECT`, and `VOL.0` (plus any higher-numbered `VOL.*` files). Then run:

```bash
uv run python -m main
```

## Project layout

```
main.py               # Entry point
resource/             # AGI resource decoders (DIR, VOL, VIEW, OBJECT, ...)
gfx/                  # SDL2-backed rendering
util/                 # Byte/crypto helpers
AGI_Specifications/   # Vendored copy of Peter Kelly's AGI spec (reference)
```

## References

Andromeda is a cleanroom implementation built from public specifications, not from disassembly of Sierra's interpreters.

- Peter Kelly, *AGI Specifications* — primary format reference (vendored in `AGI_Specifications/`)
- [ScummVM AGI engine](https://github.com/scummvm/scummvm/tree/master/engines/agi) — secondary behavioral cross-check
- [NAGI](https://github.com/sonneveld/nagi) — Nick Sonneveld's cleanroom AGI reimplementation
- [AGI Wiki](http://agiwiki.sierrahelp.com/)

## License

MIT — see [LICENSE](LICENSE).
