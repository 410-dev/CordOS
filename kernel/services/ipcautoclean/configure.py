import kernel.registry as Registry
import kernel.io as IO

def main(args: list):
    if len(args) < 1:
        IO.println("Usage: ipcautoclean <enabled|disabled|expire=n>")
        return

    if args[0] == "enabled":
        Registry.write("SOFTWARE.NanoPyOS.Kernel.IPC.EnableAutoCleaner", "1")
        IO.println("IPC auto cleaner enabled.")
    elif args[0] == "disabled":
        Registry.write("SOFTWARE.NanoPyOS.Kernel.IPC.EnableAutoCleaner", "0")
        IO.println("IPC auto cleaner disabled.")
    elif args[0].startswith("expire="):
        try:
            time = int(args[0].split("=")[1])
            Registry.write("SOFTWARE.NanoPyOS.Kernel.IPC.MemoryLiveTime", str(time))
            IO.println(f"IPC memory expire time set to {time} seconds.")
        except ValueError:
            IO.println("Invalid time. Expected integer.")

