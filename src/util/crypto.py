from itertools import cycle


def xor_cycle(key_string, file):
    with open(file, mode='rb') as f:
        return bytearray(map(lambda t: t[0] ^ t[1], zip(list(f.read()), cycle(map(ord, key_string)))))
