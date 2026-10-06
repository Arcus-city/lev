from urllib.parse import urlparse


def detect_protocol(source):
    if source.url:
        scheme = urlparse(source.url).scheme.lower()
        if scheme == "opc.tcp":
            return "opcua"

    port = source.port
    if port == 502:
        return "modbus"
    if port == 47808:
        return "bacnet"

    raise ValueError(
        f"Cannot auto-detect protocol for source={source.name}. "
        "Specify protocol explicitly."
    )
