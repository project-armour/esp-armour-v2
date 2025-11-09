"""
Module to handle display
"""
import asyncio

from machine import Pin, SoftI2C
from time import sleep_ms
from state import *
import ssd1306
import framebuf

class Display:
    """Display Handler class"""
    def __init__(self, i2c):
        """Initialize display"""
        self.display = ssd1306.SSD1306_I2C(128, 32, i2c)
        self.mode = "bitmap"
        self.bitmap = "logo"
        self.framebuffer = None
        self.lines = ["", "", ""]
        self.update()

    def update(self, *args):
        """Update screen"""
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
        """Used to set content of line"""
        self.lines[line] = content
        self.update()

    def set_mode(self, mode):
        """Switches between bitmap and text mode"""
        self.mode = mode
        self.update()

    def set_bitmap(self, bitmap):
        """Used to change bitmap image"""
        self.bitmap = bitmap
        self.update()
