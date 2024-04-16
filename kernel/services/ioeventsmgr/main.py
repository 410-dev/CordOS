import asyncio

from objects.discordmessage import DiscordMessageWrapper

import kernel.registry as Registry
import os


def main():
    # Does nothing in the background.
    pass


def printIfEnabled(msg: str):
    if Registry.read("SOFTWARE.CordOS.Kernel.Services.ioeventsmgr.Print", default="0") == "1":
        print(msg)


async def runModule(message: DiscordMessageWrapper, scope: str):
    # List directories in kernel/events/interaction and value of SOFTWARE.CordOS.Events.EventsBundleContainer
    eventBundles: list = []

    kernelBundles: list = []
    kernelBundleEnabled: bool = Registry.read("SOFTWARE.CordOS.Events.Kernel.InboundPassiveEnabled") == "1" and scope == "passive"
    kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.InboundInteractiveEnabled") == "1" and scope == "interaction")
    kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundEnabled") == "1" and scope == "output")
    if kernelBundleEnabled:
        kernelBundles: list = os.listdir(f"kernel/events/{scope}")
        for idx, eventBundle in enumerate(kernelBundles):
            kernelBundles[idx] = f"kernel/events/{scope}/{eventBundle}"

    userBundles: list = []
    userBundleEnabled: bool = Registry.read("SOFTWARE.CordOS.Events.User.InboundPassiveEnabled") == "1" and scope == "passive"
    userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.InboundInteractiveEnabled") == "1" and scope == "interaction")
    userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundEnabled") == "1" and scope == "output")
    if userBundleEnabled:
        eventBundlesContainers: list = Registry.read("SOFTWARE.CordOS.Events.EventsBundleContainer", default="").replace(", ", ",").split(",")
        for eventBundle in eventBundlesContainers:
            fileList: list = os.listdir(eventBundle + os.sep + scope)
            if fileList is None or len(fileList) == 0:
                continue
            userBundles.append(eventBundle)
        for idx, eventBundle in enumerate(userBundles):
            userBundles[idx] = f"{eventBundle}/{scope}"

    eventBundles.extend(kernelBundles)
    eventBundles.extend(userBundles)

    printIfEnabled(f"Event bundles: {eventBundles}")

    if len(eventBundles) == 0:
        return

    # Check if the event is in the eventBundles
    for idx, eventBundle in enumerate(eventBundles):
        printIfEnabled(f"Checking event bundle {eventBundle}...")
        if not os.path.isfile(os.path.join(eventBundle, "main.py")):
            eventBundles.pop(idx)
            printIfEnabled(f"Event bundle {eventBundle} does not have a main.py file.")

    import importlib
    executedTasks: list = []
    for eventBundle in eventBundles:
        try:
            module = importlib.import_module(eventBundle.replace("/", ".").replace("\\", ".") + ".main")
            importlib.reload(module)
            # await module.main(message)
            executedTasks.append(asyncio.create_task(module.main(message)))
            printIfEnabled(f"Event bundle {eventBundle} started in a new thread.")
        except Exception as e:
            printIfEnabled(f"Error while running event bundle {eventBundle}: {e}")

    for task in executedTasks:
        await task


async def onInteractiveInputEvent(message: DiscordMessageWrapper):
    await runModule(message, "interaction")


async def onPassiveInputEvent(message: DiscordMessageWrapper):
    await runModule(message, "passive")


async def onReplyOutputEvent(message: DiscordMessageWrapper):
    print("Reply output event")
    await runModule(message, "output_reply")


async def onSendOutputEvent(message: DiscordMessageWrapper):
    print("Send output event")
    await runModule(message, "output_send")


async def onOutputEvent(message: DiscordMessageWrapper):
    print("Output event")
    await runModule(message, "output")
