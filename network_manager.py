import network
import asyncio
from utils import CallbackSource
from state import config, state

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

class NetworkManager(CallbackSource):
    events = ('connected', 'disconnect', 'connecting', 'failed')
    def __init__(self):
        super().__init__()
        self.network_config = config["networking"]
        self.networks = self.network_config["networks"]
        self.retry = self.network_config["retry_count"]
        self.connect_timeout = self.network_config["connect_timeout"]
        self.blacklist = []
        self.disconnected = True

    def reload_config(self):
        self.network_config = config["networking"]
        self.networks = self.network_config["networks"]
        self.retry = self.network_config["retry_count"]
        self.connect_timeout = self.network_config["connect_timeout"]

    async def connect(self, ssid, password):
        for _ in range(self.retry):
            sta_if.connect(ssid, password)
            for i in range(self.connect_timeout):
                stat = sta_if.status()
                self.trigger('connecting', ssid)
                if stat == network.STAT_GOT_IP:
                    self.trigger('connected', ssid)
                    return True
                elif stat != network.STAT_CONNECTING:
                    break
                await asyncio.sleep_ms(200)
            sta_if.disconnect()
        self.trigger('failed', ssid)
        self.blacklist.append(ssid)
        return False


    async def network_loop(self):
        ticks = 0
        while True:
            if sta_if.isconnected():
                await asyncio.sleep_ms(1000)
                continue
            elif not self.disconnected:
                self.trigger('disconnect')
                self.disconnected = True

            scan = sta_if.scan()
            ticks += 1
            if ticks >= 200:
                self.blacklist = []
                ticks = 0

            for ssid, _, _, _, _, _ in scan:
                ssid = ssid.decode()
                if ssid in self.networks and ssid not in self.blacklist:
                    if await self.connect(ssid, self.networks[ssid]['password']):
                        self.disconnected = False
                        break
            await asyncio.sleep_ms(500)
