import gzip

from faststream_compressors.compressors.base import BaseCompressor, BaseDecompressor
from faststream_compressors import interfaces
from typing import Any


class GzipCompressor(BaseCompressor):
    """A class for compressing data using gzip."""

    ENCODING = "gzip"

    __slots__ = ("__compress_level",)

    def __init__(
        self,
        compress_level: int = 9,
        publish_quality: float = 1.0,
        filter: interfaces.CompressFilter | None = None,
    ):
        """
        Initializes the GzipCompressor with the specified compression level.

        :param compress_level: The level of compression to use (1-9). Default is 9.
        """
        self.__compress_level = compress_level

        super().__init__(publish_quality=publish_quality, filter=filter)

    def __call__(self, data: bytes) -> tuple[bytes, dict[str, Any]]:
        """
        Compresses the provided data using gzip.

        :param data: Data to be compressed.
        :returns: Gzip-compressed data.
        """
        return gzip.compress(data, compresslevel=self.__compress_level), {}


class GzipDecompressor(BaseDecompressor):
    """A class for decompressing gzip-compressed data."""

    ENCODING = "gzip"

    def __call__(self, data: bytes, /, headers: dict[str, Any]) -> bytes:
        """
        Decompresses the provided gzip-compressed data.

        :param data: Gzip-compressed data.
        :returns: Decompressed data.
        """
        return gzip.decompress(data)


__all__ = "GzipCompressor", "GzipDecompressor"
