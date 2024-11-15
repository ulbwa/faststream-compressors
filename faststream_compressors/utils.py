def serialize_accept_encoding_header(value: dict[str, float]) -> str:
    result: list[str] = []

    for encoding, quality in sorted(value.items(), key=lambda x: x[1], reverse=True):
        if quality > 1:
            quality = 1
        if quality < 0:
            quality = 0
        quality = round(quality, 3)
        if quality == 1:
            result.append(encoding)
        else:
            result.append(f"{encoding};q={quality}")

    return ", ".join(result)


def parse_accept_encoding_header(value: str) -> dict[str, float]:
    result: dict[str, float] = dict()

    for item in value.split(","):
        encoding, *quality_string = item.split(";q=", maxsplit=1)
        encoding = encoding.strip().casefold()
        if encoding in result:
            continue
        quality = float(quality_string[0]) if quality_string else 1.0
        if quality > 1:
            quality = 1
        if quality < 0:
            quality = 0
        result[encoding] = quality

    return result


__all__ = "serialize_accept_encoding_header", "parse_accept_encoding_header"
