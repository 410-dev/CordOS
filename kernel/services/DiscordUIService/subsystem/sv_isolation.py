from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper

import kernel.partitionmgr as PartitionMgr
import kernel.journaling as Journaling

import json
import os
import traceback

def getIsolationAvailable(message: DiscordMessageWrapper) -> bool:

    if not PartitionMgr.Data.isDir(f"CordOS/sessions/{message.guild.id}"):
        Journaling.record("INFO", f"Isolation not setup for guild {message.guild.id}.")
        return False

    Journaling.record("INFO", f"Isolation setup for guild {message.guild.id}.")
    declaration = json.loads(PartitionMgr.Data.read(f"CordOS/sessions/{message.guild.id}/isolation.json"))
    return declaration["isolation"]


def mkIsolation(message: DiscordMessageWrapper):
    try:
        # Setup isolation environment
        PartitionMgr.Data.mkdir(f"CordOS/sessions/{message.guild.id}")
        isolationDeclare = {
            "isolation": True,
            "guild": message.guild.id,
            "name": message.guild.name,
            "permissions": {
                "local.commands.modify": {
                    "enabled": True,
                    "key": ""
                },
                "local.commands.execute": {
                    "enabled": True,
                    "key": ""
                },
                "local.services.modify": {
                    "enabled": False,
                    "key": ""
                },
                "local.services.load": {
                    "enabled": False,
                    "key": ""
                },
                "local.events.modify": {
                    "enabled": False,
                    "key": ""
                },
                "local.events.load": {
                    "enabled": False,
                    "key": ""
                },
                "global.commands.modify": {
                    "enabled": False,
                    "key": ""
                },
                "global.commands.execute": {
                    "enabled": False,
                    "key": ""
                },
                "global.services.modify": {
                    "enabled": False,
                    "key": ""
                },
                "global.services.load": {
                    "enabled": False,
                    "key": ""
                },
                "global.events.modify": {
                    "enabled": False,
                    "key": ""
                }
            }
        }
        Journaling.record("INFO", f"Isolation container created for guild {message.guild.id}.")
        PartitionMgr.Data.write(f"CordOS/sessions/{message.guild.id}/isolation.json",
                                json.dumps(isolationDeclare, indent=4))
        Journaling.record("INFO", f"Isolation declaration created for guild {message.guild.id}.")

        # Copy files
        filesToCopy = [
            "commands"
        ]
        for file in filesToCopy:
            Journaling.record("INFO", f"Copying {file} to isolation container for guild {message.guild.id}.")
            PartitionMgr.RootFS.copy(file, PartitionMgr.Data.path(f"CordOS/sessions/{message.guild.id}"))
            Journaling.record("INFO", f"Copy of {file} to isolation container for guild {message.guild.id} complete.")

        # File patches
        Journaling.record("INFO", f"Patching files in isolation container for guild {message.guild.id}.")
        patchPattern = [
            ("import kernel.registry as", "import kernel.services.DiscordUIService.subsystem.registry as"),
            ("import kernel.ipc as", "import kernel.services.DiscordUIService.subsystem.ipc as"),
            ("import kernel.partitionmgr as", "import kernel.services.DiscordUIService.subsystem.partitionmgr as"),
            ("import commands.packtool", f"import {PartitionMgr.Data.path('CordOS/sessions').replace('\\', '/').replace('//', '/').replace('/', '.')}.commands.packtool"),
        ]
        patchNeglectPattern = "#@GLOBAL"

        def recursiveFileBuild(path: str, l: list) -> list:
            for element in os.listdir(path):
                full_path = os.path.join(path, element)
                if not full_path.endswith(".py"):
                    continue

                if os.path.isdir(full_path):
                    l += recursiveFileBuild(full_path, [])
                else:
                    l.append(full_path)
            return l

        filesToPatch = recursiveFileBuild(PartitionMgr.Data.path(f"CordOS/sessions/{message.guild.id}"), [])
        for file in filesToPatch:
            with open(file, "r") as f:
                content = f.read()
            for line in content.split("\n"):
                if patchNeglectPattern in line:
                    continue
                if "import" not in line:
                    continue
                for pattern in patchPattern:
                    content = content.replace(pattern[0], pattern[1])
            with open(file, "w") as f:
                f.write(content)
            Journaling.record("INFO", f"Patched: {file}")
        Journaling.record("INFO", f"File patching complete for guild {message.guild.id}.")

        dirsToCreate = [
            "storage",
            "etc/registry"
        ]

        for d in dirsToCreate:
            Journaling.record("INFO", f"Creating directory {d} in isolation container for guild {message.guild.id}.")
            PartitionMgr.Data.mkdir(f"CordOS/sessions/{message.guild.id}/{d}")
            Journaling.record("INFO", f"Directory {d} created in isolation container for guild {message.guild.id}.")

        Journaling.record("INFO", f"Isolation setup complete for guild {message.guild.id}.")
        return True
    except Exception as e:
        Journaling.record("ERROR", f"Error setting up isolation for guild {message.guild.id}. e: {e}")
        return False


def getIsolationPermission(message: DiscordMessageWrapper, key: str) -> str:
    try:
        declaration = json.loads(PartitionMgr.Data.read(f"CordOS/sessions/{message.guild.id}/isolation.json"))
        return declaration["permissions"][key]["key"]
    except Exception as e:
        Journaling.record("ERROR", f"Error getting isolation config key for guild {message.guild.id}. e: {e}")
        return ""


def getCallerContainerPath(mustContain: str = "CordOS/sessions/") -> str:
    mustContain = mustContain.replace("\\", "/").replace("//", "/")
    for frame in traceback.extract_stack():
        filename = frame.filename
        filename = filename.replace("\\", "/").replace("//", "/")
        if mustContain in filename:
            try:
                session_id = filename.split(mustContain)[1].split("/")[0]
                if mustContain.endswith("/"):
                    return f"{mustContain}{session_id}"
                return f"{mustContain}/{session_id}"
            except IndexError:
                pass  # Handle cases where the path doesn't have the expected structure
    return None  # Indicate that the session ID wasn't found
