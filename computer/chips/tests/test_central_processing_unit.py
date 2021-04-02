import pytest

from computer.chips.central_processing_unit import CPU


class TestCpu:
    def test_make(self):
        cpu = CPU()
