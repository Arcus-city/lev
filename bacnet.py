import BAC0
from core.models import Measurement


class BacnetAdapter:
    protocol = "bacnet"

    def __init__(self, source):
        self.source = source
        self.bacnet = None

    async def ensure_connected(self):
        if self.bacnet is None:
            kwargs = {}
            if self.source.local_ip:
                kwargs["ip"] = self.source.local_ip
            if self.source.port:
                kwargs["port"] = self.source.port
            self.bacnet = BAC0.start(**kwargs)

            # Give BAC0 time to finish startup when using direct assignment.
            await self.bacnet._initialized

    async def poll(self):
        await self.ensure_connected()
        result = []

        for p in self.source.points:
            address = p["address"]
            object_type = p["object_type"]
            instance = p["instance"]
            prop = p.get("property", "presentValue")

            request = f"{address} {object_type} {instance} {prop}"
            value = await self.bacnet.read(request)

            result.append(
                Measurement(
                    name=p["name"],
                    value=value,
                    unit=p.get("unit"),
                )
            )

        return result

    async def close(self):
        if self.bacnet is not None:
            await self.bacnet._disconnect()
            self.bacnet = None
