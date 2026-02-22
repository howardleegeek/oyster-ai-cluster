from typing import Optional


class SecurityConfig:
    max_iterations: int = 3
    review_required: bool = True
    sandbox_mode: bool = True
    branch_isolation: bool = True

    def __init__(
        self,
        max_iterations: int = 3,
        review_required: bool = True,
        sandbox_mode: bool = True,
        branch_isolation: bool = True,
    ):
        self.max_iterations = max_iterations
        self.review_required = review_required
        self.sandbox_mode = sandbox_mode
        self.branch_isolation = branch_isolation

    @classmethod
    def from_request(
        cls,
        max_iterations: Optional[int] = None,
        review_required: Optional[bool] = None,
        sandbox_mode: Optional[bool] = None,
        branch_isolation: Optional[bool] = None,
    ) -> "SecurityConfig":
        return cls(
            max_iterations=max_iterations if max_iterations is not None else 3,
            review_required=review_required if review_required is not None else True,
            sandbox_mode=sandbox_mode if sandbox_mode is not None else True,
            branch_isolation=branch_isolation if branch_isolation is not None else True,
        )

    def model_dump(self) -> dict:
        return {
            "max_iterations": self.max_iterations,
            "review_required": self.review_required,
            "sandbox_mode": self.sandbox_mode,
            "branch_isolation": self.branch_isolation,
        }


class SecurityBoundary:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._current_iteration = 0
        self._review_approved = False

    @property
    def can_iterate(self) -> bool:
        return self._current_iteration < self.config.max_iterations

    @property
    def needs_review(self) -> bool:
        return self.config.review_required and not self._review_approved

    @property
    def is_sandboxed(self) -> bool:
        return self.config.sandbox_mode

    @property
    def is_branch_isolated(self) -> bool:
        return self.config.branch_isolation

    def get_current_iteration(self) -> int:
        return self._current_iteration

    def increment_iteration(self) -> None:
        self._current_iteration += 1

    def approve_review(self) -> None:
        self._review_approved = True

    def validate_task(self, description: str) -> tuple[bool, Optional[str]]:
        if len(description) > 10000:
            return False, "Task description exceeds maximum length of 10000 characters"

        if self.is_sandboxed:
            desc_lower = description.lower()
            for pattern in DANGEROUS_PATTERNS:
                if pattern in desc_lower:
                    return False, f"Dangerous pattern detected: {pattern}"

        return True, None


DANGEROUS_PATTERNS = [
    "rm -rf",
    "delete all",
    "drop table",
    "format disk",
    "shutdown",
    "reboot",
    "--force",
]


def validate_task_security(
    description: str,
    config: SecurityConfig,
) -> tuple[bool, Optional[str]]:
    desc_lower = description.lower()
    
    for pattern in DANGEROUS_PATTERNS:
        if pattern in desc_lower:
            return False, f"Dangerous pattern detected: {pattern}"
    
    if config.max_iterations < 1 or config.max_iterations > 10:
        return False, "Max iterations must be between 1 and 10"
    
    return True, None
