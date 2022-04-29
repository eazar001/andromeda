def nibble(byte, section, endian='big'):
    if endian == 'little':
        section = 'lo' if section == 'hi' else section

    return (240 & byte) >> 4 if section == 'hi' else 15 & byte
