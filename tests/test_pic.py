import pytest

from resource.directory import read_dir
from resource.pic import (
    AbsoluteLine, DisablePriorityDraw, DisableVisualDraw, EndOfPicture, FloodFill, NoOp,
    PlotWithPen, RelativeLine, SetPenStyle, SetPriorityColor, SetVisualColor, XCorner,
    YCorner, decode_bytes, decode_pic, preprocess_pic_stream,
)
from resource.volume import VolumeReader

ABSENT_VOL = 0xF
END = 0xFF
FIRST_OPCODE = 0xF0


def cmds(*hex_strings):
    return [bytes.fromhex(h) for h in hex_strings]


# Spec: andromeda-wiki/entities/picture.md, "Bytecode dispatch" and "Opcode catalogue".
# Deliberately unpinned (undecided): a unary opcode as the payload's last byte, and how
# 0xFB..0xFE or stray bytes below 0xF0 are grouped.
@pytest.mark.parametrize("payload, expected", [
    pytest.param("", [], id="empty"),
    pytest.param("ff", cmds("ff"), id="end-only"),
    pytest.param("f0 0e f1 ff 99", cmds("f0 0e", "f1", "ff"), id="end-drops-trailing"),
    pytest.param("f1 f3 ff", cmds("f1", "f3", "ff"), id="nullary-f1-f3"),
    pytest.param("f2 03 f9 10 ff", cmds("f2 03", "f9 10", "ff"), id="unary-f2-f9"),
    pytest.param("f0 ff f2 03 ff", cmds("f0 ff", "f2 03", "ff"), id="unary-takes-ff"),
    pytest.param("f9 f6 f3 ff", cmds("f9 f6", "f3", "ff"), id="unary-takes-opcode"),
    pytest.param("f6 10 20 f8 01 02 ff", cmds("f6 10 20", "f8 01 02", "ff"), id="variable-f6-f8"),
    pytest.param("f4 01 02 03 f5 04 05 06 ff", cmds("f4 01 02 03", "f5 04 05 06", "ff"), id="variable-f4-f5"),
    pytest.param("f7 10 20 33 fa 01 02 ff", cmds("f7 10 20 33", "fa 01 02", "ff"), id="variable-f7-fa"),
    pytest.param("f8 f6 01 f0 05 ff", cmds("f8", "f6 01", "f0 05", "ff"), id="variable-no-args"),
    pytest.param("f6 10 20", cmds("f6 10 20"), id="variable-at-payload-end"),
])
def test_preprocess_pic_stream(payload, expected):
    assert preprocess_pic_stream(bytes.fromhex(payload)) == expected


# Spec: andromeda-wiki/entities/picture.md, "Opcode catalogue" and "Bytecode dispatch".
# Pairs drop a partly read group [picture.md, "Bytecode dispatch"]. 0xFA's arguments stay
# flat until its pairs-vs-triples grouping, which depends on the pen style, is decided.
# Deliberately unpinned: a unary opcode with no argument byte.
@pytest.mark.parametrize("command, expected", [
    pytest.param("f0 0e", SetVisualColor(color=0x0E), id="f0-visual-color"),
    pytest.param("f1", DisableVisualDraw(), id="f1-disable-visual"),
    pytest.param("f2 03", SetPriorityColor(color=0x03), id="f2-priority-color"),
    pytest.param("f3", DisablePriorityDraw(), id="f3-disable-priority"),
    pytest.param("f4 01 02 03", YCorner(coord=[1, 2, 3]), id="f4-y-corner"),
    pytest.param("f5 04 05 06", XCorner(coord=[4, 5, 6]), id="f5-x-corner"),
    pytest.param("f6 10 20 30 40", AbsoluteLine(coord=[(0x10, 0x20), (0x30, 0x40)]), id="f6-pairs"),
    pytest.param("f6 10 20 30", AbsoluteLine(coord=[(0x10, 0x20)]), id="f6-drops-partial-pair"),
    pytest.param("f6", AbsoluteLine(coord=[]), id="f6-no-args"),
    pytest.param("f7 10 20 33", RelativeLine(coord=[0x10, 0x20, 0x33]), id="f7-relative-line"),
    pytest.param("f8 01 02 03 04", FloodFill(coord=[(1, 2), (3, 4)]), id="f8-pairs"),
    pytest.param("f8 01", FloodFill(coord=[]), id="f8-drops-partial-pair"),
    pytest.param("f9 10", SetPenStyle(style=0x10), id="f9-pen-style"),
    pytest.param("fa 01 02", PlotWithPen(coord=[1, 2]), id="fa-plot-with-pen"),
    pytest.param("fb", NoOp(), id="fb-skipped"),
    pytest.param("fe", NoOp(), id="fe-skipped"),
    pytest.param("05", NoOp(), id="stray-byte-skipped"),
    pytest.param("ff", EndOfPicture(), id="ff-end"),
])
def test_decode_bytes(command, expected):
    assert decode_bytes(bytes.fromhex(command)) == expected


@pytest.mark.parametrize("payload, expected", [
    pytest.param("", [], id="empty"),
    pytest.param("ff", [EndOfPicture()], id="end-only"),
    pytest.param("f1 ff", [DisableVisualDraw(), EndOfPicture()], id="nullary-then-end"),
    pytest.param("f0 01 f7 01 02 f9 03 ff",
                 [SetVisualColor(color=1), RelativeLine(coord=[1, 2]), SetPenStyle(style=3),
                  EndOfPicture()],
                 id="one-op-per-command"),
    pytest.param("f0 0e ff 99", [SetVisualColor(color=0x0E), EndOfPicture()], id="end-drops-trailing"),
])
def test_decode_pic(payload, expected):
    assert decode_pic(bytes.fromhex(payload)) == expected


# Skipped bytes draw nothing; how many NoOps they become is unpinned, like their grouping.
@pytest.mark.parametrize("payload, expected", [
    pytest.param("fb 01 02 f1 ff", [DisableVisualDraw(), EndOfPicture()], id="fb-and-its-bytes"),
    pytest.param("fe f3 ff", [DisablePriorityDraw(), EndOfPicture()], id="fe-alone"),
    pytest.param("05 06 f1 ff", [DisableVisualDraw(), EndOfPicture()], id="stray-bytes"),
])
def test_decode_pic_skips_ignored_bytes(payload, expected):
    ops = decode_pic(bytes.fromhex(payload))
    assert [op for op in ops if op != NoOp()] == expected


def pictures(game):
    """Yield (slot, payload) for every present PICTURE in the game."""
    for slot, (vol, offset) in enumerate(read_dir(game.path / "PICDIR")):
        if vol == ABSENT_VOL:
            continue
        reader = VolumeReader(game.path / f"VOL.{vol}")
        try:
            yield slot, reader.read_resource(offset)[1]
        finally:
            reader.close()


def test_preprocess_round_trips_every_picture(game):
    for slot, payload in pictures(game):
        # The first 0xFF is the terminator only if no fixed argument is 0xFF.
        # Holds for SQ1, which never passes a color above 15 [picture.md, "Opcode catalogue"].
        body = payload[:payload.index(END) + 1]
        commands = preprocess_pic_stream(payload)
        assert b"".join(commands) == body, f"picture {slot}"
        assert all(c[0] >= FIRST_OPCODE for c in commands), f"picture {slot}"
        assert commands[-1] == bytes([END]), f"picture {slot}"


def test_decode_every_picture(game):
    for slot, payload in pictures(game):
        commands = preprocess_pic_stream(payload)
        ops = decode_pic(payload)
        assert len(ops) == len(commands), f"picture {slot}"
        assert ops[-1] == EndOfPicture(), f"picture {slot}"
        assert EndOfPicture() not in ops[:-1], f"picture {slot}"
        for op in ops:
            if isinstance(op, (AbsoluteLine, FloodFill)):
                assert all(len(p) == 2 for p in op.coord), f"picture {slot}: {op}"
