import json
import os
import traceback

from objects.user import User
from objects.server import Server

import kernel.servers as Servers
import kernel.objects as Objects
import kernel.registry as Registry
import kernel.config as Config
import kernel.services as Services

import discord
import importlib

from typing import List

# Load configurations
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

def splitArgument(splitted_list: list) -> List[str]:
    string = " ".join(splitted_list)
    words = []
    in_quotes = False
    current_word = ""
    for char in string:
        if char == " " and not in_quotes:
            if current_word:
                words.append(current_word)
                current_word = ""
        elif char == '"':
            in_quotes = not in_quotes
        else:
            current_word += char
    if current_word:
        words.append(current_word)
    return words

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
        command = message.content[len(prefix):].split()[0]
        args = message.content.split()[1:]

        # Handle the command based on its name
        commandPaths: List[str] = json.loads(Registry.read("SOFTWARE.CordOS.Kernel.Programs.Paths"))['data']
        appropriateCommandPath: str = ""
        for commandPath in commandPaths:
            try:
                with open(os.path.join(commandPath, command, "main.py"), 'r') as f:
                    appropriateCommandPath = commandPath
                    break
            except:
                pass
        
        if appropriateCommandPath == "":
            await message.reply(f"Command {command} not found.", mention_author=True)
            return

        try:
            module_name = f"{appropriateCommandPath.replace('/', '.')}{command}.main"
            module = importlib.import_module(module_name)
            
            if Registry.read("SOFTWARE.CordOS.Kernel.ReloadOnCall") == "1":
                importlib.reload(module)

            CommandClass = getattr(module, command.capitalize())
            
            # Set arguments: Split by space, but if there's a quote, don't split
            args = splitArgument(args)

            # Instantiate the command and execute it
            command_instance = CommandClass(args, message)
            await command_instance.exec()
        except Exception as e:
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error executing command '{command}': {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
            await message.reply(f"Error executing command '{command}': {e}", mention_author=True)
    
    
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
                
            else:            
                print(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n{e}\nIt may be due to registry issue. To recover, type `regfix`. If it does not work, type `regrestore` to fully clean the registry.")
                await message.reply(f"!!!SYSTEM PANIC!!!!\nKernel cannot launch subprocess due to the following error:\n```{e}```\nIt may be due to registry issue. To recover, type `regfix`. If it does not work, type `regrestore` to fully clean the registry.", mention_author=True)
        

# Register the on_ready event handler
client.event(on_ready)

# Register the on_message event handler
client.event(on_message)

# Start the client
Services.start(3)
print("Starting client...")
client.run(config['token'])


