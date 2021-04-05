from bitarray import bitarray


def bin_to_dec(bits):
    return int.from_bytes(bits.tobytes(), 'big')


def dec_to_bin(dec):
    out = bitarray()
    out.frombytes(dec.to_bytes(2, 'big'))
    return out
