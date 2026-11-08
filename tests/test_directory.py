import pytest

from resource.directory import read_dir
from resource.volume import VolumeReader

DIR_NAMES = ["VIEWDIR", "LOGDIR", "PICDIR", "SNDDIR"]
ABSENT_VOL = 0xF
SIGNATURE = 0x1234
MAX_SLOTS = 256


def expected_entries(game, dir_name):
    return [tuple(e) for e in game.dirs[dir_name]["entries"]]


def first_mismatch(expected, actual):
    """Index of the first slot where the lists differ, or None if they match."""
    diffs = (i for i, (e, a) in enumerate(zip(expected, actual)) if e != a)
    return next(diffs, None if len(expected) == len(actual) else min(len(expected), len(actual)))


def absent_count(entries):
    return sum(vol == ABSENT_VOL for vol, _ in entries)


@pytest.mark.parametrize("dir_name", DIR_NAMES)
class TestDirectory:
    # Golden values: specific to each game.

    def test_slot_count(self, game, dir_name):
        assert len(read_dir(game.path / dir_name)) == len(expected_entries(game, dir_name))

    def test_absent_count(self, game, dir_name):
        actual = read_dir(game.path / dir_name)
        assert absent_count(actual) == absent_count(expected_entries(game, dir_name))

    def test_entries(self, game, dir_name):
        expected, actual = expected_entries(game, dir_name), read_dir(game.path / dir_name)
        slot = first_mismatch(expected, actual)
        at = lambda xs: xs[slot] if slot < len(xs) else "<missing>"
        assert slot is None, f"first mismatch at slot {slot}: expected {at(expected)}, got {at(actual)}"

    # Invariants: hold for any AGI v2 game.

    def test_one_slot_per_triplet(self, game, dir_name):
        path = game.path / dir_name
        assert len(read_dir(path)) == min(path.stat().st_size // 3, MAX_SLOTS)

    def test_present_slots_point_at_valid_headers(self, game, dir_name):
        for slot, (vol, offset) in enumerate(read_dir(game.path / dir_name)):
            if vol == ABSENT_VOL:
                continue
            vol_path = game.path / f"VOL.{vol}"
            reader = VolumeReader(vol_path)
            try:
                header, payload = reader.read_resource(offset)
            finally:
                reader.close()
            assert header.signature == SIGNATURE, f"slot {slot}"
            assert header.vol == vol, f"slot {slot}"
            assert len(payload) == header.length, f"slot {slot}: payload runs past end of {vol_path.name}"
