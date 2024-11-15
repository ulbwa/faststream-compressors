from abc import ABC

from faststream_compressors import interfaces


class BaseCompressor(interfaces.Compressor, ABC):
    __slots__ = "__publish_quality", "__filter"

    def __init__(
        self,
        publish_quality: float = 1.0,
        filter: interfaces.CompressFilter | None = None,
    ):
        self.__publish_quality = publish_quality
        self.__filter = filter

    @property
    def publish_quality(self) -> float:  # type: ignore
        return self.__publish_quality

    @property
    def filter(self) -> interfaces.CompressFilter | None:  # type: ignore
        return self.__filter


class BaseDecompressor(interfaces.Decompressor, ABC):
    def __init__(self, rpc_accept_quality: float = 1.0):
        self.__rpc_accept_quality = rpc_accept_quality

    @property
    def rpc_accept_quality(self) -> float:  # type: ignore
        return self.__rpc_accept_quality


__all__ = "BaseCompressor", "BaseDecompressor"
