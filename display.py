import asyncio

from machine import Pin, SoftI2C
from time import sleep_ms
from state import *
import ssd1306
import framebuf

class Display:
    def __init__(self, i2c):
        self.display = ssd1306.SSD1306_I2C(128, 32, i2c)
        self.mode = "bitmap"
        self.bitmap = "logo"
        self.framebuffer = None
        self.lines = ["", "", ""]
        self.update()

    def update(self, *args):
        if self.mode == "text":
            self.display.fill(0)
            for i, line in enumerate(self.lines):
                self.display.text(line.format(**state.state), 0, i * 10 + 1)
            self.display.show()
        elif self.mode == "bitmap":
            with open(f"bitmaps/{self.bitmap}.bin", 'rb') as bitmap_file:
                bitmap = bytearray(bitmap_file.read())
                self.framebuffer = framebuf.FrameBuffer(bitmap, 128, 32, framebuf.MONO_HLSB)
            self.display.blit(self.framebuffer, 0, 0)
            self.display.show()

    def set_line(self, line, content):
        self.lines[line] = content
        self.update()

    def set_mode(self, mode):
        self.mode = mode
        self.update()

    def set_bitmap(self, bitmap):
        self.bitmap = bitmap
        self.update()
