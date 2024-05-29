import kernel.registry as Registry
import kernel.ipc as IPC
import kernel.io as IO


def main(args: list):
    try:
        foundation = Registry.read("SOFTWARE.NanoPyOS.Kernel.Profiles.Foundation")
        version = Registry.read("SOFTWARE.NanoPyOS.Kernel.Profiles.Version")
        build = Registry.read("SOFTWARE.NanoPyOS.Kernel.Profiles.Build")
        isSafe = "Normal Mode" if not IPC.read("kernel.safemode") else "Safe Mode"

        IO.println(f"Version Profiling:\n\nSystem: {foundation} {version} (build {build}) {'(TEST VERSION) ' if '.alpha.' in build or '.beta.' in build or '.test.' in build else '' } {isSafe}\nCurrently using Sync Mode.")

    except Exception as e:
        IO.println(f"Error loading profile: {e}")
