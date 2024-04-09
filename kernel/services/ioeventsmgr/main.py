import asyncio

from discord import Message

import kernel.registry as Registry
import os


def main():
    # Does nothing in the background.
    pass

async def runModule(message: Message, scope: str):
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

    print(f"Event bundles: {eventBundles}")

    if len(eventBundles) == 0:
        return

    # Check if the event is in the eventBundles
    for idx, eventBundle in enumerate(eventBundles):
        print(f"Checking event bundle {eventBundle}...")
        if not os.path.isfile(os.path.join(eventBundle, "main.py")):
            eventBundles.pop(idx)
            print(f"Event bundle {eventBundle} does not have a main.py file.")

    import importlib
    executedTasks: list = []
    for eventBundle in eventBundles:
        try:
            module = importlib.import_module(eventBundle.replace("/", ".").replace("\\", ".") + ".main")
            importlib.reload(module)
            # await module.main(message)
            executedTasks.append(asyncio.create_task(module.main(message)))
            print(f"Event bundle {eventBundle} started in a new thread.")
        except Exception as e:
            print(f"Error while running event bundle {eventBundle}: {e}")

    for task in executedTasks:
        await task


async def onInteractiveInputEvent(message: Message):
    await runModule(message, "interaction")


async def onPassiveInputEvent(message: Message):
    await runModule(message, "passive")


async def onOutputEvent(message: Message):
    # Unsupported now
    pass
