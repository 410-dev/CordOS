import os
import kernel.partitionmgr as Partitions

def set(id: str, value: str):
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        os.makedirs(parentPath)

    # Write value to file
    with open(f"{parentPath}/value", 'w') as f:
        f.write(value)

def read(id: str) -> str:
    parentPath: str = f"{Partitions.cache()}/ipc/{id}"

    # Check if parent path exists
    if not os.path.exists(parentPath):
        return ""

    # Read value from file
    with open(f"{parentPath}/value", 'r') as f:
        return f.read()