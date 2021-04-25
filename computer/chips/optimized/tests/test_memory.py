import pytest

from computer.chips.tests import test_memory

from computer.chips.optimized.memory import RAM8K, RAM32K, CombinedRAM


class TestOptimizedRAM8K(test_memory.TestRam8K):
    @pytest.fixture
    def ram(self):
        return RAM8K()


class TestOptimizedRAM32K(test_memory.TestRam32K):
    @pytest.fixture
    def ram(self):
        return RAM32K()


class TestOptimizedCombinedRAM(test_memory.TestCombinedRAM):
    @pytest.fixture
    def ram(self):
        return CombinedRAM()
