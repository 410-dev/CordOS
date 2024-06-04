import kernel.ipc as IPC
import kernel.partitionmgr as PartitionMgr

from kernel.services.DiscordUIService.objects.discordmessage import DiscordMessageWrapper

import traceback
import hashlib

def getExecutionCallerScriptPathAsId(Id: str) -> str:
    trace = traceback.extract_stack()
    fullPath = trace[-2].filename
    scope = fullPath.replace("\\", "/").replace("//", "/")
    scope = hashlib.md5(scope.encode()).hexdigest()
    return f"{scope}.{Id}"

def set(Id: str, value: object):
    IPC.set(getExecutionCallerScriptPathAsId(Id), value)

def delete(Id: str):
    IPC.delete(getExecutionCallerScriptPathAsId(Id))

def read(Id: str, default=None):
    return IPC.read(getExecutionCallerScriptPathAsId(Id), default=default)

def exists(Id: str) -> bool:
    return IPC.exists(getExecutionCallerScriptPathAsId(Id))

def removeExpired():
    IPC.removeExpired()

def canRepeatUntilShutdown():
    return IPC.canRepeatUntilShutdown()

def repeatUntilShutdown(delay: float, function, delayFirst=False, terminateIfAnyOf=None, terminateIfAllOf=None):
    IPC.repeatUntilShutdown(delay, function, delayFirst=delayFirst, terminateIfAnyOf=terminateIfAnyOf, terminateIfAllOf=terminateIfAllOf)
