import asyncio
import struct
from pymodbus.client import AsyncModbusTcpClient

from core.models import Measurement


class ModbusAdapter:
    protocol = "modbus"

    def __init__(self, source):
        self.source = source
        self.client = AsyncModbusTcpClient(
            source.host,
            port=source.port or 502,
            timeout=5,
            retries=3,
        )

    async def poll(self):
        if not self.client.connected:
            await self.client.connect()

        if not self.client.connected:
            raise ConnectionError(
                f"Modbus connection failed: {self.source.host}:{self.source.port}"
            )

        result = []
        for p in self.source.points:
            kind = p["type"]
            address = int(p["address"])
            count = int(p.get("count", 1))
            dtype = p.get("datatype", "uint16")

            if kind == "holding_registers":
                rr = await self.client.read_holding_registers(
                    address=address,
                    count=count,
                    device_id=self.source.device_id,
                )
                values = rr.registers
            elif kind == "input_registers":
                rr = await self.client.read_input_registers(
                    address=address,
                    count=count,
                    device_id=self.source.device_id,
                )
                values = rr.registers
            elif kind == "coils":
                rr = await self.client.read_coils(
                    address=address,
                    count=count,
                    device_id=self.source.device_id,
                )
                values = rr.bits[:count]
            elif kind == "discrete_inputs":
                rr = await self.client.read_discrete_inputs(
                    address=address,
                    count=count,
                    device_id=self.source.device_id,
                )
                values = rr.bits[:count]
            else:
                raise ValueError(f"Unsupported Modbus point type: {kind}")

            if rr.isError():
                raise RuntimeError(f"Modbus error for point {p['name']}: {rr}")

            value = self.decode(values, dtype, kind)
            result.append(
                Measurement(
                    name=p["name"],
                    value=value,
                    unit=p.get("unit"),
                )
            )

        return result

    @staticmethod
    def decode(values, dtype, kind):
        if dtype == "bool":
            return bool(values[0])

        if dtype == "uint16":
            return int(values[0])

        if dtype == "int16":
            return struct.unpack(">h", struct.pack(">H", values[0]))[0]

        if dtype in ("uint32", "int32", "float32"):
            if len(values) < 2:
                raise ValueError(f"{dtype} requires two registers")
            raw = struct.pack(">HH", values[0], values[1])
            if dtype == "uint32":
                return struct.unpack(">I", raw)[0]
            if dtype == "int32":
                return struct.unpack(">i", raw)[0]
            return struct.unpack(">f", raw)[0]

        raise ValueError(f"Unsupported Modbus datatype: {dtype}")

    async def close(self):
        self.client.close()
