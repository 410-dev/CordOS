import kernel.ipc as IPC
import time

def main():
    while True:
        IPC.removeExpired()
        time.sleep(0.5)

        if IPC.read("power.off"):
            break
