import kernel.registry as Registry

class Version:
    
    def __init__(self, lineArgs, message) -> None:
        self.args: list = lineArgs
        self.message = message

    async def exec(self):
        
        try: 
            foundation = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Foundation")
            version = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")
            botName = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotName")
            botVer = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotVersion")
            await self.message.reply(f"Version Profiling:\nBaseSystem: {foundation} {version}\nBot: {botName} {botVer}", mention_author=True)
        except Exception as e:
            await self.message.reply(f"Error opening config.json e: {e}", mention_author=True)