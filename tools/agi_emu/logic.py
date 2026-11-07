"""Assemble a LOGIC payload in the 2.917 layout: text offset, bytecode, encrypted text."""
import struct

from opcodes import ACTIONS, TESTS

KEY = b"Avis Durgan"


def _xor(data: bytes) -> bytes:
    return bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(data))


def text_section(messages: list[str]) -> bytes:
    """Count, end pointer and offset table in the clear, then the XORed bodies.

    Pointers count from the byte after the count; message 1 is the first entry.
    """
    bodies = [m.encode("ascii") + b"\0" for m in messages]
    table_end = 2 + 2 * len(bodies)
    offsets, pos = [], table_end
    for b in bodies:
        offsets.append(pos)
        pos += len(b)
    head = bytes([len(bodies)]) + struct.pack("<H", pos) + b"".join(struct.pack("<H", o) for o in offsets)
    return head + _xor(b"".join(bodies))


def payload(code: bytes, messages: list[str] = ()) -> bytes:
    """The resource body that follows the 5-byte VOL header."""
    return struct.pack("<H", len(code)) + bytes(code) + text_section(list(messages))


# ----- bytecode combinators. Each returns bytes, so programs compose by concatenation.
IF, ELSE, NOT, OR = 0xFF, 0xFE, 0xFD, 0xFC


def _args(table, name, args):
    op, argc = table[name]
    if argc is not None and len(args) != argc:
        raise ValueError(f"{name} takes {argc} arguments, got {len(args)}")
    return bytes([op, *args])


def act(name, *args):
    """One action command."""
    return _args(ACTIONS, name, args)


def cond(name, *args):
    """One test command, for use inside `if_`."""
    return _args(TESTS, name, args)


def not_(t):
    return bytes([NOT]) + t


def or_(*tests):
    return bytes([OR]) + b"".join(tests) + bytes([OR])


def said(*words):
    return bytes([TESTS["said"][0], len(words)]) + b"".join(struct.pack("<H", w) for w in words)


def _rel(n):
    return struct.pack("<h", n)


def if_(tests, then, else_=b""):
    """`if (tests) { then } else { else_ }`; the tests in `tests` are ANDed."""
    if else_:
        then = then + bytes([ELSE]) + _rel(len(else_))
    return bytes([IF]) + tests + bytes([IF]) + _rel(len(then)) + then + else_


def goto(offset):
    return bytes([ELSE]) + _rel(offset)


def program(*parts):
    """Concatenate parts and end with `return`."""
    return b"".join(parts) + act("return")
