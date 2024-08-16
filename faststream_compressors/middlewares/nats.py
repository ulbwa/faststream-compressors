from faststream_compressors.middlewares import BaseDecompressionMiddleware
from nats.aio.msg import Msg


class NatsDecompressionMiddleware(BaseDecompressionMiddleware):
    msg: Msg | None

    @property
    def content_type(self) -> str | None:
        return self.msg.headers.get("content-type")

    @property
    def content_encoding(self) -> list[str] | None:
        if "content-encoding" not in self.msg.headers:
            return
        return list(map(str.strip, self.msg.headers["content-encoding"].split(",")))

    @property
    def body(self) -> bytes:
        return self.msg.data

    @body.setter
    def body(self, value: bytes):
        self.msg.data = value


__all__ = ("NatsDecompressionMiddleware",)
