import gzip

from faststream_compressors.compressors import BaseCompressor


class GzipCompressor(BaseCompressor):
    """A class for compressing data using gzip."""

    ENCODING = "gzip"

    def __init__(self, compress_level: int = 9):
        """
        Initializes the GzipCompressor with the specified compression level.

        :param compress_level: The level of compression to use (1-9). Default is 9.
        """
        self.compress_level = compress_level

    def __call__(self, data: bytes) -> bytes:
        """
        Compresses the provided data using gzip.

        :param data: Data to be compressed.
        :returns: Compressed data.
        """
        return gzip.compress(data, compresslevel=self.compress_level)


class GzipDecompressor(BaseCompressor):
    """A class for decompressing gzip-compressed data."""

    ENCODING = "gzip"

    def __call__(self, data: bytes) -> bytes:
        """
        Decompresses the provided gzip-compressed data.

        :param data:Gzip-compressed data.
        :returns: Decompressed data.
        """
        return gzip.decompress(data)


__all__ = ("GzipCompressor", "GzipDecompressor")
