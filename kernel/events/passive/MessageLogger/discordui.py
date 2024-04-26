import kernel.registry as Registry

async def mainAsync(message):
    if Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessage") == "1":
        formattedMsg = Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessageFormat")
        formattedMsg = formattedMsg.replace("$uname", str(message.author.name))
        formattedMsg = formattedMsg.replace("$author", str(message.author))
        formattedMsg = formattedMsg.replace("$uid", str(message.author.id))
        formattedMsg = formattedMsg.replace("$serverid", str(message.guild.id))
        formattedMsg = formattedMsg.replace("$servername", str(message.guild.name))
        formattedMsg = formattedMsg.replace("$message", str(message.content))
        print(formattedMsg)
