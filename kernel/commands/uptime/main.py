import kernel.clock as Clock

class Uptime:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message

    async def exec(self):
        await self.message.reply(f"Uptime: {Clock.getUptime()}")