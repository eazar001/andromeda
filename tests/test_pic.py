import pytest

from resource.directory import read_dir
from resource.pic import preprocess_pic_stream
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
