import kernel.io as IO
import kernel.host as Host
import kernel.partitionmgr as PartitionManager
import kernel.commands.packtool.spec as Spec
import kernel.commands.packtool.database as Database
import requests
import json


def remove(ids: list):
    for uid in ids:
        IO.println(f"Removing {uid}...")
        success, stage, message = removeTask(uid)
        if not success:
            IO.println(message)
            return


def removeTask(uid: str) -> tuple:
    return False, "NOT_IMPLEMENTED", "This is not implemented yet."
