from typing import Any, Awaitable, Callable, Sequence

from faststream import BaseMiddleware, ContextRepo
from faststream.message import StreamMessage, encode_message
from faststream.response import PublishCommand, PublishType

from faststream_compressors import exceptions, interfaces, utils


class BaseCompressionMiddleware(BaseMiddleware):
    __slots__ = "compressors", "decompressors", "msg"

    def __init__(
        self,
        compressors: dict[str, list[interfaces.Compressor]],
        decompressors: dict[str, interfaces.Decompressor],
        msg: Any | None,
        context: ContextRepo,
    ) -> None:
        self.compressors = compressors
        self.decompressors = decompressors

        super().__init__(msg, context=context)

    @property
    def rpc_accept_encoding_header(self) -> str:
        value = dict()
        for decompressor in self.decompressors.values():
            value[decompressor.ENCODING] = decompressor.rpc_accept_quality

        value["identity"] = min(value.values(), default=1.0)
        return utils.serialize_accept_encoding_header(value)

    async def consume_scope(
        self, call_next: Callable[[Any], Awaitable[Any]], msg: StreamMessage[Any]
    ) -> Any:
        if "Content-Encoding" not in msg.headers:
            return await call_next(msg)

        if msg.headers["Content-Encoding"] == "identity":
            return await call_next(msg)

        applied_encodings: list[str] = list(
            map(str.strip, msg.headers["Content-Encoding"].split(","))
        )

        if "identity" in applied_encodings:
            raise exceptions.UnacceptableContentEncoding(msg.headers["Content-Encoding"])

        for applied_encoding in applied_encodings:
            decompressor = self.decompressors.get(applied_encoding.casefold())
            if decompressor is None:
                raise exceptions.UnknownEncoding(applied_encoding)
            msg.body = decompressor(msg.body, msg.headers)

        msg.clear_cache()
        return await call_next(msg)

    async def publish_scope(
        self,
        call_next: Callable[[PublishCommand], Awaitable[PublishCommand]],
        cmd: PublishCommand,
    ) -> Any:
        if "Content-Encoding" in cmd.headers:
            return await call_next(cmd)

        cmd.body, content_type = encode_message(cmd.body)
        if content_type is not None:
            cmd.add_headers({"content-type": content_type})

        applied_encodings: list[str] = list()

        if cmd.publish_type == PublishType.REPLY:
            if "Accept-Encoding" in cmd.headers:
                parsed_header = utils.parse_accept_encoding_header(
                    cmd.headers["Accept-Encoding"]
                )
                if "identity" not in parsed_header:
                    parsed_header["identity"] = parsed_header.get("*", 1.0)
                if (star_quality := parsed_header.pop("*", None)) is not None:
                    for encoding in self.decompressors.keys():
                        if encoding in parsed_header:
                            continue
                        parsed_header[encoding] = star_quality

                for encoding, quality in sorted(
                    parsed_header.items(), key=lambda x: x[1], reverse=True
                ):
                    if quality < parsed_header["identity"]:
                        break

                    if encoding not in self.decompressors:
                        continue

                    for compressor in sorted(
                        self.compressors[encoding],
                        key=lambda x: x.publish_quality,
                        reverse=True,
                    ):
                        if compressor.filter is not None:
                            if not compressor.filter(
                                cmd.body, cmd.headers, tuple(applied_encodings)
                            ):
                                continue

                        cmd.body, cmd.headers = compressor(cmd.body)
                        applied_encodings.append(compressor.ENCODING)
                        break

                if len(applied_encodings) and parsed_header.get("identity", 0.0) == 0:
                    raise exceptions.UnacceptableAcceptEncoding(
                        cmd.headers["Accept-Encoding"]
                    )

            else:
                # No Accept-Encoding header
                # Accept-Encoding: *;q=1.0
                for compressor in sorted(
                    (
                        compressor
                        for compressors in self.compressors.values()
                        for compressor in compressors
                    ),
                    key=lambda x: x.publish_quality,
                    reverse=True,
                ):
                    if compressor.ENCODING in applied_encodings:
                        continue

                    if compressor.filter is not None:
                        if not compressor.filter(
                            cmd.body, cmd.headers, tuple(applied_encodings)
                        ):
                            continue

                    cmd.body, cmd.headers = compressor(cmd.body)
                    applied_encodings.append(compressor.ENCODING)

        else:
            if cmd.publish_type == PublishType.REQUEST:
                cmd.headers.update({"Accept-Encoding": self.rpc_accept_encoding_header})

            for compressor in sorted(
                (
                    compressor
                    for compressors in self.compressors.values()
                    for compressor in compressors
                ),
                key=lambda x: x.publish_quality,
                reverse=True,
            ):
                if compressor.ENCODING in applied_encodings:
                    continue

                if compressor.filter is not None:
                    if not compressor.filter(
                        cmd.body, cmd.headers, tuple(applied_encodings)
                    ):
                        continue

                cmd.body, cmd.headers = compressor(cmd.body)
                applied_encodings.append(compressor.ENCODING)

        if len(applied_encodings) == 0:
            applied_encodings.append("identity")

        cmd.add_headers({"Content-Encoding": ",".join(applied_encodings)})

        return await call_next(cmd)


class CompressionMiddleware(BaseMiddleware):
    def __init__(
        self,
        compressors: Sequence[interfaces.Compressor] = (),
        decompressors: Sequence[interfaces.Decompressor] = (),
    ):
        self.compressors: dict[str, list[interfaces.Compressor]] = dict()
        self.decompressors: dict[str, interfaces.Decompressor] = dict()

        for compressor in compressors:
            self.add_compressor(compressor)

        for decompressor in decompressors:
            self.add_decompressor(decompressor)

    def add_compressor(self, compressor: interfaces.Compressor, /) -> None:
        if compressor.ENCODING.casefold() in map(str.casefold, ("*", "identity")):
            raise ValueError(f"Encoding {compressor.ENCODING} is reserved")

        if not (0 <= compressor.publish_quality <= 1):
            raise ValueError(f"{compressor.publish_quality=!r} must be between 0 and 1")

        if compressor.ENCODING.casefold() in self.compressors:
            if compressor.publish_quality in (
                x.publish_quality for x in self.compressors[compressor.ENCODING]
            ):
                raise ValueError(
                    f"Compressor with ENCODING={compressor.ENCODING!r} and "
                    f"publish_quality={compressor.publish_quality!r} already exists"
                )

            if compressor.filter is None:
                if any(x.filter is None for x in self.compressors[compressor.ENCODING]):
                    raise ValueError(
                        "Cannot add a compressor with fn=None when one already exists"
                    )
            else:
                compressor_wo_fn = next(
                    (
                        x
                        for x in self.compressors[compressor.ENCODING]
                        if x.filter is None
                    ),
                    None,
                )
                if (
                    compressor_wo_fn
                    and compressor.publish_quality < compressor_wo_fn.publish_quality
                ):
                    raise ValueError(
                        "Cannot add a compressor with fn!=None when there is a "
                        "compressor with fn=None and higher publish_quality"
                    )

            self.compressors[compressor.ENCODING.casefold()].append(compressor)

        else:
            self.compressors[compressor.ENCODING.casefold()] = [compressor]

    def add_decompressor(self, decompressor: interfaces.Decompressor, /) -> None:
        if decompressor.ENCODING.casefold() in map(str.casefold, ("*", "identity")):
            raise ValueError(f"Encoding {decompressor.ENCODING} is reserved")

        if not (0 <= decompressor.rpc_accept_quality <= 1):
            raise ValueError(
                f"{decompressor.rpc_accept_quality=!r} must be between 0 and 1"
            )

        if decompressor.ENCODING.casefold() in self.decompressors:
            raise ValueError(
                f"Decompressor with ENCODING={decompressor.ENCODING!r} already exists"
            )

        self.decompressors[decompressor.ENCODING.casefold()] = decompressor

    def __call__(
        self, msg: Any | None, /, *, context: ContextRepo
    ) -> BaseCompressionMiddleware:
        return BaseCompressionMiddleware(
            self.compressors, self.decompressors, msg=msg, context=context
        )


__all__ = ("CompressionMiddleware",)
