from typing import Any

import pytest

from faststream_compressors import BaseCompressor, CompressionMiddleware, GzipCompressor
from faststream_compressors.compressors.base import BaseDecompressor
from faststream_compressors.compressors.gzip import GzipDecompressor
from faststream_compressors.compressors.lzma import LzmaCompressor, LzmaDecompressor


async def test_add_compressor():
    middleware = CompressionMiddleware()
    assert middleware.compressors == {}
    middleware.add_compressor(GzipCompressor())
    assert len(middleware.compressors) == 1
    assert "gzip" in middleware.compressors
    assert len(middleware.compressors["gzip"]) == 1
    assert isinstance(middleware.compressors["gzip"][0], GzipCompressor)


async def test_add_multiple_compressors_with_same_encoding():
    middleware = CompressionMiddleware()
    middleware.add_compressor(
        GzipCompressor(
            publish_quality=0.9,
            filter=lambda x, y, z: False,  # type: ignore
        )
    )
    middleware.add_compressor(GzipCompressor(publish_quality=1))
    assert len(middleware.compressors) == 1
    assert "gzip" in middleware.compressors
    assert len(middleware.compressors["gzip"]) == 2


async def test_add_multiple_compressors_with_same_encoding_without_filter():
    middleware = CompressionMiddleware()
    middleware.add_compressor(GzipCompressor(publish_quality=0.9))
    with pytest.raises(ValueError):
        middleware.add_compressor(GzipCompressor(publish_quality=1))


async def test_add_multiple_compressors_with_same_quality():
    middleware = CompressionMiddleware()
    middleware.add_compressor(GzipCompressor(publish_quality=1))
    middleware.add_compressor(LzmaCompressor(publish_quality=1))
    assert len(middleware.compressors) == 2
    assert "gzip" in middleware.compressors
    assert len(middleware.compressors["gzip"]) == 1
    assert "lzma" in middleware.compressors
    assert len(middleware.compressors["lzma"]) == 1


async def test_add_multiple_compressors_with_same_encoding_with_same_quality():
    middleware = CompressionMiddleware()
    middleware.add_compressor(
        GzipCompressor(
            publish_quality=1,
            filter=lambda x, y, z: False,  # type: ignore
        )
    )
    with pytest.raises(ValueError):
        middleware.add_compressor(GzipCompressor(publish_quality=1))


async def test_add_multiple_compressors_filter_pq_lt_without_filter():
    middleware = CompressionMiddleware()
    middleware.add_compressor(GzipCompressor(publish_quality=1))
    with pytest.raises(ValueError):
        middleware.add_compressor(
            GzipCompressor(
                publish_quality=0.9,
                filter=lambda x, y, z: False,  # type: ignore
            )
        )


async def test_add_compressor_negative_publish_quality():
    middleware = CompressionMiddleware()
    with pytest.raises(ValueError):
        middleware.add_compressor(GzipCompressor(publish_quality=-0.1))


async def test_add_compressor_publish_quality_gt_1():
    middleware = CompressionMiddleware()
    with pytest.raises(ValueError):
        middleware.add_compressor(GzipCompressor(publish_quality=1.1))


async def test_add_compressor_with_reserved_encoding():
    middleware = CompressionMiddleware()

    class IdentityCompressor(BaseCompressor):
        ENCODING = "identity"

        def __call__(self, data: bytes) -> tuple[bytes, dict[str, Any]]: ...

    with pytest.raises(ValueError):
        middleware.add_compressor(IdentityCompressor())

    class StarCompressor(BaseCompressor):
        ENCODING = "*"

        def __call__(self, data: bytes) -> tuple[bytes, dict[str, Any]]: ...

    with pytest.raises(ValueError):
        middleware.add_compressor(StarCompressor())


async def test_init_middleware_with_compressor():
    middleware = CompressionMiddleware(compressors=[GzipCompressor()])
    assert len(middleware.compressors) == 1
    assert "gzip" in middleware.compressors
    assert len(middleware.compressors["gzip"]) == 1


async def test_init_middleware_with_multiple_compressors():
    middleware = CompressionMiddleware(compressors=[GzipCompressor(), LzmaCompressor()])
    assert len(middleware.compressors) == 2
    assert "gzip" in middleware.compressors
    assert "lzma" in middleware.compressors
    assert len(middleware.compressors["gzip"]) == 1


async def test_init_middleware_with_multiple_compressors_with_same_encoding():
    middleware = CompressionMiddleware(
        compressors=[
            GzipCompressor(
                compress_level=1,
                filter=lambda x, y, z: False,  # type: ignore
                publish_quality=0.9,
            ),
            GzipCompressor(),
        ]
    )
    assert len(middleware.compressors) == 1
    assert "gzip" in middleware.compressors
    assert len(middleware.compressors["gzip"]) == 2


#


async def test_add_decompressor():
    middleware = CompressionMiddleware()
    assert middleware.decompressors == {}
    middleware.add_decompressor(GzipDecompressor())
    assert len(middleware.decompressors) == 1
    assert "gzip" in middleware.decompressors
    assert isinstance(middleware.decompressors["gzip"], GzipDecompressor)


async def test_add_multiple_decompressors_with_same_encoding():
    middleware = CompressionMiddleware()
    middleware.add_decompressor(GzipDecompressor(rpc_accept_quality=1))

    with pytest.raises(ValueError):
        middleware.add_decompressor(GzipDecompressor(rpc_accept_quality=0.9))


async def test_add_multiple_decompressors_same_quality():
    middleware = CompressionMiddleware()
    middleware.add_decompressor(GzipDecompressor(rpc_accept_quality=1))
    middleware.add_decompressor(LzmaDecompressor(rpc_accept_quality=1))
    assert len(middleware.decompressors) == 2


async def test_add_decompressor_negative_rpc_quality():
    middleware = CompressionMiddleware()
    with pytest.raises(ValueError):
        middleware.add_decompressor(GzipDecompressor(rpc_accept_quality=-0.1))


async def test_add_decompressor_publish_quality_gt_1():
    middleware = CompressionMiddleware()
    with pytest.raises(ValueError):
        middleware.add_decompressor(GzipDecompressor(rpc_accept_quality=1.1))


async def test_add_decompressor_with_reserved_encoding():
    middleware = CompressionMiddleware()

    class IdentityDecompressor(BaseDecompressor):
        ENCODING = "identity"

        def __call__(self, data: bytes, /, headers: dict[str, Any]) -> bytes: ...

    with pytest.raises(ValueError):
        middleware.add_decompressor(IdentityDecompressor())

    class StarDecompressor(BaseDecompressor):
        ENCODING = "*"

        def __call__(self, data: bytes, /, headers: dict[str, Any]) -> bytes: ...

    with pytest.raises(ValueError):
        middleware.add_decompressor(StarDecompressor())


async def test_init_middleware_with_decompressor():
    middleware = CompressionMiddleware(decompressors=[GzipDecompressor()])
    assert len(middleware.decompressors) == 1
    assert "gzip" in middleware.decompressors
    assert isinstance(middleware.decompressors["gzip"], GzipDecompressor)


async def test_init_middleware_with_multiple_decompressors():
    middleware = CompressionMiddleware(
        decompressors=[GzipDecompressor(), LzmaDecompressor()]
    )
    assert len(middleware.decompressors) == 2
    assert "gzip" in middleware.decompressors
    assert "lzma" in middleware.decompressors
    assert isinstance(middleware.decompressors["gzip"], GzipDecompressor)
    assert isinstance(middleware.decompressors["lzma"], LzmaDecompressor)


async def test_init_middleware_with_multiple_decompressors_with_same_encoding():
    with pytest.raises(ValueError):
        CompressionMiddleware(
            decompressors=[
                GzipDecompressor(),
                GzipDecompressor(),
            ]
        )
