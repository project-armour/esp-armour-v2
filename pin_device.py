"""Module for output devices"""
import asyncio

from machine import Pin, PWM


class OutputPin(Pin):
    """Output pin devices"""
    def __init__(self, id):
        """Initialize pin"""
        super().__init__(id, mode=Pin.OUT)
        self.task = None
        self.off()

    def off(self):
        """Switch off pin"""
        super().off()
        self.cancel_task()

    def on(self):
        """Switch on pin"""
        super().on()
        self.cancel_task()

    def value(self, x=None):
        """Set pin value"""
        if x is None:
            return super().value()
        super().value(x)
        self.cancel_task()

    def cancel_task(self):
        """Cancel pin pulse task"""
        if self.task is not None:
            self.task.cancel()

    async def pulse_task(self, delay, repeat):
        """Task to pulse pin"""
        for i in range(repeat):
            super().on()
            await asyncio.sleep_ms(delay)
            super().off()
            await asyncio.sleep_ms(delay)

    def pulse(self, delay, repeat):
        """Sets task to pulse pin"""
        self.task = asyncio.create_task(self.pulse_task(delay, repeat))

class PWMPin:
    """PWM output pin for buzzer"""
    def __init__(self, id):
        """Initializes pin and PWM"""
        self.pin = Pin(id)
        self.pwm = PWM(self.pin, freq=1300, duty_u16=0)
        self.task = None
        self.off()

    def off(self):
        """Switch off pin"""
        self.pwm.deinit()
        self.cancel_task()

    def on(self):
        """Switch on pin"""
        self.pwm.init(freq=1300, duty_u16=32768)
        self.cancel_task()

    def cancel_task(self):
        """Cancel pulse task"""
        if self.task is not None:
            self.task.cancel()

    async def pwm_time(self, time, cycles):
        """Task to pulse buzzer"""
        for i in range(cycles//2):
            self.pwm.init(freq=1838, duty_u16=32768)
            await asyncio.sleep_ms(time)
            self.pwm.init(freq=2600, duty_u16=32768)
            await asyncio.sleep_ms(time)
        self.pwm.deinit()

    def pulse(self, time, cycles):
        """Creates task to pulse buzzer"""
        self.task = asyncio.create_task(self.pwm_time(time, cycles))