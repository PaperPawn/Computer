from bitarray import bitarray


def bin_to_dec(bits):
    if len(bits) != 16:
        msg = f'bitarray must be 16 long, is {len(bits)}'
        print(msg)
        raise Exception(msg)
    return int.from_bytes(bits.tobytes(), 'big')


def dec_to_bin(dec):
    out = bitarray()
    out.frombytes(dec.to_bytes(2, 'big'))
    return out
