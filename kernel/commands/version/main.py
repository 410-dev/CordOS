import kernel.registry as Registry
import kernel.ipc as IPC

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
            isSafe = "" if not IPC.read("kernel.safemode") else " (Safe Mode)"
            await self.message.reply(f"Version Profiling:\n\nBaseSystem: {foundation} {version} {isSafe}\nBot: {botName} {botVer}", mention_author=True)
        except Exception as e:
            await self.message.reply(f"Error loading profile: {e}", mention_author=True)
