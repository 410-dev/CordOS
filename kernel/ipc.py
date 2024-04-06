import threading
import time

import kernel.registry as Registry
import kernel.clock as Clock

class IPCMemory:
    memory = {}
    referenceTime = {}

    def add(id: str, value: object):
        IPCMemory.memory[id] = value
        IPCMemory.referenceTime[id] = Clock.getEpoch()

    def get(id: str, default=None) -> object:
        if IPCMemory.exists(id):
            IPCMemory.referenceTime[id] = Clock.getEpoch()
            return IPCMemory.memory[id]
        return default

    def exists(id: str) -> bool:
        return id in IPCMemory.memory

    def delete(id: str):
        del IPCMemory.memory[id]
        del IPCMemory.referenceTime[id]


def set(id: str, value: object):
    # Use static memory
    IPCMemory.add(id, value)


def delete(id: str):
    # Use static memory
    IPCMemory.delete(id)

def read(id: str, default=None) -> object:
    # Use static memory
    return IPCMemory.get(id, default=default)

def exists(id: str) -> bool:
    # Use static memory
    return IPCMemory.exists(id)

def removeExpired():
    ipcGC: int = int(Registry.read("SOFTWARE.CordOS.Kernel.IPC.EnableAutoCleaner", default="1"))
    if ipcGC == 0:
        return
    memoryLiveTime: int = int(Registry.read("SOFTWARE.CordOS.Kernel.IPC.MemoryLiveTime", default="1800"))
    for key in IPCMemory.memory.keys():
        if IPCMemory.referenceTime[key] + memoryLiveTime < Clock.getEpoch():
            IPCMemory.delete(key)

