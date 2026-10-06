import os
from asyncua import Client
from core.models import Measurement


class OpcUaAdapter:
    protocol = "opcua"

    def __init__(self, source):
        self.source = source
        self.client = None

    async def ensure_connected(self):
        if self.client is None:
            self.client = Client(url=self.source.url)

            if self.source.username:
                self.client.set_user(self.source.username)

            if self.source.password_env:
                password = os.getenv(self.source.password_env)
                if password:
                    self.client.set_password(password)

            await self.client.connect()

    async def poll(self):
        await self.ensure_connected()

        nodes = [
            self.client.get_node(p["node_id"])
            for p in self.source.points
        ]

        values = await self.client.read_values(nodes)

        return [
            Measurement(
                name=p["name"],
                value=value,
                unit=p.get("unit"),
            )
            for p, value in zip(self.source.points, values)
        ]

    async def close(self):
        if self.client is not None:
            try:
                await self.client.disconnect()
            finally:
                self.client = None
