# faststream-compressors

A middleware for the FastStream framework to support message compression.

## Example

```python
from faststream.nats import NatsBroker

from faststream_compressors.compressors import GzipCompressor, GzipDecompressor
from faststream_compressors.compressors.lz4 import Lz4Decompressor  # pip install "faststream_compressors[lz4]"
from faststream_compressors.middlewares.nats import NatsCompressionMiddleware

compression_middleware = NatsCompressionMiddleware.make_middleware(
    # Compression methods used for decompressing messages.
    # The order does not matter here.
    decompressors=(GzipDecompressor(), Lz4Decompressor()),
    # Compression methods used for compressing messages.
    # The order in which compressors are specified matters.
    compressors=GzipCompressor(),
)

broker = NatsBroker(middlewares=(compression_middleware,))
```

| Broker | Is Supported? | Middleware                                               |
|--------|---------------|----------------------------------------------------------|
| NATS   | ✅             | `faststream_compressors.middlewares.nats.NatsMiddleware` |
| Other  | ❌             |                                                          |

You can submit a pull request to add support for middleware for your broker. I expect that FastStream will update its
middleware API soon, allowing us to create a universal middleware for each broker. For now, only NATS is supported.

| Compression Method | Is Supported? | Compressor                                                                                                          | Extra Dependency              |
|--------------------|---------------|---------------------------------------------------------------------------------------------------------------------|-------------------------------| 
| gzip               | ✅             | `faststream_compressors.compressors.GzipCompressor`<br/>`faststream_compressors.compressors.GzipDecompressor`       |                               |
| lz4                | ✅             | `faststream_compressors.compressors.lz4.Lz4Compressor`<br/>`faststream_compressors.compressors.lz4.Lz4Decompressor` | `faststream-compressors[lz4]` |
| Other              | ❌             |                                                                                                                     |                               |

You can submit a pull request to add support for your compression method or use your custom algorithm that adheres to
the BaseCompressor interface.

```python
from faststream import FastStream, Header
from faststream.nats import NatsBroker

from faststream_compressors.compressors import BaseCompressor

from faststream_compressors.middlewares.nats import NatsCompressionMiddleware


class MyCompressor(BaseCompressor):
    ENCODING = "xor1"

    def __call__(self, data: bytes) -> bytes:
        return bytes(byte ^ 1 for byte in data)


compression_middleware = NatsCompressionMiddleware.make_middleware(
    decompressors=MyCompressor(), compressors=MyCompressor()
)

broker = NatsBroker(middlewares=(compression_middleware,))
app = FastStream(broker)


@broker.subscriber("my-subject")
async def my_handler(data: str, encoding: str = Header("content-encoding")):
    print(data, encoding)


@app.after_startup
async def ping():
    await broker.publish("My secret message", "my-subject")
```
