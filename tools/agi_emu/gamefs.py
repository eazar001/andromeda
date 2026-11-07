"""A map of game files, with resource overrides appended to VOL.0 and their DIR repointed."""
from pathlib import Path
import struct

ABSENT = b"\xff\xff\xff"


def load_dir(game_dir) -> dict[str, bytes]:
    """Every regular file in the game directory, keyed by upper-case name."""
    return {p.name.upper(): p.read_bytes() for p in Path(game_dir).iterdir() if p.is_file()}


def dir_entry(vol: int, offset: int) -> bytes:
    return bytes([(vol << 4) | (offset >> 16), (offset >> 8) & 0xFF, offset & 0xFF])


def vol_resource(vol: int, body: bytes) -> bytes:
    return b"\x12\x34" + bytes([vol]) + struct.pack("<H", len(body)) + body


def with_resources(files: dict[str, bytes], directory: str, bodies: dict[int, bytes]) -> dict[str, bytes]:
    """A copy of `files` where each number in `bodies` resolves, through `directory`, to that payload."""
    files = dict(files)
    vol, table = bytearray(files["VOL.0"]), bytearray(files[directory])
    for n, body in sorted(bodies.items()):
        while len(table) < 3 * (n + 1):
            table += ABSENT
        table[3 * n:3 * n + 3] = dir_entry(0, len(vol))
        vol += vol_resource(0, body)
    files["VOL.0"], files[directory] = bytes(vol), bytes(table)
    return files
