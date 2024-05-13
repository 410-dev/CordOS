class Vc:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message
    
    async def mainAsync(self):
        """
        Directs the parameters to the correct function.
        """
        await self.message.reply("This plugin is currently unsupported.", mention_author=True)
        pass

    