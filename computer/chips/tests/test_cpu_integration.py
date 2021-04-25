import pytest

from computer.chips.memory import CombinedRAM

from computer.chips.tests import test_central_processing_unit as test_cpu

from computer.utility.numbers import dec_to_bin


class TestCPUIntegration:
    @staticmethod
    def make_ram():
        return CombinedRAM()

    @staticmethod
    def load_instructions(ram, instructions):
        for i, instruction in enumerate(instructions):
            address = dec_to_bin(i)
            ram(instruction, address, 1)
        ram.tick()


class TestCPUMoveIntegration(TestCPUIntegration, test_cpu.TestCPUMove):
    pass


class TestCPUStackIntegration(TestCPUIntegration, test_cpu.TestCPUStack):
    pass


class TestCPUALUIntegration(TestCPUIntegration, test_cpu.TestCPUALU):
    pass


class TestCPUJumpIntegration(TestCPUIntegration, test_cpu.TestCPUJump):
    pass


class TestCPUJumpZeroIntegration(TestCPUIntegration, test_cpu.TestCPUJumpZero):
    pass


class TestCPUJumpNegativeIntegration(TestCPUIntegration, test_cpu.TestCPUJumpNegative):
    pass


class TestCPUJumpOverflowIntegration(TestCPUIntegration, test_cpu.TestCPUJumpOverflow):
    pass


class TestCPUResetIntegration(TestCPUIntegration, test_cpu.TestCPUReset):
    pass


class TestCPUHDDIntegration(TestCPUIntegration, test_cpu.TestCPUHDD):
    pass


class TestCpuCallReturnIntegration(TestCPUIntegration, test_cpu.TestCpuCallReturn):
    pass
