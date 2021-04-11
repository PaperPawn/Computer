def get_bitarray_string(bits):
    return str(bits.copy()).replace("bitarray('", '').replace("')", '')