class InvalidNFTError(Exception):
    """Raised when an invalid NFT ID is provided."""
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class UnauthorizedError(Exception):
    """Raised when an invalid NFT ID is provided."""
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class InvalidOrderError(Exception):
    """Raised when an order has invalid product configuration."""
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)