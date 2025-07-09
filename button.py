import asyncio

import machine
from machine import Pin, disable_irq, enable_irq
from time import ticks_ms, ticks_diff

from asyncio import ThreadSafeFlag, sleep_ms

from utils import CallbackSource


class Button(CallbackSource):
    events = ("single" , "long")
    def __init__(self, pin, debounce_interval=50, long_interval=2000, double_interval=300):
        super().__init__()
        self.pin = Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP)

        self.debounce_interval = debounce_interval
        self.long_interval = long_interval
        self.double_interval = double_interval

        self.last_rise = 0
        self.last_state = 0
        self.last_fall = 0
        self.last_press = 0

        self.flag = ThreadSafeFlag()

        self.pin.irq(self._irq)
        asyncio.create_task(self.loop())

    def _irq(self, pin):
        irq_status = disable_irq()
        current_ticks = ticks_ms()
        if pin.value() == 0 and self.last_state == 0:
            self.last_state = 1
            self.last_rise = current_ticks
        elif pin.value() == 1 and self.last_state == 1:
            self.last_fall = current_ticks
            self.last_state = 0
            self.flag.set()
        enable_irq(irq_status)


    async def loop(self):
        while True:
            await self.flag.wait()
            td = ticks_diff(self.last_fall, self.last_rise)
            if td >= self.long_interval:
                self.last_press = 0
                self.trigger('long')
                continue

            elif td >= self.debounce_interval:
                self.last_press = ticks_ms()
            self.flag.clear()
            self.trigger('single')
