from display import *
from button import *
from pin_device import *
from heart_rate import *

fake_call = Button(22)
trigger = Button(15)
buzzer = OutputPin(5)
flash = OutputPin(19)
motor = OutputPin(21)
i2c = SoftI2C(sda = Pin(16), scl = Pin(17))
heart_rate_sensor = HeartRate(pin=4)

display = Display(i2c)