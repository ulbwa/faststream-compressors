from abc import abstractmethod
from functools import partial
from typing import Any, Callable, Sequence

from faststream import BaseMiddleware
from faststream.log.logging import logger
from faststream.broker.message import encode_message
from faststream.types import AsyncFunc

from faststream_compressors.compressors import BaseCompressor
from faststream_compressors.errors import UnknownEncoding
from faststream_compressors.handler import CompressorHandler, DecompressorHandler


class BaseCompressionMiddleware(BaseMiddleware):
    """
    A base class for creating middleware to handle message compression and decompression.

    This middleware is used to compress data before sending messages and decompress data upon receiving messages.
    """

    def __init__(
        self,
        msg: Any,
        *,
        decompressors: Sequence[BaseCompressor],
        compressors: Sequence[BaseCompressor] | None = None,
    ):
        self.decompressor_handler = DecompressorHandler(*decompressors)
        self.compressor_handler = CompressorHandler(*compressors)

        super().__init__(msg)

    @classmethod
    def make_middleware(
        cls,
        decompressors: Sequence[BaseCompressor] | BaseCompressor,
        compressors: Sequence[BaseCompressor] | BaseCompressor | None = None,
    ) -> Callable[[Any], "BaseCompressionMiddleware"]:
        """
        Creates a partial function that can be used to instantiate the middleware.

        :param decompressors: A sequence of decompressors or a single decompressor to use for message decompression.
        :param compressors: A sequence of compressors or a single compressor to use for message compression.
        :return: A partial function to instantiate the middleware.
        """
        if isinstance(decompressors, BaseCompressor):
            decompressors = (decompressors,)
        if isinstance(compressors, BaseCompressor):
            compressors = (compressors,)
        return partial(
            cls,
            compressors=compressors,
            decompressors=decompressors,
        )

    @property
    @abstractmethod
    def content_type(self) -> str | None:
        """
        Abstract property to get the content type of the message.

        :return: The content type of the message.
        """

    @property
    @abstractmethod
    def content_encoding(self) -> list[str] | None:
        """
        Abstract property to get the content encoding of the message.

        :return: A list of encodings applied to the message.
        """

    async def on_receive(self) -> None:
        if not self.content_encoding:
            return

        try:
            self.msg.data = self.decompressor_handler(
                self.msg.data, *reversed(self.content_encoding)
            )
        except UnknownEncoding as exception:
            logger.warning(f"{self.__class__.__name__}: {exception}")
        except Exception as exception:
            logger.error("Failed to decompress message:", exc_info=exception)

    async def publish_scope(
        self,
        call_next: "AsyncFunc",
        msg: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if not self.compressor_handler.compressors:
            return await call_next(msg, *args, **kwargs)

        if not kwargs["headers"]:
            kwargs["headers"] = dict()

        if "content-encoding" in kwargs["headers"]:
            return await call_next(msg, *args, **kwargs)

        try:
            if "content-type" not in kwargs["headers"]:
                msg, kwargs["headers"]["content-type"] = encode_message(msg)
            msg, kwargs["headers"]["content-encoding"] = self.compressor_handler(msg)
        except Exception as exception:
            logger.error("Failed to compress message:", exc_info=exception)

        return await call_next(msg, *args, **kwargs)


__all__ = ("BaseCompressionMiddleware",)
