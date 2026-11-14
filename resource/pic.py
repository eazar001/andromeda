from enum import Enum


class PicOp:
    pass


class OpType(Enum):
    NULLARY = 0
    UNARY = 1
    VARIABLE = 2


def decode_pic(payload: bytes) -> list[PicOp]:
    pass


def preprocess_pic_stream(payload: bytes) -> list[bytes]:
    op_type = None
    nullary, unary, no_op = {0xF1, 0xF3, 0xFF}, {0xF0, 0xF2, 0xF9}, {0xFB, 0xFC, 0xFD, 0xFE}
    rest = payload[:]
    bs = []

    for b in rest:
        if b in nullary:
            op_type = OpType.NULLARY
            command, rest = parse(rest, OpType.NULLARY)
            bs.append(command)
        elif b in unary:
            op_type = OpType.UNARY
            command, rest = parse(rest, OpType.UNARY)


        command, rest = parse(rest, op_type)


# returns a tuple with a bytes array for the full command and a bytes array for the remainder
# of the stream
def parse(bs: bytes, op_type: OpType) -> tuple[bytes, bytes]:
    if op_type == OpType.NULLARY:
        return bytes(bs[0]), bs[1:]

    if op_type == OpType.UNARY:
        return bs[:2], bs[2:]

    command = [bs[0]]

    for b in bs[1:]:
        if b >= 0xF0:
            command.append(b)
            break

        command.append(b)

    return bytes(command), bs[len(command):]


def no_op(x: int) -> bool:
    return