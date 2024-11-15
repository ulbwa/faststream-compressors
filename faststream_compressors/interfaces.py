from abc import abstractmethod
from typing import Any, Protocol


class Decompressor(Protocol):
    ENCODING: str

    rpc_accept_quality: float

    @abstractmethod
    def __call__(
        self,
        data: bytes,
        /,
        headers: dict[str, Any],
    ) -> bytes: ...


class CompressFilter(Protocol):
    @abstractmethod
    def __call__(
        self,
        data: bytes,
        /,
        headers: dict[str, Any],
        applied_encodings: tuple[str, ...],
    ) -> bool: ...


class Compressor(Protocol):
    ENCODING: str

    publish_quality: float
    filter: CompressFilter | None

    @abstractmethod
    def __call__(self, data: bytes) -> tuple[bytes, dict[str, Any]]: ...


__all__ = "Decompressor", "CompressFilter", "Compressor"
