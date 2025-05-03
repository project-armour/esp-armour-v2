from display import *
from button import *
from pin_device import *
from heart_rate import *

fake_call = Button(2)
trigger = Button(15)
buzzer = OutputPin(5)
flash = OutputPin(19)
motor = OutputPin(21)
# heart_rate_sensor = HeartRate(4)

display = Display(16, 17)