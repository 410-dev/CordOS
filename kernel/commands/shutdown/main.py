import kernel.io as IO
import kernel.ipc as IPC


def main(args):
    IPC.set("power.off", True)
    IPC.set("power.off.state", "OFF")
    IO.println(f"Shutdown signal published. System will shutdown after all services have stopped.")