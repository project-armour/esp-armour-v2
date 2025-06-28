import network
import asyncio
from state import Config, State

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

class NetworkManager:
    def __init__(self):
        self.network_config = Config["networking"]
        self.networks = self.network_config["networks"]
        self.retry = self.network_config["retry_count"]
        self.connect_timeout = self.network_config["connect_timeout"]
    async def connect(self, ssid, password):
        for _ in range(self.retry):
            sta_if.connect(ssid, password)
            for i in range(10):
                stat = sta_if.status()
                if stat == network.STAT_GOT_IP:
                    return True
                elif stat != network.STAT_CONNECTING:
                    break
                await asyncio.sleep_ms(200)
            sta_if.disconnect()

        return False


    async def network_loop(self):
        while True:
            if sta_if.isconnected():
                asyncio.sleep_ms(1000)
                continue
            scan = sta_if.scan()

            for ssid, _, _, _, _, _ in scan:
                if ssid in self.networks:
                    if await self.connect(ssid, self.networks[ssid]['password']):
                        break
            await asyncio.sleep_ms(500)
