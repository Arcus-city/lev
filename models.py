from dataclasses import dataclass, field
from typing import Any


@dataclass
class Measurement:
    name: str
    value: Any
    unit: str | None = None
    quality: str = "good"


@dataclass
class SourceConfig:
    name: str
    protocol: str
    enabled: bool = True
    poll_interval: float = 1.0

    # generic/network fields
    host: str | None = None
    port: int | None = None
    url: str | None = None
    local_ip: str | None = None

    # Modbus
    device_id: int = 1
    points: list[dict] = field(default_factory=list)

    # OPC UA
    username: str | None = None
    password_env: str | None = None


@dataclass
class GatewayConfig:
    gateway: Any
    https: Any
    sources: list[SourceConfig]

    @classmethod
    def from_dict(cls, d):
        g = type("GatewaySettings", (), d.get("gateway", {}))()
        h = type("HttpsSettings", (), d.get("https", {}))()
        sources = [SourceConfig(**s) for s in d.get("sources", [])]
        return cls(gateway=g, https=h, sources=sources)
