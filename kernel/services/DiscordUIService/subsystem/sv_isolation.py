from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper
from kernel.services.DiscordUIService.objects.server import Server as ServerO
from kernel.services.DiscordUIService.objects.user import User

import kernel.services.DiscordUIService.subsystem.server as Server

import kernel.partitionmgr as PartitionMgr
import kernel.journaling as Journaling
import kernel.io as IO
import kernel.registry as Registry

import json
import os
import traceback


def getRoot(subDir: str = "")-> str:
    return PartitionMgr.Data.path(f"CordOS/sessions/s{subDir}")


def getIsolationAvailable(message: DiscordMessageWrapper) -> bool:
    if not PartitionMgr.RootFS.isDir(getRoot(message.guild.id)):
        Journaling.record("INFO", f"Isolation not setup for guild {message.guild.id}.")
        if mkIsolation(message):
            Journaling.record("INFO", f"Isolation setup completed for guild {message.guild.id}.")
            return True

    Journaling.record("INFO", f"Isolation setup for guild {message.guild.id}.")
    declaration = json.loads(PartitionMgr.RootFS.read(f"{getRoot(message.guild.id)}/isolation.json"))
    return declaration["isolation"]


def mkIsolation_sync(message: DiscordMessageWrapper, fileMap: list) -> bool:
    try:
        for file in fileMap:
            Journaling.record("INFO", f"Copying {file} to isolation container for guild {message.guild.id}.")
            PartitionMgr.RootFS.mkdir(f"{getRoot(message.guild.id)}/{file[1]}")
            PartitionMgr.RootFS.copy(file[0], f"{getRoot(message.guild.id)}/{file[1]}")
            Journaling.record("INFO", f"Copy of {file} to isolation container for guild {message.guild.id} complete.")
    except Exception as e:
        Journaling.record("ERROR", f"Error setting up isolation for guild {message.guild.id}. e: {e}")
        return False
    return True


def mkIsolation_patchImports(message: DiscordMessageWrapper, patchPath: str, patchPattern: list = None, patchNeglectPattern: str = "#GLOBAL") -> bool:
    if patchPattern is None:
        patchPathPattern = patchPath.replace("\\", "/").replace("//", "/").replace("/", ".")
        if patchPathPattern.endswith("."):
            patchPathPattern = patchPathPattern[:-1]
        patchPattern = [
            ("kernel.registry", "kernel.services.DiscordUIService.subsystem.registry"),
            ("kernel.ipc", "kernel.services.DiscordUIService.subsystem.ipc"),
            ("kernel.partitionmgr", "kernel.services.DiscordUIService.subsystem.partitionmgr"),
            ("import commands.", f"import {patchPathPattern}.commands."),
        ]

    def recursiveFileBuild(path: str, l: list) -> list:
        for element in os.listdir(path):
            full_path = os.path.join(path, element)
            if os.path.isdir(full_path):
                l += recursiveFileBuild(full_path, [])
            else:
                l.append(full_path)
        return l

    filesToPatch = recursiveFileBuild(patchPath, [])
    for file in filesToPatch:
        if ".py" not in file or "__pycache__" in file or ".pyc" in file:
            continue
        Journaling.record("INFO", f"Patching: {file}")
        try:
            with open(file, "r") as f:
                content = f.read()
            for line in content.split("\n"):
                if patchNeglectPattern in line:
                    continue
                for pattern in patchPattern:
                    content = content.replace(pattern[0], pattern[1])
                    content = content.replace("..", ".")
            with open(file, "w") as f:
                f.write(content)
            Journaling.record("INFO", f"Patched: {file}")
        except Exception as e:
            Journaling.record("ERROR", f"Error patching file {file}. e: {e}")
    Journaling.record("INFO", f"File patching complete for guild {message.guild.id}.")


def mkIsolation(message: DiscordMessageWrapper) -> bool:
    try:
        # Setup isolation environment
        PartitionMgr.RootFS.mkdir(getRoot(message.guild.id))
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
                },
                "kernel.commands.modify": {
                    "enabled": False,
                    "key": ""
                },
                "kernel.commands.execute": {
                    "enabled": False,
                    "key": ""
                }
            }
        }
        Journaling.record("INFO", f"Isolation container created for guild {message.guild.id}.")
        PartitionMgr.RootFS.write(f"{getRoot(message.guild.id)}/isolation.json", json.dumps(isolationDeclare, indent=4))
        Journaling.record("INFO", f"Isolation declaration created for guild {message.guild.id}.")

        # Copy files
        filesToCopy = [
            ("commands", "commands"),
        ]
        Journaling.record("INFO", f"Copying files to isolation container for guild {message.guild.id}.")
        mkIsolation_sync(message, filesToCopy)

        # File patches
        Journaling.record("INFO", f"Patching files in isolation container for guild {message.guild.id}.")
        mkIsolation_patchImports(message, getRoot(message.guild.id))

        dirsToCreate = [
            "storage",
            "etc/registry"
        ]

        for d in dirsToCreate:
            Journaling.record("INFO", f"Creating directory {d} in isolation container for guild {message.guild.id}.")
            PartitionMgr.RootFS.mkdir(f"{getRoot(message.guild.id)}/{d}")
            Journaling.record("INFO", f"Directory {d} created in isolation container for guild {message.guild.id}.")

        Journaling.record("INFO", f"Preparing registry for isolation container for guild {message.guild.id}.")
        prepareRegistry(message)

        # def updateUserData(message):
        Journaling.record("INFO", "Updating server.json")
        try:
            sv: ServerO = Server.load()
            if sv is None:
                user = User(message.author.id, message.author.name, [], [])
                sv = ServerO(message.guild.id, message.guild.name, [], [], [])
                sv.updateUserObject(user)
                Server.save(sv, message)
            user = Server.getUserAtServer(message.getMessageObject())
            Server.updateUserAtServer(user, message)
            Server.save(sv, message)
        except Exception as e:
            Journaling.record("ERROR", f"Error updating user data: {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintErrors") == "1": print(f"Error updating user data: {e}")
            if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()

        # Journaling.record("INFO", "Updating server.json")

        # updateUserData(message)
        # user = User(message.author.id, message.author.name, [], [])
        # sv: ServerO = ServerO(message.guild.id, message.guild.name, [], [], [user])
        # Server.save(sv, message.getMessageObject())

        Journaling.record("INFO", f"Isolation setup complete for guild {message.guild.id}.")
        return True
    except Exception as e:
        Journaling.record("ERROR", f"Error setting up isolation for guild {message.guild.id}. e: {e}")
        return False


def getIsolationPermission(message: DiscordMessageWrapper, key: str, authorization: str = "") -> str:
    try:
        declaration = json.loads(PartitionMgr.RootFS.read(f"{getRoot(message.guild.id)}/isolation.json"))
        return declaration["permissions"][key]["enabled"] and declaration["permissions"][key]["key"] == authorization
    except Exception as e:
        Journaling.record("ERROR", f"Error getting isolation config key for guild {message.guild.id}. e: {e}")
        return ""


def getCallerContainerPath(mustContain: str = getRoot()) -> str:
    mustContain = mustContain.replace("\\", "/").replace("//", "/")
    for frame in traceback.extract_stack():
        filename = frame.filename
        filename = filename.replace("\\", "/").replace("//", "/")
        if mustContain in filename:
            try:
                session_id = filename.split(mustContain)[1].split("/")[0]
                # if mustContain.endswith("/"):
                return f"{mustContain}{session_id}"
                # return f"{mustContain}/{session_id}"
            except IndexError:
                pass  # Handle cases where the path doesn't have the expected structure
    return None  # Indicate that the session ID wasn't found

def prepareRegistry(message: DiscordMessageWrapper):
    regPath = getContainerPath(message, "etc/registry")
    blueprintList: list = []
    with open("defaults/registry.cordreg", 'r') as f:
        conf: list = f.readlines()
        for line in conf:
            if line.startswith("#"):
                continue
            if line.strip() == "":
                continue
            blueprintList.append(line.strip())

    for reg in blueprintList:
        try:
            regn = reg.split("=")[0]
            optional = regn.startswith("?")
            if optional: regn = regn[1:]
            regVal = Registry.read(regn, regloc=regPath)
            if regVal is None or not optional:
                value = reg.split("=")[1] if len(reg.split("=")) > 1 else None
                Registry.write(regn, value, regloc=regPath)
                Journaling.record("INFO", f"Prepared: {regn}")

        except Exception as e:
            IO.println("Error while preparing registry: " + str(e))


def getContainerPath(message: DiscordMessageWrapper, subDir: str) -> str:
    return getRoot(message.guild.id) + f"/{subDir}"


def getRegistry(message: DiscordMessageWrapper, key: str) -> str:
    return getRoot(message.guild.id) + f"/etc/registry/{key.replace('.', '/')}"


def setRegistry(message: DiscordMessageWrapper, key: str, value: str) -> bool:
    try:
        PartitionMgr.RootFS.write(getRegistry(message, key), value)
        return True
    except Exception as e:
        Journaling.record("ERROR", f"Error setting registry key for guild {message.guild.id}. e: {e}")
        return False
