"""The real routine against the models. Skipped without local game data; none is stored here."""
import pytest

import checks
from emulator import OVERLAY, PictureEmu, load_pens


@pytest.fixture(scope="module")
def emu(game_dir):
    return PictureEmu(game_dir)


@pytest.fixture(scope="module")
def pens(game_dir):
    return load_pens(game_dir)


@pytest.fixture(scope="module")
def corpus(emu, pens, game_dir):
    return checks.game_corpus(emu, pens, game_dir)


def test_all_game_pictures_match_the_rules(corpus):
    result = corpus["rules"]
    assert result.pictures == 73
    assert (result.visual_pixels, result.priority_pixels) == (0, 0)


def test_showpic_as_shipped_differs_only_in_priority(corpus):
    result = corpus["showpic as shipped"]
    assert (result.differing_pictures, result.visual_pixels, result.priority_pixels) == (8, 0, 7592)


def test_correcting_the_stale_check_alone_removes_every_difference(corpus):
    assert corpus["showpic, stale check fixed"].differing_pictures == 0


def test_literal_5_1_fill_differs_in_two_pictures(corpus):
    result = corpus["showpic fixed, priority only over 4"]
    assert (result.differing_pictures, result.priority_pixels) == (2, 194)


def test_a_sample_of_each_synthetic_family_matches(emu, pens):
    for name, pictures in checks.synthetic_families(seed=1, scale=0.02):
        assert checks.count_mismatches(emu, pens, pictures) == 0, name


def test_overlay_keeps_the_buffer(emu):
    emu.run([0xF0, 0, 0xF2, 1, 0xF6, 0, 0, 10, 0, 0xFF])
    assert emu.run([0xFF], entry=OVERLAY)[3] == 0x10
