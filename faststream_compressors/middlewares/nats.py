from nats.aio.msg import Msg

from faststream_compressors.middlewares import BaseDecompressionMiddleware


class NatsDecompressionMiddleware(BaseDecompressionMiddleware):
    msg: Msg

    @property
    def content_type(self) -> str | None:
        if not self.msg.headers:
            return
        return self.msg.headers.get("content-type")

    @property
    def content_encoding(self) -> list[str] | None:
        if not self.msg.headers:
            return
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
