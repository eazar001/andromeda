"""Puts these flat modules on the path, and finds game data, which isn't in the repo."""
import os
from pathlib import Path

import pytest

DEFAULT_GAME = Path(__file__).resolve().parents[2] / "test_games" / "sq1"


@pytest.fixture(scope="session")
def game_dir():
    path = Path(os.environ.get("AGI_GAME_DIR", DEFAULT_GAME))
    if not (path / "AGI.decoded").exists():
        pytest.skip(f"no decoded interpreter in {path}")
    return path
