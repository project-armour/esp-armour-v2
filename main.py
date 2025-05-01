import asyncio

from hardware import *
from connection_handler import *
from command_handler import *
from state import *

cmd = CommandHandler()
async def flash(cmd):
    buzzer.pulse(1000, 3)

async def buzzer_on(cmd):
    buzzer.on()

async def buzzer_off(cmd):
    buzzer.off()


cmd.register_command("bf", flash)
cmd.register_command("b0", buzzer_off)
cmd.register_command("b1", buzzer_on)

bt = BluetoothHandler(config['name'], cmd)
state.set('status', "Off")

state.on('set', display.update())
display.set_line(0, 'Status: {status}')

def on_ready():
    state.set('status', "Ready")

def on_connect(device):
    state.set('status', "Connected")

bt.on("ready", on_ready)
bt.on("connect", on_connect)

async def main():
    tasks = bt.tasks
    await asyncio.gather(*tasks)

asyncio.run(main())
