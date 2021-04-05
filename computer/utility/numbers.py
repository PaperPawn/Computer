from bitarray import bitarray


def bin_to_dec(bits):
    out = 0
    for i, bit in enumerate(bits):
        out += 2 ** (15 - i) * bit
    return out


def dec_to_bin(dec):
    out = bitarray('0'*16)

    for i in range(16):
        bit_number = 2 ** (15 - i)
        if dec >= bit_number:
            dec -= bit_number
            out[i] = 1
    return out
