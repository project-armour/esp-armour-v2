import asyncio

from hardware import *
from connection_handler import *
from command_handler import *
from state import *

cmd = CommandHandler()

bt = BluetoothHandler(config['name'], cmd)
state.set('status', "Off")

state.on('set', display.update)
display.set_line(0, 'Status: {status}')

def on_ready():
    state.set('status', "Ready")

def on_connect(device):
    state.set('status', "Connected")

bt.on("ready", on_ready)
bt.on("connect", on_connect)

async def single_press(bt):
    await bt.indicate("trg single")
trigger.on('single', single_press, bt)

async def main():
    tasks = bt.tasks
    await asyncio.gather(*tasks)

asyncio.run(main())
