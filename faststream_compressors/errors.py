class UnknownEncoding(ValueError):
    """Exception raised when an unknown encoding is encountered."""

    def __init__(self, encoding: str):
        super().__init__(f"Unknown encoding: {encoding!r}")


__all__ = ("UnknownEncoding",)
