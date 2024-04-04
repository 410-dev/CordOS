import json
import os
import traceback
import time
import discord
import importlib
import threading
import asyncio

import kernel.servers as Servers
import kernel.objects as Objects
import kernel.registry as Registry
import kernel.config as Config
import kernel.servicectl as Services
import kernel.launchcmd as Launcher
import kernel.clock as Clock
import kernel.ipc as IPC
import kernel.host as HostMachine


# Load configurations
Services.start(0)
Clock.init()
IPC.init()
Services.start(1)
config = Config.load()


# Load registry
prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
paths: list = json.loads(Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths"))['data']
foundation = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Foundation")
version = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")
botname = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotName")
botver = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotVersion")

print(f"Starting up {foundation} {version}")
print(f"Token: {config['token']}")
print(f"Prefix: {prefix}")
print(f"Paths: {paths}")
print(f"Launching {botname} {botver}")

# Instantiate a Discord client object
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

Services.start(2)

# Define a function to send a message to all servers that the bot is connected to
async def broadcast_message(message):
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(message)

# Define an event handler for when the bot is ready to start receiving events
async def on_ready():
    print(f"Logged in as {client.user}")
    # await broadcast_message("I'm online and ready to go!")

def getConfig(key):
    keys = key.split('.')
    dictionary = config.copy()
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return None

    return dictionary

# Define a function to handle incoming messages
@client.event
async def on_message(message):
    try:
        if Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessage") == "1":
            formattedMsg = Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessageFormat")
            formattedMsg = formattedMsg.replace("$uname", str(message.author.name))
            formattedMsg = formattedMsg.replace("$author", str(message.author))
            formattedMsg = formattedMsg.replace("$uid", str(message.author.id))
            formattedMsg = formattedMsg.replace("$serverid", str(message.guild.id))
            formattedMsg = formattedMsg.replace("$servername", str(message.guild.name))
            formattedMsg = formattedMsg.replace("$message", str(message.content))
            print(formattedMsg)

        # Check if the message was sent by the bot itself
        if message.author == client.user:
            return

        # Check if the message starts with the bot's prefix
        prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
        if not message.content.startswith(prefix):
            return

        # Update the user's server data
        Servers.updateServer(message)

        # Extract the command and arguments from the message content
        try:
            msgContent: str = message.content[len(prefix):]
            args: list = Launcher.splitArguments(msgContent)
            cmd: str = Launcher.getCommand(args)
            runnablePath: str = Launcher.getRunnableModule(args)
        except Exception as e:
            await message.reply(f"Failed looking up for command. This should not occur. {e}", mention_author=True)
            return

        if runnablePath == "":
            await message.reply(f"Command {cmd} not found.", mention_author=True)
            return

        try:
            await Launcher.runRunnableModule(runnablePath, args, message)
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error executing command '{cmd}': {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await message.reply(f"Error executing command '{cmd}': {e}", mention_author=True)

    except Exception as e:

        # Set everything default mode. Try not loading registry.
        if message.content.startswith("."):
            if message.content == ".regrestore":
                print("Running registry restore.")
                print("Erasing registry.")
                Registry.delete("", deleteSubkeys=True)
                print("Registry erased.")
                await message.reply("Registry erased.", mention_author=True)
                Registry.build('defaults/registry.cordblueprint', 'data/registry')
                print("Registry rebuilt.")
                await message.reply("Registry rebuilt.", mention_author=True)
                return

            elif message.content == ".regfix":
                print("Running registry fix.")
                Registry.build('defaults/registry.cordblueprint', 'data/registry')
                print("Registry rebuilt.")
                await message.reply("Registry rebuilt.", mention_author=True)

            elif message.content == ".rebootfix":
                print("Terminating system and restarting kernel.")
                await message.reply("Terminating system and restarting kernel.", mention_author=True)
                isPosix: bool = HostMachine.getHostOSType() == "posix"
                if isPosix:
                    # sleep for 3 seconds, then run boot.sh file asynchronously
                    shScript: str = os.path.join(os.getcwd(), "boot.sh")
                    # chmod +x boot.sh
                    exitcode = HostMachine.executeCommand(f"chmod +x {shScript}")
                    if exitcode != 0:
                        print(f"POSIX: Failed to make {shScript} executable.")
                        await message.reply(f"Failed to queue reboot. (POSIX, Exit code {exitcode}@stg1)", mention_author=True)
                    else:
                        exitcode = HostMachine.executeCommand(f"sleep 3 && {shScript} &")
                        if exitcode != 0:
                            print(f"POSIX: Failed to run {shScript}.")
                            await message.reply(f"Failed to queue reboot. (POSIX, Exit code {exitcode}@stg2)", mention_author=True)
                        else:
                            await message.reply("Reboot queued.", mention_author=True)
                            await client.close()
                            exit(0)

                else:
                    # sleep for 3 seconds, then run boot.bat file asynchronously
                    batScript: str = os.path.join(os.getcwd(), "boot.bat")
                    exitcode = HostMachine.executeCommand(f"timeout 3 && start {batScript}")
                    if exitcode != 0:
                        print(f"NON-POSIX: Failed to run {batScript}.")
                        await message.reply(f"Failed to queue reboot. (NON-POSIX, Exit code {exitcode})", mention_author=True)
                    else:
                        await message.reply("Reboot queued.", mention_author=True)
                        await client.close()
                        exit(0)

            else:
                print(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n{e}\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel. However, this is not recommended as it uses asynchronous subprocesses and may console instability.")
                await message.reply(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n```{e}```\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel. However, this is not recommended as it uses asynchronous subprocesses and may console instability.", mention_author=True)


# Register the on_ready event handler
client.event(on_ready)

# Register the on_message event handler
client.event(on_message)

# Shutdown signal
async def shutdownListener():
    while True:
        try:
            value: str = IPC.read(Registry.read("SOFTWARE.CordOS.Kernel.Services.CoreServices.IPC.LabelKernelState"))
            if value == Registry.read("SOFTWARE.CordOS.Kernel.Signals.Shutdown") or value == Registry.read("SOFTWARE.CordOS.Kernel.Signals.Restart"):
                print(f"Received shutdown signal '{value}'.")
                try:
                    await client.close()
                    break
                except:
                    print("Error in shutting down client.")
                    exit(1)
        except:
            pass

        # Sleep
        time.sleep(1)

# Start the client
Services.start(3)

# Start the shutdown listener
def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(shutdownListener())
    loop.close()

# Start the shutdown listener in an appropriate manner for async execution
print("Starting IPC event listener...")
thread = threading.Thread(target=start_async_loop)
thread.daemon = True
thread.start()

print("Starting client...")
client.run(config['token'])

