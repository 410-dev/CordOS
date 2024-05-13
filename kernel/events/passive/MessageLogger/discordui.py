import kernel.registry as Registry
import kernel.journaling as Journaling
import kernel.io as IO

async def mainAsync(message):
    if Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessage") == "1":
        formattedMsg = Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessageFormat")
        Journaling.record("INFO", f"Message received from {message.author.name}#{message.author.discriminator} in {message.guild.name}, format of log: {formattedMsg}")
        formattedMsg = formattedMsg.replace("$uname", str(message.author.name))
        formattedMsg = formattedMsg.replace("$author", str(message.author))
        formattedMsg = formattedMsg.replace("$uid", str(message.author.id))
        formattedMsg = formattedMsg.replace("$serverid", str(message.guild.id))
        formattedMsg = formattedMsg.replace("$servername", str(message.guild.name))
        formattedMsg = formattedMsg.replace("$message", str(message.content))
        Journaling.record("INFO", f"Formatted message: {formattedMsg}")
        IO.println(formattedMsg)
