import struct

from image import load_mz
from logic import KEY, act, cond, if_, not_, payload, program, said, text_section
from gamefs import dir_entry, with_resources


def tiny_mz(body, relocs, cs=0, ip=0, ss=0, sp=0x100):
    hdr_par = 2
    rel_off = 0x1C
    size = hdr_par * 16 + len(body)
    head = struct.pack("<2sHHHHHHHHHHHHH", b"MZ", size % 512, (size + 511) // 512, len(relocs),
                       hdr_par, 0, 0xFFFF, ss, sp, 0, ip, cs, rel_off, 0)
    head += b"".join(struct.pack("<HH", o, s) for o, s in relocs)
    return head.ljust(hdr_par * 16, b"\0") + body


def test_relocations_add_load_segment():
    img = load_mz(tiny_mz(b"\x34\x12\x00\x00", [(0, 0)], cs=1, ss=2), 0x1000)
    assert img.data[:2] == struct.pack("<H", 0x2234)
    assert (img.cs, img.ss, img.sp) == (0x1001, 0x1002, 0x100)


def test_text_section_layout_and_encryption():
    sec = text_section(["Hi", "x"])
    assert sec[0] == 2
    end, m1, m2 = struct.unpack_from("<HHH", sec, 1)
    assert (m1, m2) == (6, 9) and end == len(sec) - 1
    plain = bytes(b ^ KEY[i % 11] for i, b in enumerate(sec[7:]))
    assert plain == b"Hi\0x\0"


def test_payload_text_offset_counts_bytecode():
    body = payload(b"\x00", [])
    assert body == b"\x01\x00" + b"\x00" + b"\x00\x02\x00"


def test_override_appends_and_repoints():
    files = {"VOL.0": b"\xAA" * 10, "LOGDIR": b"\xff\xff\xff"}
    out = with_resources(files, "LOGDIR", {2: b"code"})
    assert out["LOGDIR"][6:9] == dir_entry(0, 10)
    assert out["VOL.0"][10:] == b"\x12\x34\x00\x04\x00code"
    assert files["VOL.0"] == b"\xAA" * 10


def test_act_checks_argument_count():
    import pytest
    assert act("assignn", 30, 5) == b"\x03\x1e\x05"
    with pytest.raises(ValueError):
        act("assignn", 30)


def test_if_skips_then_and_else_jumps_over_else():
    then, other = act("increment", 30), act("decrement", 30)
    code = if_(cond("isset", 40), then, other)
    # FF test FF off(then + FE off) then FE off(else) else
    assert code[:4] == b"\xff\x07\x28\xff"
    assert struct.unpack_from("<h", code, 4)[0] == len(then) + 3
    assert code[6:8] == then and code[8] == 0xFE
    assert struct.unpack_from("<h", code, 9)[0] == len(other) and code[11:] == other


def test_said_and_not_and_program():
    assert said(1, 0x0102) == b"\x0e\x02\x01\x00\x02\x01"
    assert not_(cond("isset", 1)) == b"\xfd\x07\x01"
    assert program(act("increment", 30)) == b"\x01\x1e\x00"


def test_view_layout_matches_the_project_decoder():
    import io, sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from resource.view import get_view_data
    from resource.volume import VolumeReader
    from resources import view
    body = view([([[1, 1, 3], [2, 3, 3]], 3)])
    path = pathlib.Path(__file__).with_name("_view.vol")
    path.write_bytes(b"\x12\x34\x00" + struct.pack("<H", len(body)) + body)
    reader = VolumeReader(str(path))
    try:
        v = get_view_data(reader, 0)
    finally:
        reader.close()
        path.unlink()
    c = v.loops[0].cels[0]
    assert (c.width, c.height, c.alpha) == (3, 2, 3)
    assert [p for p in c.cel_data if p != (0, 0)] == [(1, 2), (2, 1)]
