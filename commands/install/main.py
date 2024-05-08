import kernel.partitionmgr as PartitionMgr
import kernel.io as IO

import os
import shutil

def main(args: list):
    read = IO.read("Copy default directories to data partition? (y/n)")
    if read != "y":
        IO.println("Operation cancelled.")
        return

    IO.println("Copying default directories to data partition...")
    IO.println("Detected data partition at " + PartitionMgr.data())

    # List directories in defaults
    defaultDirs = os.listdir("defaults/data")
    for d in defaultDirs:
        if os.path.isdir(os.path.join("defaults/data", d)):
            IO.println("Copying " + d + "...")
            shutil.copytree(os.path.join("defaults/data", d), os.path.join(PartitionMgr.data(), d))

    IO.println("Default directories copied successfully.")
    PartitionMgr.write("etc/var/installed", "true")
    IO.println("Operation completed.")
