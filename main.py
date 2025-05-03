import asyncio

from hardware import *
from connection_handler import *
from command_handler import *
from state import *

cmd = CommandHandler()

bt = BluetoothHandler(config['name'], cmd)
state.set('status', "Off")
state.set('bpm', 0)
state.on('set', display.update)
display.set_line(0, 'Status: {status}')
display.set_line(1, 'BPM: {bpm}')

def on_ready():
    state.set('status', "Ready")

def on_connect(device):
    state.set('status', "Connected")

bt.on("ready", on_ready)
bt.on("connect", on_connect)

async def single_press(bt):
    await bt.indicate("trg single")

async def heart_rate_task():
    while True:
        bpm = heart_rate_sensor.get_bpm()
        if bpm is None:
            state.set('bpm', 'Undetected')
        else:
            state.set('bpm', bpm)
        sleep_ms(500)

trigger.on('single', single_press, bt)

async def main():
    tasks = []
    # tasks = bt.tasks
    tasks.append(heart_rate_task())
    await asyncio.gather(*tasks)

asyncio.run(main())
