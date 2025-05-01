import asyncio

from machine import Pin, SoftI2C
from time import sleep_ms
from state import *
import ssd1306

class Display:
    def __init__(self, sda, scl):
        i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        self.display = ssd1306.SSD1306_I2C(128, 32, i2c)
        self.lines = ["", "", ""]
        self.update()

    def update(self, *args):
        self.display.fill(0)
        for i, line in enumerate(self.lines):
            self.display.text(line.format(**state.state), 0, i * 10 + 1)
        self.display.show()

    def set_line(self, line, content):
        self.lines[line] = content
        self.update()

