"""Main program"""

import asyncio
from random import *
from hardware import *
from connection_handler import *
from command_handler import *
from state import *

cmd = CommandHandler()
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
    """Callback for bluetooth ready status"""
    state.set('status', "Ready")
    display.set_bitmap("ready")
    state.set("bt_state", "ready")


def bluetooth_connect(device):
    """Callback for bluetooth connected status"""
    state.set('status', "Connected")
    display.set_bitmap("connected")
    state.set("bt_state", "connected")


def bluetooth_disconnect(device):
    """Callback for bluetooth disconnected status"""
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

async def panic():
    """Trigger panic"""
    display.set_bitmap('panic')
    buzzer.pulse(500, 10)
    await asyncio.sleep_ms(2000)
    display.set_bitmap(state.query("bt_state"))


async def fake_call_cb():
    """Trigger fake call"""
    display.set_bitmap('fakecall')
    await asyncio.sleep_ms(2000)
    display.set_bitmap(state.query("bt_state"))


async def flashbang():
    """Flash LED"""
    flash.value(1 - flash.value())


trigger.on('single', button_press, bt, 'short1')
trigger.on('single', flashbang)

trigger.on('long', button_press, bt, 'long1')
trigger.on('long', panic)

fake_call.on('single', button_press, bt, 'short2')
fake_call.on('single', fake_call_cb)

fake_call.on('long', button_press, bt, 'long2')


async def main():
    """Main loop"""
    tasks = bt.tasks
    tasks.append(asyncio.create_task(heart_rate_sensor.mainloop()))
    # tasks.append(asyncio.create_task(heart_rate_task()))
    print(tasks)
    await asyncio.gather(*tasks)


asyncio.run(main())
