import kernel.io as IO


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
        install.install(args[2:], args[1], ignoreDependencies, ignoreConflicts, reinstall)

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
        remove.remove(args[2:], ignoreDependencies, removeAsChain)

    elif args[1] == "list":
        output = list.listPackages()
        IO.println(output)
