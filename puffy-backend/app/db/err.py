class RepoError(Exception):
    """Base class for repository exceptions."""
    pass


class RecordNotFoundError(RepoError):
    """Raised when a record is not found."""
    def __init__(self, message="Record not found"):
        super().__init__(message)


class FieldNotFoundError(RepoError):
    """Raised when a record is not found."""
    def __init__(self, message="Field not found"):
        super().__init__(message)


class RecordAlreadyExistsError(RepoError):
    """Raised when a record already exists."""
    def __init__(self, message="Record already exists"):
        super().__init__(message)


class EntityDoesNotExist(RepoError):
    def __init__(self, message="Entity does not exist"):
        super().__init__(message)

