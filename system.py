import single

try:
    import json
    import os
    import sys
    import traceback
    import time
    import discord
    import importlib
    import threading
    import asyncio

    import kernel.servers as Servers
    import kernel.objects as Objects
    import kernel.registry as Registry
    import kernel.config as Config
    import kernel.servicectl as Services
    import kernel.launchcmd as Launcher
    import kernel.clock as Clock
    import kernel.ipc as IPC
    import kernel.host as HostMachine
    import kernel.services.ioeventsmgr.main as IOEventsMgr

    from objects.discordmessage import DiscordMessageWrapper

    # Check commandline arguments
    argsList: list = sys.argv
    safeMode: bool = "--safe" in argsList
    singleUser: bool = "--single" in argsList

    foundation = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Foundation")
    version = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")
    print(f"Starting up {foundation} {version}")

    # Load configurations
    Services.start(0, safeMode)
    Clock.init()
    IPC.set("kernel.safemode", safeMode)
    Services.start(1, safeMode)
    Services.start(2, safeMode)
    Services.start(3, safeMode)
    Services.start(4, safeMode)  # Shell level

    while threading.active_count() > 1:
        time.sleep(1)


except Exception as e:
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"KERNEL CRASHED WITH UNHANDLED EXCEPTION")
    print(f"---------------------------------------")
    print(f"Error Time: {time.ctime()}")
    print(f"Error: {e}")
    print(f"---------------------------------------")
    print(f"Stack Trace:")
    traceback.print_exc()
    print(f"---------------------------------------")
    print(f"System will restart in safe mode after 3 seconds.")
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    time.sleep(3)
    sys.exit(3)
