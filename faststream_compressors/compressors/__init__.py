from abc import ABC, abstractmethod
from typing import ClassVar


class BaseCompressor(ABC):
    """
    Abstract base class for all compressors.

    :cvar ENCODING: String representation of the compression scheme used. E.g. "gzip" and "lz4".
    """

    ENCODING: ClassVar[str]

    @abstractmethod
    def __call__(self, data: bytes) -> bytes:
        """
        Compresses the provided data.
        This method must be overridden in a subclass.

        :param data: Data to be compressed.
        :returns: Compressed data.
        """


from faststream_compressors.compressors.gzip import *  # noqa: F401

__all__ = ("BaseCompressor",) + gzip.__all__
