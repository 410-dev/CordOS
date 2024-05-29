import sys
import traceback
import time
import discord
import threading
import asyncio

import kernel.servers as Servers
import kernel.registry as Registry
import kernel.config as Config
import kernel.ipc as IPC
import kernel.journaling as Journaling
import kernel.io as IO
import kernel.services.DiscordUIService.asyncioevents as IOEventsMgr
import kernel.services.power.configure as Power
import kernel.webhook as Webhook

from kernel.objects.discordmessage import DiscordMessageWrapper

def main():
    try:
        Journaling.record("INFO", "DiscordUIService is starting up.")
        config = Config.load()

        Journaling.record("INFO", "Loading registry...")
        prefix = Registry.read("SOFTWARE.CordOS.Config.Core.Prefix")
        paths: list = Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths").replace(", ", ",").split(",")
        botname = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotName")
        botver = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.BotVersion")

        if 'token' not in config:
            IO.println("ERROR: Unable to start DiscordUIService. Token not found in config file.")
            Journaling.record("ERROR", "Token not found in config file.")
            Power.halt()

        IO.println(f"Token: {config['token']}")
        IO.println(f"Prefix: {prefix}")
        IO.println(f"Paths: {paths}")
        IO.println(f"Launching {botname} {botver}")
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
        # async def broadcast_message(message):
        #     for guild in client.guilds:
        #         for channel in guild.text_channels:
        #             if channel.permissions_for(guild.me).send_messages:
        #                 await channel.send(message)

        # Define an event handler for when the bot is ready to start receiving events
        async def on_ready():
            IO.println(f"Logged in as {client.user}")
            try:
                enabled = Registry.read("SOFTWARE.CordOS.Kernel.Services.DiscordUIService.OnReadyMessage", default="0")
                if enabled == "1":
                    webhooks = Registry.read("SOFTWARE.CordOS.Kernel.Services.DiscordUIService.OnReadyWebhooks", default="").replace(", ", ",").split(",")
                    for webhook in webhooks:
                        try:
                            IO.println(f"Sending on_ready webhook to {webhook}")
                            Webhook.send(webhook, f"DiscordUIService for {client.user} is now online.")
                        except Exception as ex:
                            IO.println("Failed to send on_ready webhook: " + str(ex))

            except Exception as ex:
                IO.println("Failed to prepare on_ready webhook: " + str(ex))
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
                    IO.println(formattedMsg)
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

                # Update the user's server etc
                Journaling.record("INFO", "Updating server etc.")
                Servers.updateServer(message.getMessageObject())

                Journaling.record("INFO", "InboundInteractive events hooker is enabled.")
                await IOEventsMgr.onInteractiveInputEvent(message)

            except Exception as e:
                # Set everything default mode. Try not loading registry.
                Journaling.record("ERROR", f"Significant error occurred and has to be handled manually: {e}")
                if message.content.startswith("."):
                    if message.content == ".regrestore":
                        Journaling.record("INFO", "Running registry restore - erasing registry.")
                        IO.println("Running registry restore.")
                        IO.println("Erasing registry.")
                        Registry.delete("", deleteSubkeys=True)
                        IO.println("Registry erased.")
                        await message.reply("Registry erased.", mention_author=True)
                        Journaling.record("INFO", "Registry erased.")
                        Journaling.record("INFO", "Rebuilding registry....")
                        Registry.build('defaults/registry.cordreg', Config.get('registry'))
                        Journaling.record("INFO", "Registry rebuilt.")
                        IO.println("Registry rebuilt.")
                        await message.reply("Registry rebuilt.", mention_author=True)
                        return

                    elif message.content == ".regfix":
                        IO.println("Running registry fix.")
                        Journaling.record("INFO", "Running registry fix.")
                        Registry.build('defaults/registry.cordreg', Config.get('registry'))
                        IO.println("Registry rebuilt.")
                        Journaling.record("INFO", "Registry rebuilt.")
                        await message.reply("Registry rebuilt.", mention_author=True)

                    elif message.content == ".rebootfix":
                        Journaling.record("INFO", "Terminating system and restarting kernel in safemode. Set `SOFTWARE.CordOS.Kernel.SafeMode` to 0 after reboot to return to normal mode.")
                        IO.println("Terminating system and restarting kernel in safemode. Set `SOFTWARE.CordOS.Kernel.SafeMode` to 0 after reboot to return to normal mode.")
                        await message.reply("Terminating system and restarting kernel in safemode. Set `SOFTWARE.CordOS.Kernel.SafeMode` to 0 after reboot to return to normal mode.", mention_author=True)
                        try:
                            Journaling.record("INFO", "Updating registry / IPC.")
                            Power.reboot_safe()
                            Registry.write("SOFTWARE.CordOS.Kernel.SafeMode", "1")
                            Journaling.record("INFO", "Registry / IPC updated.")
                        except:
                            Journaling.record("ERROR", "Failed to update registry / IPC. The system will try reboot to safe mode anyway.")
                            IO.println("Failed to update registry / IPC. The system will try reboot to safe mode anyway.")
                            await message.reply("Failed to update registry. The system will try reboot to safe mode anyway.", mention_author=True)
                            sys.exit(3)

                        await client.close()
                        sys.exit(1)

                    else:
                        Journaling.record("ERROR", f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n{e}\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel in safemode. However, this is not recommended as it uses asynchronous subprocesses and may console instability.")
                        IO.println(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n{e}\nIt may be due to registry issue. To recover, type `regfix` to reset default registries. If it does not work, type `regrestore` to fully clean the registry. If it still does not work, type `rebootfix` to restart the kernel in safemode. However, this is not recommended as it uses asynchronous subprocesses and may console instability.")
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
                    # Journaling.record("INFO", "Checking for shutdown signal.")
                    powerOffTrigger: bool = bool(IPC.read("power.off", default=False))
                    if powerOffTrigger:
                        Journaling.record("INFO", "Received shutdown signal. Recognizing the signal.")
                        signal: str = str(IPC.read("power.off.state", default="OFF"))
                        IO.println(f"Received shutdown signal '{signal}'.")
                        Journaling.record("INFO", f"Received shutdown signal '{signal}'.")
                        try:
                            if signal == "OFF":
                                await client.close()
                                break
                            elif signal.startswith("REBOOT"):
                                await client.close()
                                break
                            await client.close()
                            break
                        except Exception as e:
                            Journaling.record("ERROR", f"Error in shutting down client: {e}")
                            IO.println("Error in shutting down client: " + str(e))
                            break

                except Exception as e:
                    pass

                # Sleep
                time.sleep(1)

        # Push client to IPC
        Journaling.record("INFO", "Pushing client to IPC.")
        IPC.set("discord.client", client)

        # Start the shutdown listener
        def start_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(shutdownListener())
            loop.close()

        # Start the shutdown listener in an appropriate manner for async execution
        Journaling.record("INFO", "Starting IPC event listener.")
        IO.println("Starting IPC event listener...")
        thread = threading.Thread(target=start_async_loop)
        thread.daemon = True
        thread.start()

        Journaling.record("INFO", "Starting client.")
        IO.println("Starting client...")
        client.run(config['token'])

        terminationCode = IPC.read("power.off.state")
        Journaling.record("INFO", f"CoreSystem terminating with code '{terminationCode}'.")
        IO.println(f"CoreSystem terminating with code '{terminationCode}'.")
        if terminationCode == "REBOOT":
            sys.exit(1)
        elif terminationCode == "REBOOT-SAFE":
            sys.exit(3)
        else:
            sys.exit(0)

    except discord.errors.LoginFailure as e:
        IO.println(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        IO.println(f"DiscordUIService HAS CRASHED DUE TO DISCORD LOGIN FAILURE")
        IO.println(f"---------------------------------------")
        IO.println(f"Error Time: {time.ctime()}")
        IO.println(f"Error: {e}")
        IO.println(f"---------------------------------------")
        IO.println(f"System will stop now immediately.")
        IO.println(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        Journaling.record("ERROR", f"DiscordUIService has crashed due to Discord login failure: {e}")
        Power.reset_safe()

    except Exception as e:
        IO.println(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        IO.println(f"DiscordUIService HAS CRASHED WITH UNHANDLED EXCEPTION")
        IO.println(f"---------------------------------------")
        IO.println(f"Error Time: {time.ctime()}")
        IO.println(f"Error: {e}")
        IO.println(f"---------------------------------------")
        IO.println(f"Stack Trace:")
        traceback.print_exc()
        IO.println(f"---------------------------------------")
        IO.println(f"System will restart in safe mode after 3 seconds.")
        IO.println(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        Journaling.record("ERROR", f"DiscordUIService has crashed with unhandled exception: {e}")
        time.sleep(3)
        Power.reset_safe()