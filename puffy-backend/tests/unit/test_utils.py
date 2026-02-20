"""Unit tests for utility functions."""

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestUtils:
    """Test cases for utility functions in app/utils.py and app/plib/utils.py."""

    def test_gen_random_hex_str_length(self):
        """Test that gen_random_hex_str generates correct length."""
        from app.plib.utils import gen_random_hex_str

        for length in [8, 16, 20, 32]:
            result = gen_random_hex_str(length)
            assert len(result) == length * 2  # hex doubles the length

    def test_gen_random_hex_str_is_hexadecimal(self):
        """Test that gen_random_hex_str returns valid hexadecimal."""
        from app.plib.utils import gen_random_hex_str

        result = gen_random_hex_str(16)
        try:
            int(result, 16)
        except ValueError:
            pytest.fail("gen_random_hex_str did not return valid hexadecimal")

    def test_gen_random_hex_str_uniqueness(self):
        """Test that gen_random_hex_str generates unique values."""
        from app.plib.utils import gen_random_hex_str

        results = [gen_random_hex_str(16) for _ in range(100)]
        unique_results = set(results)

        # High probability of uniqueness for 100 samples
        assert len(unique_results) > 95
