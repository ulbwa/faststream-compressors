class UnknownEncoding(ValueError):
    """Exception raised when an unknown encoding is encountered."""

    def __init__(self, encoding: str):
        super().__init__(f"Unknown encoding: {encoding!r}")


class UnacceptableAcceptEncoding(ValueError):
    """Exception raised when the requested encoding is not acceptable."""

    def __init__(self, value: str):
        super().__init__(f"Unacceptable Accept-Encoding: {value!r}")


class UnacceptableContentEncoding(ValueError):
    """Exception raised when the content encoding is not acceptable."""

    def __init__(self, value: str):
        super().__init__(f"Unacceptable Content-Encoding: {value!r}")


__all__ = "UnknownEncoding", "UnacceptableAcceptEncoding", "UnacceptableContentEncoding"
