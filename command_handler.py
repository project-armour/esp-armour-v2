"""Module for bluetooth command handler"""


class CommandHandler:
    """Handles commands sent through bluetooth"""

    def __init__(self):
        self.commands = {}
        self.register_command("hb", self.heartbeat)

    async def handle_command(self, cmd):
        """Handles recieved commands"""
        command = cmd.split()
        try:
            resp = await self.commands[command[0]](cmd)
            if resp is None:
                return "ok"
            else:
                return resp
        except KeyError:
            return "nocmd"
        except:
            return "err"

    def register_command(self, cmd, handler):
        """Registers a new command"""
        self.commands[cmd] = handler

    async def heartbeat(self, cmd):
        """Sends heartbeat in response"""
        return "alive"

    # async def alert(self, cmd):
