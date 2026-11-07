"""Boot the interpreter with optional LOGIC overrides: the entry point for scenarios and tests."""
import os
from pathlib import Path

from gamefs import load_dir, with_resources
from logic import payload
from machine import Machine

DEFAULT_GAME = Path(__file__).resolve().parents[2] / "test_games" / "sq1"
FIRST_RUN_FLAG = 250


def game_files(game_dir=None):
    return load_dir(game_dir or os.environ.get("AGI_GAME_DIR", DEFAULT_GAME))


def boot(logics=None, messages=None, pictures=None, views=None, sounds=None, switches="", game_dir=None,
         **fields):
    """A machine whose LOGIC n runs `logics[n]` bytecode, with `messages[n]` as its texts.

    `pictures`, `views` and `sounds` map resource numbers to raw payloads that replace the game's own.
    """
    messages = messages or {}
    files = game_files(game_dir)
    files = with_resources(files, "LOGDIR", {n: payload(code, messages.get(n, [])) for n, code in (logics or {}).items()})
    files = with_resources(files, "PICDIR", pictures or {})
    files = with_resources(files, "VIEWDIR", views or {})
    files = with_resources(files, "SNDDIR", sounds or {})
    return Machine(files, switches=switches, **fields)
