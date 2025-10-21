import asyncio

import machine
from machine import Pin, disable_irq, enable_irq
from time import ticks_ms, ticks_diff

from asyncio import ThreadSafeFlag, sleep_ms

from utils import CallbackSource


class Button(CallbackSource):
    events = ("single" , "long")
    eventdebug = True

    def __init__(self, pin, debounce_interval=50, long_interval=1500, name = ""):
        super().__init__()
        self.pin = Pin(pin, mode=Pin.IN, pull=None)

        self.debounce_interval = debounce_interval
        self.long_interval = long_interval

        self.last_rise = 0
        self.last_fall = 0
        self.name = name
        self.state = 0

        asyncio.create_task(self.loop())


    async def loop(self):
        while True:
            await asyncio.sleep_ms(50)
            pv = self.pin.value()
            if self.state == 0 and pv == 0:
                self.last_rise = ticks_ms()
                self.state = 1
            elif self.state == 1 and pv == 1:
                self.last_fall = ticks_ms()
                self.state = 0
                if ticks_diff(self.last_fall, self.last_rise) > self.long_interval:
                    self.trigger('long')
                else:
                    self.trigger('single')
