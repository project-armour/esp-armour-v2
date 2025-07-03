import asyncio

from hardware import *
from connection_handler import *
from command_handler import *
from state import *
from network_manager import *

cmd = CommandHandler()
netman = NetworkManager()
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

async def button_press(bt, type):
    await bt.indicate(f"trg ${type}")

def heart_rate_get(bpm):
    if bpm is None:
        state.set('bpm', 'Undetected')
    else:
        state.set('bpm', bpm)

heart_rate_sensor.on("heart_rate", heart_rate_get)

trigger.on('single', button_press, bt, 'single')
trigger.on('double', button_press, bt, 'double')
trigger.on('long', button_press, bt, 'long')

async def main():
    tasks = bt.tasks
    tasks.append(asyncio.create_task(heart_rate_sensor.mainloop()))
    tasks.append(asyncio.create_task(netman.network_loop()))
    # tasks.append(asyncio.create_task(heart_rate_task()))
    print(tasks)
    await asyncio.gather(*tasks)

asyncio.run(main())
