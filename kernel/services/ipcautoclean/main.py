import kernel.ipc as IPC
import kernel.journaling as Journaling
import time

def main():
    while True:
        IPC.removeExpired()
        time.sleep(0.5)

        if IPC.read("power.off"):
            Journaling.record("INFO", "Powering off IPC auto cleaner.")
            break
