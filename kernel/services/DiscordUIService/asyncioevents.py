import asyncio

import kernel.registry as Registry
import os

def printIfEnabled(msg: str):
    if Registry.read("SOFTWARE.CordOS.Kernel.Services.ioeventsmgr.Print", default="0") == "1":
        print(msg)


async def runModule(message, scope: str):
    # List directories in kernel/events/interaction and value of SOFTWARE.CordOS.Events.EventsBundleContainer
    try:
        eventBundles: list = []

        kernelBundles: list = []
        kernelBundleEnabled: bool = Registry.read("SOFTWARE.CordOS.Events.Kernel.InboundPassiveEnabled") == "1" and scope == "passive"
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.InboundInteractiveEnabled") == "1" and scope == "interaction")
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundReplyEnabled") == "1" and scope == "reply")
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundSendEnabled") == "1" and scope == "send")
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundGlobalEnabled") == "1" and scope == "output")
        if kernelBundleEnabled:
            if os.path.isdir(f"kernel/events/{scope}"):
                kernelBundles: list = os.listdir(f"kernel/events/{scope}")
                for idx, eventBundle in enumerate(kernelBundles):
                    kernelBundles[idx] = f"kernel/events/{scope}/{eventBundle}"

        userBundles: list = []
        userBundleEnabled: bool = Registry.read("SOFTWARE.CordOS.Events.User.InboundPassiveEnabled") == "1" and scope == "passive"
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.InboundInteractiveEnabled") == "1" and scope == "interaction")
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundReplyEnabled") == "1" and scope == "reply")
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundSendEnabled") == "1" and scope == "send")
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundGlobalEnabled") == "1" and scope == "output")
        if userBundleEnabled:
            eventBundlesContainers: list = Registry.read("SOFTWARE.CordOS.Events.EventsBundleContainer", default="").replace(", ", ",").split(",")
            for eventBundle in eventBundlesContainers:
                if not os.path.isdir(eventBundle):
                    continue
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
                executedTasks.append(asyncio.create_task(module.mainAsync(message)))
                printIfEnabled(f"Event bundle {eventBundle} started in a new thread.")
            except Exception as e:
                printIfEnabled(f"Error while running event bundle {eventBundle}: {e}")

        for task in executedTasks:
            await task

    except Exception as e:
        printIfEnabled(f"Error while running event bundles: {e}")


async def onInteractiveInputEvent(message):
    await runModule(message, "interaction")


async def onPassiveInputEvent(message):
    await runModule(message, "passive")


async def onReplyOutputEvent(message):
    await runModule(message, "reply")


async def onSendOutputEvent(message):
    await runModule(message, "send")


async def onOutputEvent(message):
    await runModule(message, "output")
