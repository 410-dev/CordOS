import json
import os
import sys
import traceback
import time
import discord
import threading
import asyncio

import kernel.servers as Servers
import kernel.registry as Registry
import kernel.config as Config
import kernel.launchcmd as Launcher
import kernel.ipc as IPC
import kernel.journaling as Journaling
import kernel.services.DiscordUIService.asyncioevents as IOEventsMgr
import kernel.services.DiscordUIService.asynclauncher as AsyncLauncher

from objects.discordmessage import DiscordMessageWrapper

def main():
    try:
        Journaling.record("INFO", "DiscordUIService is starting up.")
        config = Config.load()

        Journaling.record("INFO", "Loading registry...")
        prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
        paths: list = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")
        botname = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotName")
        botver = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotVersion")

        print(f"Token: {config['token']}")
        print(f"Prefix: {prefix}")
        print(f"Paths: {paths}")
        print(f"Launching {botname} {botver}")
        Journaling.record("INFO", f"Token: {config['token']}")
        Journaling.record("INFO", f"Prefix: {prefix}")
        Journaling.record("INFO", f"Paths: {paths}")
        Journaling.record("INFO", f"Launching {botname} {botver}")

        # Instantiate a Discord client object
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        Journaling.record("INFO", "Client instantiated.")

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

        Journaling.record("INFO", "Initializing on_message event handler.")

        # Define a function to handle incoming messages
        @client.event
        async def on_message(message_original):
            Journaling.record("INFO", "Message received.")
            powerOffTrigger: bool = bool(IPC.read("power.off", default=False))
            if powerOffTrigger:
                Journaling.record("INFO", "Received shutdown signal.")
                return

            message = DiscordMessageWrapper(message_original)
            Journaling.record("INFO", f"Converted message to DiscordMessageWrapper.")
            try:

                if Registry.read("SOFTWARE.CordOS.Experimental.SystemEventHooker.InboundPassive", default="0") == "1":
                    Journaling.record("INFO", "Experimental InboundPassive events hooker is enabled.")
                    await IOEventsMgr.onPassiveInputEvent(message)

                elif Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessage") == "1":
                    formattedMsg = Registry.read("SOFTWARE.CordOS.Events.Inbound.PrintMessageFormat")
                    formattedMsg = formattedMsg.replace("$uname", str(message.author.name))
                    formattedMsg = formattedMsg.replace("$author", str(message.author))
                    formattedMsg = formattedMsg.replace("$uid", str(message.author.id))
                    formattedMsg = formattedMsg.replace("$serverid", str(message.guild.id))
                    formattedMsg = formattedMsg.replace("$servername", str(message.guild.name))
                    formattedMsg = formattedMsg.replace("$message", str(message.content))
                    print(formattedMsg)
                    Journaling.record("INFO", f"{formattedMsg}")

                else:
                    Journaling.record("INFO", "InboundPassive event is disabled. Running command execution.")

                # Check if the message was sent by the bot itself
                if message.author == client.user:
                    Journaling.record("INFO", "Message was sent by the bot itself. Ignoring.")
                    return

                # Check if the message starts with the bot's prefix
                prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
                if not message.content.startswith(prefix):
                    Journaling.record("INFO", "Message does not start with the bot's prefix. Ignoring.")
                    return

                # Update the user's server data
                Journaling.record("INFO", "Updating server data.")
                Servers.updateServer(message.getMessageObject())

                if Registry.read("SOFTWARE.CordOS.Experimental.SystemEventHooker.InboundInteractive", default="0") == "1":
                    Journaling.record("INFO", "Experimental InboundInteractive events hooker is enabled.")
                    await IOEventsMgr.onInteractiveInputEvent(message)

                else:
                    Journaling.record("INFO", "Running command execution. (This will be deprecated once the event hooker ends experimental phase.)")
                    print("EXECUTING COMMAND WITHIN DISCORDUISERVICE!!!!")
                    print("THIS METHOD WILL BE DEPRECATED IN FUTURE RELEASES.")
                    # Extract the command and arguments from the message content
                    try:
                        msgContent: str = message.content[len(prefix):]
                        args: list = Launcher.splitArguments(msgContent)
                        cmd: str = Launcher.getCommand(args)
                        runnablePath: str = Launcher.getRunnableModule(args, "discordui")
                        Journaling.record("INFO", f"Command '{cmd}' executed by {message.author.name}#{message.author.discriminator}.")
                    except Exception as e:
                        Journaling.record("ERROR", f"Failed looking up for command. The issue is highly likely from Launcher.getRunnableModule. e: {e}")
                        await message.reply(f"Failed looking up for command. This should not occur. {e}", mention_author=True)
                        return

                    if runnablePath == "" or runnablePath is None:
                        Journaling.record("WARNING", f"Command '{cmd}' not found.")
                        await message.reply(f"Command {cmd} not found.", mention_author=True)
                        return

                    try:
                        Journaling.record("INFO", f"Executing command - Passing to AsyncLauncher.runRunnableModule: '{cmd}'.")
                        await AsyncLauncher.runRunnableModule(runnablePath, args, message)
                    except Exception as e:
                        Journaling.record("ERROR", f"Error executing command '{cmd}': {e}")
                        if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1":
                            print(f"Error executing command '{cmd}': {e}")
                        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1":
                            traceback.print_exc()
                        await message.reply(f"Error executing command '{cmd}': {e}", mention_author=True)

            except Exception as e:
                # Set everything default mode. Try not loading registry.
                Journaling.record("ERROR", f"Significant error occurred and has to be handled manually: {e}")
                if message.content.startswith("."):
                    if message.content == ".regrestore":
                        Journaling.record("INFO", "Running registry restore - erasing registry.")
                        print("Running registry restore.")
                        print("Erasing registry.")
                        Registry.delete("", deleteSubkeys=True)
                        print("Registry erased.")
                        await message.reply("Registry erased.", mention_author=True)
                        Journaling.record("INFO", "Registry erased.")
                        Journaling.record("INFO", "Rebuilding registry....")
                        Registry.build('defaults/registry.cordreg', Config.get('registry'))
                        Journaling.record("INFO", "Registry rebuilt.")
                        print("Registry rebuilt.")
                        await message.reply("Registry rebuilt.", mention_author=True)
                        return

                    elif message.content == ".regfix":
                        print("Running registry fix.")
                        Journaling.record("INFO", "Running registry fix.")
                        Registry.build('defaults/registry.cordreg', Config.get('registry'))
                        print("Registry rebuilt.")
                        Journaling.record("INFO", "Registry rebuilt.")
                        await message.reply("Registry rebuilt.", mention_author=True)

                    elif message.content == ".rebootfix":
                        Journaling.record("INFO", "Terminating system and restarting kernel in safemode. Set `SOFTWARE.CordOS.Kernel.SafeMode` to 0 after reboot to return to normal mode.")
                        print("Terminating system and restarting kernel in safemode. Set `SOFTWARE.CordOS.Kernel.SafeMode` to 0 after reboot to return to normal mode.")
                        await message.reply("Terminating system and restarting kernel in safemode. Set `SOFTWARE.CordOS.Kernel.SafeMode` to 0 after reboot to return to normal mode.", mention_author=True)
                        try:
                            Journaling.record("INFO", "Updating registry / IPC.")
                            IPC.set("power.off", True)
                            IPC.set("power.off.state", "REBOOT-SAFE")
                            Registry.write("SOFTWARE.CordOS.Kernel.SafeMode", "1")
                            Journaling.record("INFO", "Registry / IPC updated.")
                        except:
                            Journaling.record("ERROR", "Failed to update registry / IPC. The system will try reboot to safe mode anyway.")
                            print("Failed to update registry / IPC. The system will try reboot to safe mode anyway.")
                            await message.reply("Failed to update registry. The system will try reboot to safe mode anyway.", mention_author=True)
                            sys.exit(3)

                        await client.close()
                        sys.exit(1)

                    else:
                        Journaling.record("ERROR", f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n{e}\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel in safemode. However, this is not recommended as it uses asynchronous subprocesses and may console instability.")
                        print(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n{e}\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel in safemode. However, this is not recommended as it uses asynchronous subprocesses and may console instability.")
                        await message.reply(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n```{e}```\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel in safemode. However, this is not recommended as it uses asynchronous subprocesses and may console instability.", mention_author=True)

        # Register the on_ready event handler
        Journaling.record("INFO", "Registering on_ready event handler.")
        client.event(on_ready)

        # Register the on_message event handler
        Journaling.record("INFO", "Registering on_message event handler.")
        client.event(on_message)

        # Shutdown signal
        Journaling.record("INFO", "Starting IPC event listener.")
        async def shutdownListener():
            while True:
                try:
                    Journaling.record("INFO", "Checking for shutdown signal.")
                    powerOffTrigger: bool = bool(IPC.read("power.off", default=False))
                    if powerOffTrigger:
                        Journaling.record("INFO", "Received shutdown signal. Recognizing the signal.")
                        signal: str = str(IPC.read("power.off.state", default="OFF"))
                        print(f"Received shutdown signal '{signal}'.")
                        Journaling.record("INFO", f"Received shutdown signal '{signal}'.")
                        try:
                            if signal == "OFF":
                                await client.close()
                                break
                            elif signal == "REBOOT":
                                await client.close()
                                break
                            await client.close()
                            break
                        except Exception as e:
                            Journaling.record("ERROR", f"Error in shutting down client: {e}")
                            print("Error in shutting down client: " + str(e))
                            break

                except Exception as e:
                    pass

                # Sleep
                time.sleep(1)

        # Start the shutdown listener
        def start_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(shutdownListener())
            loop.close()

        # Start the shutdown listener in an appropriate manner for async execution
        Journaling.record("INFO", "Starting IPC event listener.")
        print("Starting IPC event listener...")
        thread = threading.Thread(target=start_async_loop)
        thread.daemon = True
        thread.start()

        Journaling.record("INFO", "Starting client.")
        print("Starting client...")
        client.run(config['token'])

        terminationCode = IPC.read("power.off.state")
        Journaling.record("INFO", f"CoreSystem terminating with code '{terminationCode}'.")
        print(f"CoreSystem terminating with code '{terminationCode}'.")
        if terminationCode == "REBOOT":
            sys.exit(1)
        elif terminationCode == "REBOOT-SAFE":
            sys.exit(3)
        else:
            sys.exit(0)

    except discord.errors.LoginFailure as e:
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"DiscordUIService HAS CRASHED DUE TO DISCORD LOGIN FAILURE")
        print(f"---------------------------------------")
        print(f"Error Time: {time.ctime()}")
        print(f"Error: {e}")
        print(f"---------------------------------------")
        print(f"System will stop now immediately.")
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        Journaling.record("ERROR", f"DiscordUIService has crashed due to Discord login failure: {e}")
        sys.exit(0)

    except Exception as e:
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"DiscordUIService HAS CRASHED WITH UNHANDLED EXCEPTION")
        print(f"---------------------------------------")
        print(f"Error Time: {time.ctime()}")
        print(f"Error: {e}")
        print(f"---------------------------------------")
        print(f"Stack Trace:")
        traceback.print_exc()
        print(f"---------------------------------------")
        print(f"System will restart in safe mode after 3 seconds.")
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        Journaling.record("ERROR", f"DiscordUIService has crashed with unhandled exception: {e}")
        time.sleep(3)
        sys.exit(3)