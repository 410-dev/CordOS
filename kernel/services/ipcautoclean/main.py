import kernel.ipc as IPC
# import kernel.journaling as Journaling
# import time

def main():
    IPC.repeatUntilShutdown(0.5, IPC.removeExpired, delayFirst=True)
