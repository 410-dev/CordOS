import kernel.clock as Clock
import kernel.io as IO

class Uptime:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message

    async def mainAsync(self):
        await self.message.reply(f"Uptime: {Clock.getUptime()}")


def main(args: list):
    IO.println(f"Uptime: {Clock.getUptime()}")
