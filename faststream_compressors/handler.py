from abc import ABC

from faststream_compressors.compressors import BaseCompressor
from faststream_compressors.errors import UnknownEncoding


class BaseCompressorHandler(ABC):
    """
    Abstract base class for compressor handlers.

    :param compressors: A sequence of compressors to be managed by the handler.
    """

    def __init__(self, *compressors: BaseCompressor):
        self.compressors = compressors

    def get_compressor(self, encoding: str) -> BaseCompressor:
        """
        Retrieves the compressor corresponding to the given encoding.

        :param encoding: The encoding of the compressor to retrieve.
        :returns: The compressor corresponding to the given encoding.
        :raises UnknownEncoding: If no compressor with the given encoding is found.
        """
        compressor: BaseCompressor | None = next(
            filter(lambda x: encoding == x.ENCODING, self.compressors), None
        )
        if not compressor:
            raise UnknownEncoding(encoding)
        return compressor


class CompressorHandler(BaseCompressorHandler):
    """Handles the compression of message data."""

    def __call__(self, data: bytes) -> tuple[bytes, str | None]:
        """
        Compresses the provided data using the sequence of compressors.

        :param data: The data to be compressed.
        :return: A tuple of the compressed data and a comma-separated content-type header value.
        """
        encodings = []
        for compressor in self.compressors:
            encodings.append(compressor.ENCODING)
            data = compressor(data)
        return data, ", ".join(encodings) if encodings else None


class DecompressorHandler(BaseCompressorHandler):
    """Handles the decompression of message data."""

    def __call__(self, data: bytes, *encodings: str) -> bytes:
        """
        Decompresses the provided data using the sequence of encodings.

        :param data: The data to be decompressed.
        :param encodings: A sequence of encodings to be used for decompression.
        :return: The decompressed data.
        """
        for encoding in encodings:
            compressor = self.get_compressor(encoding)
            data = compressor(data)
        return data


__all__ = ("CompressorHandler", "DecompressorHandler")
