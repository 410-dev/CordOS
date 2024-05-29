import os

import kernel.host as Host
import kernel.io as IO
import kernel.partitionmgr as PartitionManager

import kernel.commands.packtool.install as Install
import kernel.commands.packtool.remove as Remove
import kernel.commands.packtool.list as List

# packtool install <url>...
# packtool remove <name>...
# packtool list


def main(args: list):
    if len(args) < 2:
        IO.println("Usage: packtool <install|remove|list> <url|name>...")
        return

    if args[1] == "install" or args[1] == "patch":
        if len(args) < 3:
            IO.println("Usage: packtool install|patch <url>...")
            return
        ignoreDependencies = False
        ignoreConflicts = False
        reinstall = False
        if len(args) > 3 and '--ignore-dependencies' in args:
            ignoreDependencies = True
        if len(args) > 3 and '--ignore-conflicts' in args:
            ignoreConflicts = True
        if len(args) > 3 and '--reinstall' in args:
            reinstall = True
        Install.install(args[2:], args[1], ignoreDependencies, ignoreConflicts, reinstall)

    elif args[1] == "remove":
        if len(args) < 3:
            IO.println("Usage: packtool remove <name>...")
            return
        ignoreDependencies = False
        removeAsChain = False
        if len(args) > 3 and '--ignore-dependencies' in args:
            ignoreDependencies = True
        if len(args) > 3 and '--chain' in args:
            removeAsChain = True
        Remove.remove(args[2:], ignoreDependencies, removeAsChain)

    elif args[1] == "list":
        output = List.listPackages()
        IO.println(output)
