import lzma
from typing import Any

from faststream_compressors.compressors.base import BaseCompressor, BaseDecompressor
from faststream_compressors import interfaces


class LzmaCompressor(BaseCompressor):
    """A class for compressing data using lzma."""

    ENCODING = "lzma"

    def __init__(
        self,
        check: int = -1,
        preset: int | None = None,
        publish_quality: float = 1.0,
        filter: interfaces.CompressFilter | None = None,
    ):
        self.check = check
        self.preset = preset

        super().__init__(publish_quality=publish_quality, filter=filter)

    def __call__(self, data: bytes) -> tuple[bytes, dict[str, Any]]:
        """
        Compresses the provided data using lzma.

        :param data: Data to be compressed.
        :returns: Compressed data.
        """
        return lzma.compress(data, check=self.check, preset=self.preset), {}


class LzmaDecompressor(BaseDecompressor):
    """A class for decompressing lzma-compressed data."""

    ENCODING = "lzma"

    def __call__(self, data: bytes, /, headers: dict[str, Any]) -> bytes:
        """
        Decompresses the provided lzma-compressed data.

        :param data:Lzma-compressed data.
        :returns: Decompressed data.
        """
        return lzma.decompress(data)


__all__ = "LzmaCompressor", "LzmaDecompressor"
