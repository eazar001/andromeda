def nibble(byte, section):
    return (240 & byte) >> 4 if section == 'hi' else 15 & byte

# returns mirror bit, and the non-mirror loop index, given a nibble
def cel_mirror(n):
    return n >> 3, n & 7