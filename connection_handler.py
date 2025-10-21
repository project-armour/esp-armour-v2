import asyncio
import struct

import bluetooth
import aioble
from state import *
from utils import CallbackSource

SERVICE_UUID = bluetooth.UUID("0cc04a2c-b3c2-4431-a6f1-b9180ebce500")
ARMOUR_CONTROL_CHARACTERISTIC_UUID = bluetooth.UUID("0cc04a2c-b3c2-4431-a6f1-b9180ebce501")
HEART_RATE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A37)

_ADV_INTERVAL_US = 500_000

class BluetoothHandler(CallbackSource):

    events = ("ready", "connect", "disconnect")

    def __init__(self, name, command_handler):
        super().__init__()
        self.service = aioble.Service(SERVICE_UUID)

        self.armour_control = aioble.Characteristic(self.service, ARMOUR_CONTROL_CHARACTERISTIC_UUID,
                                                    write=True, notify=True, capture=True, indicate=True)
        self.heart_rate_char = aioble.Characteristic(self.service, HEART_RATE_CHARACTERISTIC_UUID,
                                                     read=True, notify=True)
        aioble.register_services(self.service)

        self.name = name

        self.connections = []
        self.command_handler = command_handler

        self.tasks = [
            asyncio.create_task(self.ble_advertise()),
            asyncio.create_task(self.handle_connection())
        ]

    async def ble_advertise(self):
        device_name = self.name
        while True:
            try:
                self.trigger("ready")
                async with await aioble.advertise(_ADV_INTERVAL_US, name=device_name,
                                                  services=[SERVICE_UUID]) as connection:
                    self.trigger("connect", connection.device)
                    self.connections.append(connection)
                    await connection.disconnected()
                    self.connections.remove(connection)
                    self.trigger("disconnect")
                    
            except Exception as e:
                print("Advertising error:", e)
            await asyncio.sleep_ms(500)

    async def handle_connection(self):
        while True:
            # Wait for a write operation on the LED characteristic.
            connection, data = await self.armour_control.written()
            cmd = data.decode().strip()
            resp = await self.command_handler.handle_command(cmd)
            self.armour_control.notify(connection, resp)

            # A small delay to yield control.
            await asyncio.sleep_ms(500)

    async def indicate(self, data):
        for connection in self.connections:
            await self.armour_control.indicate(connection, data)

    @staticmethod
    def _encode_int(i):
        return struct.pack("<h", i)

    async def update_heart_rate(self, heart_rate):
        await self.heart_rate_char.write(self._encode_int(heart_rate))

