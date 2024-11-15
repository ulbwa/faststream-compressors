from typing import Any
import lz4.frame

from faststream_compressors.compressors.base import BaseCompressor, BaseDecompressor
from faststream_compressors import interfaces


class Lz4Compressor(BaseCompressor):
    """A class for compressing data using LZ4."""

    ENCODING = "lz4"

    def __init__(
        self,
        compression_level: int = 9,
        block_size: int = 0,
        content_checksum: bool = False,
        block_linked: bool = True,
        store_size: bool = False,
        publish_quality: float = 1.0,
        filter: interfaces.CompressFilter | None = None,
    ):
        """
        Initializes the Lz4Compressor.

        :param block_size: Sepcifies the maximum blocksize to use.
        :param  content_checksum: Specifies whether to enable checksumming
            of the uncompressed content. If True, a checksum is stored at the
            end of the frame, and checked during decompression.
        :param block_linked: Specifies whether to use block-linked
            compression. If ``True``, the compression ratio is improved,
            particularly for small block sizes.
        :param store_size: If ``True`` then the frame will include an 8-byte
            header field that is the uncompressed size of data included
            within the frame.
        """
        self.compression_level = compression_level
        self.block_size = block_size
        self.content_checksum = content_checksum
        self.block_linked = block_linked
        self.store_size = store_size

        super().__init__(publish_quality=publish_quality, filter=filter)

    def __call__(self, data: bytes) -> tuple[bytes, dict[str, Any]]:
        """
        Compresses the provided data using LZ4.

        :param data: Data to be compressed.
        :returns: LZ4-compressed data.
        """
        return lz4.frame.compress(
            data,
            compression_level=self.compression_level,
            block_size=self.block_size,
            content_checksum=self.content_checksum,
            block_linked=self.block_linked,
            store_size=self.store_size,
        ), {}


class Lz4Decompressor(BaseDecompressor):
    """A class for decompressing LZ4-compressed data."""

    ENCODING = "lz4"

    def __call__(self, data: bytes, /, headers: dict[str, Any]) -> bytes:
        """
        Decompresses the provided LZ4-compressed data.

        :param data: LZ4-compressed data.
        :returns: Decompressed data.
        """
        return lz4.frame.decompress(data)


__all__ = "Lz4Compressor", "Lz4Decompressor"
