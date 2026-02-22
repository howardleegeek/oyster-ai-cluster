import pytest
from agent_sdk.security import SecurityBoundary, SecurityConfig, validate_task_security


class TestSecurityConfig:
    def test_default_config(self):
        config = SecurityConfig()
        assert config.max_iterations == 3
        assert config.review_required is True
        assert config.sandbox_mode is True
        assert config.branch_isolation is True

    def test_custom_config(self):
        config = SecurityConfig(
            max_iterations=5,
            review_required=False,
            sandbox_mode=False,
            branch_isolation=False,
        )
        assert config.max_iterations == 5
        assert config.review_required is False
        assert config.sandbox_mode is False
        assert config.branch_isolation is False

    def test_from_request(self):
        config = SecurityConfig.from_request(
            max_iterations=7,
            review_required=False,
        )
        assert config.max_iterations == 7
        assert config.review_required is False
        assert config.sandbox_mode is True
        assert config.branch_isolation is True

    def test_max_iterations_bounds(self):
        config = SecurityConfig(max_iterations=0)
        is_valid, error = validate_task_security("test", config)
        assert is_valid is False
        
        config = SecurityConfig(max_iterations=11)
        is_valid, error = validate_task_security("test", config)
        assert is_valid is False


class TestSecurityBoundary:
    def test_initial_state(self):
        config = SecurityConfig(max_iterations=3)
        boundary = SecurityBoundary(config)
        assert boundary.can_iterate is True
        assert boundary.needs_review is True
        assert boundary.is_sandboxed is True
        assert boundary.is_branch_isolated is True
        assert boundary.get_current_iteration() == 0

    def test_iteration_limit(self):
        config = SecurityConfig(max_iterations=2)
        boundary = SecurityBoundary(config)
        boundary.increment_iteration()
        assert boundary.get_current_iteration() == 1
        assert boundary.can_iterate is True
        boundary.increment_iteration()
        assert boundary.get_current_iteration() == 2
        assert boundary.can_iterate is False

    def test_validate_task_valid(self):
        config = SecurityConfig()
        boundary = SecurityBoundary(config)
        valid, error = boundary.validate_task("Get the user information")
        assert valid is True
        assert error is None

    def test_validate_task_too_long(self):
        config = SecurityConfig()
        boundary = SecurityBoundary(config)
        long_description = "x" * 10001
        valid, error = boundary.validate_task(long_description)
        assert valid is False
        assert "exceeds maximum length" in error

    def test_validate_task_dangerous_pattern_sandbox(self):
        config = SecurityConfig(sandbox_mode=True)
        boundary = SecurityBoundary(config)
        valid, error = boundary.validate_task("Please run rm -rf / on the server")
        assert valid is False
        assert "Dangerous pattern detected" in error

    def test_validate_task_no_restriction_non_sandbox(self):
        config = SecurityConfig(sandbox_mode=False)
        boundary = SecurityBoundary(config)
        valid, error = boundary.validate_task("Please run rm -rf / on the server")
        assert valid is True
