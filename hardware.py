from display import *
from button import *
from pin_device import *
from heart_rate import *
import ssd1306
import framebuf

fake_call = Button(1, pull_up=Pin.PULL_UP)
trigger = Button(18, pull_up=Pin.PULL_UP)
buzzer = OutputPin(3)
flash = OutputPin(19)
motor = OutputPin(4)

i2c_display = SoftI2C(sda=Pin(15), scl=Pin(14))
i2c_heart_rate = SoftI2C(sda=Pin(5), scl=Pin(20))
display = Display(i2c=i2c_display)
heart_rate_sensor = HeartRate(i2c=i2c_heart_rate)