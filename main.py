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
state.set('network', 'Disconnected')
state.on('set', display.update)
display.set_line(0, 'BT: {status}')
display.set_line(1, 'BPM: {bpm}')
display.set_line(2, 'Net: {network}')

def bluetooth_ready():
    state.set('status', "Ready")

def bluetooth_connect(device):
    state.set('status', "Connected")

bt.on("ready", bluetooth_ready)
bt.on("connect", bluetooth_connect)

async def button_press(bt, type):
    print("button", type)
    await bt.indicate(f"trg ${type}")

def heart_rate_get(bpm):
    if bpm is None:
        state.set('bpm', 'Undetected')
    else:
        state.set('bpm', bpm)

heart_rate_sensor.on("heart_rate", heart_rate_get)

trigger.on('single', button_press, bt, 'single')
trigger.on('long', button_press, bt, 'long')

def network_connected(ssid):
    state.set('network', ssid)

def network_connecting(ssid):
    state.set('network', 'Connecting')

def network_failed(ssid):
    state.set('network', "Failed")

def network_disconnected():
    state.set('network', 'Disconnected')
netman.on('connected', network_connected)
netman.on('connecting', network_connecting)
netman.on('disconnect', network_disconnected)
netman.on('failed', network_failed)

async def main():
    tasks = bt.tasks
    tasks.append(asyncio.create_task(heart_rate_sensor.mainloop()))
    tasks.append(asyncio.create_task(netman.network_loop()))
    # tasks.append(asyncio.create_task(heart_rate_task()))
    print(tasks)
    await asyncio.gather(*tasks)

asyncio.run(main())
