def nibble(byte, section):
    return (240 & byte) >> 4 if section == 'hi' else 15 & byte
