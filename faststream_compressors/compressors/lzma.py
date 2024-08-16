import lzma

from faststream_compressors.compressors import BaseCompressor


class LzmaCompressor(BaseCompressor):
    """A class for compressing data using lzma."""

    ENCODING = "lzma"

    def __call__(self, data: bytes) -> bytes:
        """
        Compresses the provided data using lzma.

        :param data: Data to be compressed.
        :returns: Compressed data.
        """
        return lzma.compress(data)


class LzmaDecompressor(BaseCompressor):
    """A class for decompressing lzma-compressed data."""

    ENCODING = "lzma"

    def __call__(self, data: bytes) -> bytes:
        """
        Decompresses the provided lzma-compressed data.

        :param data:Lzma-compressed data.
        :returns: Decompressed data.
        """
        return lzma.decompress(data)


__all__ = ("LzmaCompressor", "LzmaDecompressor")
