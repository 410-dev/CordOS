import os

import kernel.host as Host
import kernel.io as IO
import kernel.partitionmgr as PartitionManager

import kernel.commands.packtool.install as Install
import kernel.commands.packtool.remove as Remove

# packtool install <url>...
# packtool remove <name>...
# packtool list


def main(args: list):
    if len(args) < 2:
        IO.println("Usage: packtool <install|remove|list> <url|name>...")
        return

    if args[1] == "install":
        if len(args) < 3:
            IO.println("Usage: packtool install <url>...")
            return
        Install.install(args[2:])

    elif args[1] == "remove":
        if len(args) < 3:
            IO.println("Usage: packtool remove <name>...")
            return
        Remove.remove(args[2:])

    elif args[1] == "list":
        pass
