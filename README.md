# faststream-compressors

A middleware for the FastStream framework to support message compression.

## Example

```python
from faststream.nats import NatsBroker

from faststream_compressors.compressors import GzipCompressor, GzipDecompressor
from faststream_compressors.middlewares import CompressionMiddleware
from faststream_compressors.middlewares.nats import NatsDecompressionMiddleware


broker = NatsBroker(    
    middlewares=(
        # Compression methods used for compressing messages.
        # The order in which compressors are specified matters.
        CompressionMiddleware.make_middleware(compressors=GzipCompressor()),
        
        # Your other middlewares here

        # Compression methods used for decompressing messages.
        # The order does not matter here
        NatsDecompressionMiddleware.make_middleware(decompressors=GzipDecompressor()),
    )
)
```

| Broker | Is Supported? | Middleware                                                            |
|--------|---------------|-----------------------------------------------------------------------|
| NATS   | ✅             | `faststream_compressors.middlewares.nats.NatsDecompressionMiddleware` |
| Other  | ❌             |                                                                       |

You can submit a pull request to add support for decompression middleware for your broker. I expect that FastStream 
will update its middleware API soon, allowing us to create a universal middleware for each broker. For now, only 
NATS is supported.

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
from faststream_compressors.middlewares import CompressionMiddleware
from faststream_compressors.middlewares.nats import NatsDecompressionMiddleware


class MyCompressor(BaseCompressor):
    ENCODING = "xor1"

    def __call__(self, data: bytes) -> bytes:
        return bytes(byte ^ 1 for byte in data)


broker = NatsBroker(
    middlewares=(
        CompressionMiddleware.make_middleware(compressors=MyCompressor()),
        NatsDecompressionMiddleware.make_middleware(decompressors=MyCompressor()),
    )
)
app = FastStream(broker)


@broker.subscriber("my-subject")
async def my_handler(data: str, encoding: str = Header("content-encoding")):
    print(data, encoding)


@app.after_startup
async def ping():
    await broker.publish("My secret message", "my-subject")
```

## ⚠️ Note: RPC Limitation (<=0.5.18)

Due to a bug in FastStream <=0.5.18, middleware does not run after receiving a response from the broker, preventing message 
decompression when using RPC. 

Update faststream to 0.5.19 to use this middleware with rpc.