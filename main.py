import asyncio
from random import *
from hardware import *
from connection_handler import *
from command_handler import *
from state import *
from network_manager import *

cmd = CommandHandler()
netman = NetworkManager()
bt = BluetoothHandler(config['name'], cmd)

state.set('status', "Off")
state.set('bt_state', "logo")
state.set('bpm', 0)
state.set('button', "")
state.set('network', 'Disconnected')
state.on('set', display.update)
display.set_line(0, 'BT: {status}')
display.set_line(1, 'Button: {button}')
display.set_line(2, 'Net: {network}')

def bluetooth_ready():
    state.set('status', "Ready")
    display.set_bitmap("ready")
    state.set("bt_state", "ready")

def bluetooth_connect(device):
    state.set('status', "Connected")
    display.set_bitmap("connected")
    state.set("bt_state", "connected")


def bluetooth_disconnect(device):
    state.set('status', "Disconnected")
    display.set_bitmap("ready")
    state.set("bt_state", "ready")


bt.on("ready", bluetooth_ready)
bt.on("connect", bluetooth_connect)
bt.on("disconnect", bluetooth_disconnect)

async def button_press(bt, type):
    print("button", type)
    state.set('button', type)
    await bt.indicate(f"trg {type}")

def heart_rate_get(bpm):
    if bpm is None:
        state.set('bpm', 'Undetected')
    else:
        state.set('bpm', bpm)

heart_rate_sensor.on("heart_rate", heart_rate_get)

async def panic():
    display.set_bitmap('panic')
    buzzer.on()
    await sleep_ms(2000)
    display.set_bitmap(state.query("bt_state"))

async def fake_call_cb():
    display.set_bitmap('fake_call')
    await sleep_ms(2000)
    display.set_bitmap(state.query("bt_state"))

async def flashbang():
    flash.value(1 - flash.value())


trigger.on('single', button_press, bt, 'short1')
trigger.on('single', flashbang)

trigger.on('long', button_press, bt, 'long1')
trigger.on('long', panic)

fake_call.on('single', button_press, bt, 'short2')
fake_call.on('single', fake_call_cb)
fake_call.on('long', button_press, bt, 'long2')

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
