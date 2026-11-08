"""Parameterizes tests over every game with golden values in tests/games/*.toml.

A game runs only when its data is in <GAME_ROOT>/<name>/ (default: test_games/),
which is gitignored; otherwise its tests skip.
"""
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).parent / "games"
GAME_ROOT = Path(os.environ.get("GAME_ROOT", Path(__file__).parents[1] / "test_games"))


@dataclass(frozen=True)
class Game:
    name: str
    path: Path
    objects: dict
    dirs: dict


def load_game(golden_file: Path) -> Game:
    with golden_file.open("rb") as f:
        data = tomllib.load(f)
    name = golden_file.stem
    return Game(name, GAME_ROOT / name, data["objects"], data["dirs"])


GAMES = [load_game(p) for p in sorted(GOLDEN_DIR.glob("*.toml"))]


@pytest.fixture(params=GAMES, ids=lambda g: g.name)
def game(request) -> Game:
    g = request.param
    if not g.path.is_dir():
        pytest.skip(f"no game data in {g.path}")
    return g
