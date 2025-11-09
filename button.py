"""
Module for button
"""
import asyncio

import machine
from machine import Pin, disable_irq, enable_irq
from time import ticks_ms, ticks_diff

from asyncio import ThreadSafeFlag, sleep_ms

from utils import CallbackSource


class Button(CallbackSource):
    """
    Handles button events
    """
    events = ("single" , "long")
    eventdebug = True

    def __init__(self, pin, debounce_interval=50, long_interval=1500, extra_long_interval=5000, name = "", pull_up=None):
        """Initializes button handler"""
        super().__init__()
        self.pin = Pin(pin, mode=Pin.IN, pull=pull_up)

        self.debounce_interval = debounce_interval
        self.long_interval = long_interval
        self.extra_long_interval = extra_long_interval
        self.last_rise = 0
        self.last_fall = 0
        self.name = name
        self.state = 0

        asyncio.create_task(self.loop())


    async def loop(self):
        "Loop to handle button events"
        while True:
            await asyncio.sleep_ms(50)
            pv = self.pin.value()
            if self.state == 0 and pv == 0:
                self.last_rise = ticks_ms()
                self.state = 1
            elif self.state == 1 and pv == 1:
                self.last_fall = ticks_ms()
                self.state = 0
                if self.extra_long_interval > ticks_diff(self.last_fall, self.last_rise) > self.long_interval:
                    self.trigger('long')
                    self.last_fall = 0
                    self.last_rise = 0
                else:
                    self.trigger('single')
                    self.last_fall = 0
                    self.last_rise = 0
