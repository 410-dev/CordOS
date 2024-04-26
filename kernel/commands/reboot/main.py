import kernel.io as IO
import kernel.ipc as IPC


def main(args):
    IPC.set("power.off", True)
    IPC.set("power.off.state", "REBOOT")
    IO.println(f"Reboot signal published. System will reboot after all services have stopped.")