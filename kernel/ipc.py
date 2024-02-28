import os
import shutil
import json

import kernel.partitionmgr as Partitions
import kernel.clock as Clock

def set(id: str, value: str):
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        os.makedirs(parentPath)

    # Write value to file
    with open(f"{parentPath}/value", 'w') as f:
        f.write(value)

def setJson(id: str, value: dict):
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        os.makedirs(parentPath)

    # Write value to file
    with open(f"{parentPath}/value", 'w') as f:
        f.write(json.dumps(value))

def delete(id: str):
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        return

    # Delete value file
    os.remove(f"{parentPath}/value")

    # Delete parent path
    os.rmdir(parentPath)

def read(id: str) -> str:
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        return ""

    # Read value from file
    with open(f"{parentPath}/value", 'r') as f:
        return f.read()
    
def readJson(id: str) -> dict:
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        return {}

    # Read value from file
    with open(f"{parentPath}/value", 'r') as f:
        return json.loads(f.read())
    
def exists(id: str) -> bool:
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    return os.path.exists(parentPath)

def init():
    # Check if uptime is less than 10 seconds
    if Clock.getUptimeSeconds() < 10000:
        # Clear IPC cache
        try:
            if os.path.exists(f"{Partitions.cache()}/ipc"):
                shutil.rmtree(os.path.join(Partitions.cache(), "ipc"))
            os.makedirs(f"{Partitions.cache()}/ipc", exist_ok=True)
            print("IPC cache cleared.")
        except Exception as e:
            print("Error in clearing IPC cache: " + str(e))
        
    else:
        print(f"IPC cache not cleared (Uptime > 3 seconds).")