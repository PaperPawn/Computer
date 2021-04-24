from computer.opcodes import *
from computer.assembler.linker import link
from computer.assembler.tokens import Token, Label
from computer.utility.numbers import dec_to_bin


class TestLinker:
    def test_empty_program_as_boot(self):
        instructions = []
        labels = {}
        variables = {}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == []

    def test_empty_program(self):
        instructions = []
        labels = {}
        variables = {}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(2), dec_to_bin(0)]

    def test_no_labels_as_boot(self):
        instructions = [move_opcode+a_address+constant_address,
                        dec_to_bin(1)]
        labels = {}
        variables = {}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == [move_opcode+a_address+constant_address,
                          dec_to_bin(1)]

    def test_no_labels(self):
        instructions = [move_opcode+a_address+constant_address,
                        dec_to_bin(1)]
        labels = {}
        variables = {}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(4),
                          dec_to_bin(0),
                          move_opcode+a_address+constant_address,
                          dec_to_bin(1)]

    def test_one_label_as_boot(self):
        instructions = [move_opcode + a_address + constant_address,
                        dec_to_bin(1),
                        jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'start', 4)]
        labels = {'start': 0}
        variables = {}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == [move_opcode + a_address + constant_address,
                          dec_to_bin(1),
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(0)]

    def test_one_label_at_start(self):
        instructions = [move_opcode + a_address + constant_address,
                        dec_to_bin(1),
                        jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'start', 4)]
        labels = {'start': 0}
        variables = {}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(9),  # Program length
                          dec_to_bin(0),  # ALlocated space
                          # Loader
                          pop_opcode+a_address+spp_address,
                          alu_opcode+alu_add+constantp_address+a_address,
                          dec_to_bin(8),  # Location of label access
                          # Program
                          move_opcode + a_address + constant_address,
                          dec_to_bin(1),  # Literal
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(0),  # Jump to start
                          ]

    def test_one_label_at_end(self):
        instructions = [jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'end', 1),
                        move_opcode + a_address + constant_address,
                        dec_to_bin(1),
                        ]
        labels = {'end': 4}
        variables = {}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(9),  # Program length
                          dec_to_bin(0),  # ALlocated space
                          # Loader
                          pop_opcode+a_address+spp_address,
                          alu_opcode+alu_add+constantp_address+a_address,
                          dec_to_bin(6),  # Location of label access
                          # Program
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(4),  # Jump to end
                          move_opcode + a_address + constant_address,
                          dec_to_bin(1)  # Literal
                          ]

    def test_two_labels(self):
        instructions = [jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'end', 1),
                        move_opcode + a_address + constant_address,
                        dec_to_bin(1),
                        jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'start', 2),
                        ]
        labels = {'start': 2, 'end': 4}
        variables = {}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(13),  # Program length
                          dec_to_bin(0),  # ALlocated space
                          # Loader
                          pop_opcode+a_address+spp_address,
                          alu_opcode+alu_add+constantp_address+a_address,
                          dec_to_bin(8),  # Location of jump to end
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(12),  # Location of jump to start
                          # Program
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(4),  # jump to end
                          move_opcode + a_address + constant_address,
                          dec_to_bin(1),  # literal
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(2)  # jump to start
                          ]

    def test_alloc_size_1_as_boot(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var', 1)
                        ]
        labels = {}
        variables = {'var': 1}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == [move_opcode+constantp_address+a_address,
                          dec_to_bin(2)]

    def test_double_alloc_size_2_as_boot(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var_1', 1),
                        move_opcode + constantp_address + b_address,
                        Token(Label.Name, 'var_2', 2)
                        ]
        labels = {}
        variables = {'var_1': 1, 'var_2': 1}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == [move_opcode+constantp_address+a_address,
                          dec_to_bin(4),
                          move_opcode + constantp_address + b_address,
                          dec_to_bin(5)]

    def test_double_alloc_size_2_as_boot(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var_1', 1),
                        move_opcode + constantp_address + b_address,
                        Token(Label.Name, 'var_2', 2)
                        ]
        labels = {}
        variables = {'var_1': 2, 'var_2': 2}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == [move_opcode+constantp_address+a_address,
                          dec_to_bin(4),
                          move_opcode + constantp_address + b_address,
                          dec_to_bin(6)]

    def test_alloc_size_1(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var', 1)]
        labels = {}
        variables = {'var': 1}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(7),  # Length of program
                          dec_to_bin(1),  # Allocated memory
                          # Loader
                          pop_opcode + a_address + spp_address,
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(6),  # Location of var access
                          # Program
                          move_opcode+constantp_address+a_address,
                          dec_to_bin(7),  # Accessing var
                          ]

    def test_alloc_size_2(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var', 1)]
        labels = {}
        variables = {'var': 2}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(7),  # Length of program
                          dec_to_bin(2),  # Allocated memory
                          # Loader
                          pop_opcode + a_address + spp_address,
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(6),  # Location of var access
                          # Program
                          move_opcode+constantp_address+a_address,
                          dec_to_bin(7),  # Accessing var
                          ]

    def test_double_alloc_size_1(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var_1', 1),
                        move_opcode + constantp_address + b_address,
                        Token(Label.Name, 'var_2', 2)
                        ]
        labels = {}
        variables = {'var_1': 1, 'var_2': 1}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(11),  # Length of program
                          dec_to_bin(2),  # Allocated memory
                          # Loader
                          pop_opcode + a_address + spp_address,
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(8),  # Location of var_1 access
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(10),  # Location of var_2 access
                          # Program
                          move_opcode+constantp_address+a_address,
                          dec_to_bin(11),  # Accessing var_1
                          move_opcode + constantp_address + b_address,
                          dec_to_bin(12),  # Accessing var_2
                          ]

    def test_double_alloc_size_2(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var_1', 1),
                        move_opcode + constantp_address + b_address,
                        Token(Label.Name, 'var_2', 2)
                        ]
        labels = {}
        variables = {'var_1': 2, 'var_2': 2}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(11),  # Length of program
                          dec_to_bin(4),  # Allocated memory
                          # Loader
                          pop_opcode + a_address + spp_address,
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(8),  # Location of var_1 access
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(10),  # Location of var_2 access
                          # Program
                          move_opcode+constantp_address+a_address,
                          dec_to_bin(11),  # Accessing var_1
                          move_opcode + constantp_address + b_address,
                          dec_to_bin(13),  # Accessing var_2
                          ]

    def test_alloc_size_1_with_label_as_boot(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var', 1),
                        jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'start', 2)
                        ]
        labels = {'start': 0}
        variables = {'var': 1}

        linked = link(instructions, labels, variables, mode='boot')
        assert linked == [move_opcode+constantp_address+a_address,
                          dec_to_bin(4),  # accessing var
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(0)  # jump to label start
                          ]

    def test_alloc_size_1_with_label(self):
        instructions = [move_opcode+constantp_address+a_address,
                        Token(Label.Name, 'var', 1),
                        jump_opcode + unused_opcode + constant_address,
                        Token(Label.Name, 'start', 2)
                        ]
        labels = {'start': 0}
        variables = {'var': 1}

        linked = link(instructions, labels, variables)
        assert linked == [dec_to_bin(11),  # Length of program
                          dec_to_bin(1),  # Allocated memory
                          # Loader
                          pop_opcode + a_address + spp_address,
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(8),  # Location of var access
                          alu_opcode + alu_add + constantp_address + a_address,
                          dec_to_bin(10),  # Location of start label jump
                          # Program
                          move_opcode+constantp_address+a_address,
                          dec_to_bin(11),  # accessing var
                          jump_opcode + unused_opcode + constant_address,
                          dec_to_bin(0)  # jump to label start
                          ]

    # def test_triple_alloc_size_2_with_2_labels(self):
    #     instructions = [move_opcode+constantp_address+a_address,
    #                     Token(Label.Name, 'var', 1),
    #                     jump_opcode + unused_opcode + constant_address,
    #                     Token(Label.Name, 'start', 2)
    #                     ]
    #     labels = {'start': 0, 'func': }
    #     variables = {'var_1': 3, 'var_2': 1, 'var_3': 1}
    #
    #     linked = link(instructions, labels, variables)
    #     assert linked == [dec_to_bin(11),  # Length of program
    #                       dec_to_bin(1),  # Allocated memory
    #                       # Loader
    #                       pop_opcode + a_address + spp_address,
    #                       alu_opcode + alu_add + constantp_address + a_address,
    #                       dec_to_bin(8),  # Location of var access
    #                       alu_opcode + alu_add + constantp_address + a_address,
    #                       dec_to_bin(10),  # Location of start label jump
    #                       # Program
    #                       move_opcode+constantp_address+a_address,
    #                       dec_to_bin(11),  # accessing var
    #                       jump_opcode + unused_opcode + constant_address,
    #                       dec_to_bin(0)  # jump to label start
    #                       ]
