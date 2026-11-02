"""What andromeda-wiki/entities/picture.md records about showpic.c."""
from showpic_model import SPLATTER_START_PROSE, SPLATTER_START_SHOWPIC, offset_disagreements, render


def test_offset_tables_have_120_entries():
    assert len(SPLATTER_START_PROSE) == len(SPLATTER_START_SHOWPIC) == 120


def test_spec_prose_offsets_all_match_the_shift_register():
    assert offset_disagreements(SPLATTER_START_PROSE) == []


def test_showpic_offsets_are_wrong_at_four_indices():
    assert offset_disagreements(SPLATTER_START_SHOWPIC) == [11, 15, 116, 117]


def test_stale_white_blocks_a_priority_only_fill_as_shipped():
    stream = bytes([0xF0, 0x0F, 0xF1, 0xF2, 5, 0xF8, 10, 10, 0xFF])
    blank = bytes([0x4F]) * (160 * 168)
    assert render(stream) == blank
    assert render(stream, stale_color=False) != blank
