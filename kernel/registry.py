import json
import os
import traceback
import datetime

import kernel.config as Config
import kernel.partitionmgr as PartitionMgr
from kernel.journaling import JournalingContainer



def journal(task: str, exists: bool, default: str, key: str, returned: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caller = traceback.extract_stack(None, 4)[-3]

    scriptPath = caller.filename.replace("//", "/").replace("\\", "/").replace(os.path.abspath(PartitionMgr.root()).replace("//", "/").replace("\\", "/"), "")
    scriptBundleScope = scriptPath.split("/")[-2] + "." + scriptPath.split("/")[-1].replace(".py", "")
    key = key.replace("/", ".").replace("\\", ".")

    if Config.get("registryJournaling.read", default=False) and task == "read":
        JournalingContainer.addEntry("_registry_access_records", f"{timestamp} - [READ] Called by '{scriptBundleScope}': '{key}' (Exists: {exists}, Default: {default}) Returned '{returned}'")
    elif Config.get("registryJournaling.write", default=False) and task == "write":
        JournalingContainer.addEntry("_registry_access_records", f"{timestamp} - [WRITE] Called by '{scriptBundleScope}': '{key}' (Exists: {exists}, Default: {default}) Set '{returned}'")
    elif Config.get("registryJournaling.delete", default=False) and task == "delete":
        JournalingContainer.addEntry("_registry_access_records", f"{timestamp} - [DELETE] Called by '{scriptBundleScope}': '{key}' (Exists: {exists}, Default: {default}) Deleted")
    elif Config.get("registryJournaling.list", default=False) and task == "list":
        JournalingContainer.addEntry("_registry_access_records", f"{timestamp} - [LIST] Called by '{scriptBundleScope}': '{key}' (Exists: {exists}, Default: {default}) Returned '{returned}'")
    elif Config.get("registryJournaling.subkeys", default=False) and task == "subkeys":
        JournalingContainer.addEntry("_registry_access_records", f"{timestamp} - [SUBKEYS] Called by '{scriptBundleScope}': '{key}' (Exists: {exists}, Default: {default}) Returned '{returned}'")


def read(key: str, regloc: str = Config.get("registry"), default=None, writeDefault=False):
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        if writeDefault:
            write(key, default, regloc)
        journal("read", False, default, key, default)
        return default

    # If regloc is directory, read list of files excluding directory and names starting with .
    if os.path.isdir(os.path.join(regloc, key)):
        listOfFiles: list = []
        for file in os.listdir(os.path.join(regloc, key)):
            if os.path.isfile(os.path.join(regloc, key, file)) and not file.startswith("."):
                listOfFiles.append(file + "=" + read(os.path.join(key, file).replace("/", "."), regloc))
            elif os.path.isdir(os.path.join(regloc, key, file)) and not file.startswith("."):
                listOfFiles.append(file)
        journal("read", True, default, key, "<list=content>" if len(listOfFiles) > 0 else "<list=empty>")
        return listOfFiles

    with open(os.path.join(regloc, key), 'r') as f:
        if os.path.isfile(os.path.join(regloc, key)):
            val = f.read().strip()
            journal("read", True, default, key, val)
            return val

        else:
            if writeDefault:
                write(key, default, regloc)
            journal("read", False, default, key, default)
            return default


def isKey(key: str, regloc: str = Config.get("registry")) -> int:
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        journal("read", False, "<none>", key, "0 (Not exists)")
        return 0
    if os.path.isdir(os.path.join(regloc, key)):
        journal("read", True, "<none>", key, "1 (Directory)")
        return 1
    else:
        journal("read", True, "<none>", key, "2 (File)")
        return 2


def write(key: str, value=None, regloc: str = Config.get("registry"), verbose=False):
    key = key.replace(".", "/")

    # If key starts with ? and already exists, return
    if key.startswith("?") and os.path.exists(os.path.join(regloc, key[1:])):
        if verbose: print(f"[  Exists  ] {key[1:].replace("/", ".")}")
        journal("write", True, "<default-init>" if value is None else value, key, "<none>")
        return

    if key.startswith("?"):
        key = key[1:]

    # If parent directory does not exist, create all parent directories
    for i in range(len(key.split("/"))):
        if not os.path.exists(os.path.join(regloc, os.sep.join(key.split("/")[:i]))):
            os.mkdir(os.path.join(regloc, os.sep.join(key.split("/")[:i])))

    # If value is none, create directory
    if value is None:
        os.mkdir(os.path.join(regloc, key))
        journal("write", True, "<key-set>", key, "<none>")
        return

    else:
        with open(os.path.join(regloc, key), 'w') as f:
            if type(value) is list:
                f.write("\n".join(value))
            elif type(value) is dict:
                f.write(json.dumps(value))
            else:
                f.write(value)
            if verbose: print(f"[ Generate ] {key.replace('/', '.').replace('?', '')}")
            journal("write", True, value, key, "<none>")


def delete(key: str, deleteSubkeys: bool = False, regloc: str = Config.get("registry")):
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        journal("delete", False, "<none>", key, "<none>")
        return

    if os.path.isfile(os.path.join(regloc, key)):
        if key.startswith("?"):
            key = key[1:]
        if key == "":
            return
        os.remove(os.path.join(regloc, key))
        journal("delete", True, "<none>", key, "<none>")
    else:
        if deleteSubkeys:
            for file in os.listdir(os.path.join(regloc, key)):
                journal("delete", True, "<none>", os.path.join(key, file), "<none>")
                if os.path.isfile(os.path.join(regloc, key, file)):
                    os.remove(os.path.join(regloc, key, file))
                else:
                    delete(os.path.join(key, file), deleteSubkeys, regloc)
        os.rmdir(os.path.join(regloc, key))
        journal("delete", True, "<none>", key, "<none>")


def listSubKeys(key: str, subdirectories: list = [], regloc: str = Config.get("registry")) -> list:
    key = key.replace(".", "/")
    if not os.path.exists(os.path.join(regloc, key)):
        journal("subkeys", False, "<none>", key, "<list=empty>")
        return []

    listOfFiles: list = []
    for file in os.listdir(os.path.join(regloc, key)):
        if os.path.isfile(os.path.join(regloc, key, file)) and not file.startswith("."):
            listOfFiles.append(file.replace("/", ".") + "=" + read(os.path.join(key, file).replace("/", "."), regloc))
        elif os.path.isdir(os.path.join(regloc, key, file)) and not file.startswith("."):
            listSubKeys(os.path.join(key, file), subdirectories, regloc)

    journal("subkeys", True, "<none>", key, "<list=content>" if len(listOfFiles) > 0 else "<list=empty>")
    return listOfFiles


def build(blueprintPath: str, registryPath: str = Config.get("registry"), silent=False):
    lines: list = []
    with open(blueprintPath, 'r') as f:
        conf: list = f.readlines()
        for line in conf:
            if line.startswith("#"):
                continue
            if line.strip() == "":
                continue
            lines.append(line.strip())

    for line in lines:
        key = line.split("=")[0]
        value = line.split("=")[1] if len(line.split("=")) > 1 else None
        write(key, value, registryPath, verbose=not silent)

