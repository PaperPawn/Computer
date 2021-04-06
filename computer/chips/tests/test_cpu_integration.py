import pytest

from computer.chips.central_processing_unit import CPU
from computer.chips.memory import RAM32K
from computer.chips.tests.test_central_processing_unit import TestCPUMove, TestCPUStack, MockHardDisk

from computer.utility.numbers import dec_to_bin


class TestCPUIntegration:
    @pytest.fixture
    def cpu(self):
        ram = RAM32K()
        hdd = MockHardDisk()
        return CPU(ram, hdd)

    @staticmethod
    def load_instructions(ram, instructions):
        for i, instruction in enumerate(instructions):
            address = dec_to_bin(i)
            ram(instruction, address[1:], 1)
        ram.tick()


class TestCPUMoveIntegration(TestCPUIntegration, TestCPUMove):
    pass


class TestCPUStackIntegration(TestCPUIntegration, TestCPUStack):
    pass
