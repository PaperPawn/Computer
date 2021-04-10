import pytest

from computer.chips.central_processing_unit import CPU
from computer.chips.memory import RAM32K

from computer.chips.tests import test_central_processing_unit as test_cpu

from computer.utility.numbers import dec_to_bin


class TestCPUIntegration:
    @pytest.fixture
    def cpu(self):
        ram = RAM32K()
        hdd = test_cpu.MockHardDisk()
        return CPU(ram, hdd)

    @staticmethod
    def load_instructions(ram, instructions):
        for i, instruction in enumerate(instructions):
            address = dec_to_bin(i)
            ram(instruction, address[1:], 1)
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
