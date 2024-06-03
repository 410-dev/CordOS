import kernel.io as IO
import kernel.ipc as IPC

import kernel.services.power.configure as power

def main(args):
    power.reboot()
