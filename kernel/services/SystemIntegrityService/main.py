import requests

import kernel.partitionmgr as PartitionMgr
import kernel.io as IO


def main():
    IO.println("Checking default installation...")
    if "true" in PartitionMgr.read("/etc/var/installed"):
        IO.println("Default installation already completed.")
        return
