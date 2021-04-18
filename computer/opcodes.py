from bitarray import bitarray

reset_opcode = bitarray('0'*16)
shutdown_opcode = bitarray('0001') + bitarray('0'*12)

push_opcode = bitarray('00110000')
pop_opcode = bitarray('00111000')

move_opcode = bitarray('00100000')

hdd_opcode = bitarray('0010')
hdd_set_sector = bitarray('1100')
hdd_read = bitarray('1000')
hdd_write = bitarray('1010')

alu_opcode = bitarray('1010')
alu_no_move_opcode = bitarray('1000')

alu_pass = bitarray('0000')

alu_add = bitarray('0100')
alu_sub = bitarray('0101')
alu_neg = bitarray('0001')
alu_inc = bitarray('0010')
alu_dec = bitarray('0011')

alu_and = bitarray('1010')
alu_or = bitarray('1100')
alu_xor = bitarray('1110')
alu_not = bitarray('1001')

jump_opcode = bitarray('01000000')
jump_zero_opcode = bitarray('01100000')
jump_neg_opcode = bitarray('01010000')
jump_overflow_opcode = bitarray('01110000')

call_opcode = bitarray('01000100')
# push_opcode = bitarray('00110000')
# pop_opcode = bitarray('00111000')
return_opcode = bitarray('01000010')

unused_opcode = bitarray('0000')

# address as value
a_address = bitarray('0000')
b_address = bitarray('0001')
c_address = bitarray('0010')
d_address = bitarray('0011')

sp_address = bitarray('0100')  # stack pointer as value
constant_address = bitarray('0101')  # pc register +1 as value

# address as pointer
ap_address = bitarray('1000')
bp_address = bitarray('1001')
cp_address = bitarray('1010')
dp_address = bitarray('1011')

spp_address = bitarray('1100')  # stack pointer as pointer
constantp_address = bitarray('1101')  # pc register +1 as pointer
