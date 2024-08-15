from faststream_compressors.middlewares import BaseCompressionMiddleware
from nats.aio.msg import Msg


class NatsCompressionMiddleware(BaseCompressionMiddleware):
    msg: Msg | None

    @property
    def content_type(self) -> str | None:
        return self.msg.headers["content-type"]

    @property
    def content_encoding(self) -> list[str] | None:
        return list(map(str.strip, self.msg.headers["content-encoding"].split(",")))


__all__ = ("NatsCompressionMiddleware",)
