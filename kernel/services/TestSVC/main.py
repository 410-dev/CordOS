import kernel.ipc as IPC
import kernel.io as IO
def main():
    def exec():
        # IO.println("TestSVC: Hello, world!")
        pass

    IPC.repeatUntilShutdown(1.5, exec, delayFirst=True)
