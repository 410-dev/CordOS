import kernel.ipc as IPC

def main():
    IPC.repeatUntilShutdown(0.5, IPC.removeExpired, delayFirst=True)
