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


class InvalidOrder(Exception):
    def __init__(self, msg: str):
        self.msg = msg 
        super().__init__(msg)

