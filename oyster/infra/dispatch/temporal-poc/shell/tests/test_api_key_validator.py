import unittest

from src.api_key_validator import is_valid_api_key, fix_external_api_key


class TestApiKeyValidator(unittest.TestCase):
    def test_valid_key_passes(self):
        self.assertTrue(is_valid_api_key("sk-abcdef123456"))
        self.assertEqual(fix_external_api_key("sk-abcdef123456"), "sk-abcdef123456")

    def test_invalid_key_rejected(self):
        self.assertFalse(is_valid_api_key(""))
        self.assertFalse(is_valid_api_key("   "))
        self.assertFalse(is_valid_api_key("short"))
        self.assertEqual(fix_external_api_key(""), "")

    def test_key_with_spaces_invalid(self):
        self.assertFalse(is_valid_api_key("abc def"))
        self.assertEqual(fix_external_api_key("abc def"), "")


if __name__ == "__main__":
    unittest.main()
