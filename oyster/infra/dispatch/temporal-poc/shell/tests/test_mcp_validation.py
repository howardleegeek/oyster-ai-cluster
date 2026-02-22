import unittest

from src.mcp_validation import validate_mcp_post_cleanup


class TestMCPValidationPostCleanup(unittest.TestCase):
    def test_all_servers_healthy(self):
        state = {
            "servers": [
                {"name": "a", "health": "healthy"},
                {"name": "b", "health": "ok"},
            ],
            "web3_integration": {"enabled": True},
        }
        res = validate_mcp_post_cleanup(state)
        self.assertTrue(res["ok"])
        self.assertEqual(len(res["issues"]), 0)

    def test_detect_issues_without_web3(self):
        state = {
            "servers": [
                {"name": "a", "health": "healthy"},
                {"name": "b", "health": "degraded"},
            ],
            "web3_integration": {"enabled": False},
        }
        res = validate_mcp_post_cleanup(state)
        self.assertFalse(res["ok"])
        self.assertIn("Server 'b' health is 'degraded'", res["issues"])

    def test_web3_enabled_requires_all_healthy(self):
        state = {
            "servers": [
                {"name": "a", "health": "healthy"},
                {"name": "b", "health": "degraded"},
            ],
            "web3_integration": {"enabled": True},
        }
        res = validate_mcp_post_cleanup(state)
        self.assertFalse(res["ok"])
        self.assertIn("Server 'b' health is 'degraded'", res["issues"])

    def test_missing_health_treated_as_issue(self):
        state = {
            "servers": [
                {"name": "a"},  # missing health
            ],
            "web3_integration": {"enabled": False},
        }
        res = validate_mcp_post_cleanup(state)
        self.assertFalse(res["ok"])
        # Should report at least one issue due to missing health information
        self.assertGreaterEqual(len(res["issues"]), 1)


if __name__ == "__main__":
    unittest.main()
