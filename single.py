import kernel.registry as Registry

def shell():
    print(f"{Registry.read('SOFTWARE.CordOS.Kernel.Programs.Paths')}")
    print("WARNING: Single user mode is not supported right now.")
    