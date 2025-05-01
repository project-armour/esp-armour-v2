import asyncio

from machine import Pin


class OutputPin(Pin):
    def __init__(self, id):
        super().__init__(id, mode=Pin.OUT)
        self.task = None

    def off(self):
        super().off()
        self.cancel_task()

    def on(self):
        super().on()
        self.cancel_task()

    def value(self, x=None):
        if x is None:
            return super().value()
        super().value(x)
        self.cancel_task()

    def cancel_task(self):
        if self.task is not None:
            self.task.cancel()

    async def pulse_task(self, delay, repeat):
        for i in range(repeat):
            super().on()
            await asyncio.sleep_ms(delay)
            super().off()
            await asyncio.sleep_ms(delay)

    def pulse(self, delay, repeat):
        self.task = asyncio.create_task(self.pulse_task(delay, repeat))