import asyncio
import os

import kernel.registry as Registry
import kernel.journaling as Journaling

def main():
    # Does nothing in the background.
    pass


def printIfEnabled(msg: str):
    Journaling.record("INFO", msg)
    if Registry.read("SOFTWARE.CordOS.Kernel.Services.ioeventsmgr.Print", default="0") == "1":
        print(msg)


async def runModule(message: str, scope: str):
    # List directories in kernel/events/interaction and value of SOFTWARE.CordOS.Events.EventsBundleContainer
    try:
        Journaling.record("INFO", f"Running event bundles for {scope} scope.")
        eventBundles: list = []

        kernelBundles: list = []
        kernelBundleEnabled: bool = Registry.read("SOFTWARE.CordOS.Events.Kernel.InboundPassiveEnabled") == "1" and scope == "passive"
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.InboundInteractiveEnabled") == "1" and scope == "interaction")
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundReplyEnabled") == "1" and scope == "reply")
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundSendEnabled") == "1" and scope == "send")
        kernelBundleEnabled = kernelBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.Kernel.OutboundGlobalEnabled") == "1" and scope == "output")
        if kernelBundleEnabled:
            Journaling.record("INFO", f"Kernel event bundles enabled for {scope} scope.")
            if os.path.isdir(f"kernel/events/{scope}"):
                kernelBundles: list = os.listdir(f"kernel/events/{scope}")
                for idx, eventBundle in enumerate(kernelBundles):
                    kernelBundles[idx] = f"kernel/events/{scope}/{eventBundle}"
                    Journaling.record("INFO", f"Kernel event bundle {kernelBundles[idx]} found.")

        userBundles: list = []
        userBundleEnabled: bool = Registry.read("SOFTWARE.CordOS.Events.User.InboundPassiveEnabled") == "1" and scope == "passive"
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.InboundInteractiveEnabled") == "1" and scope == "interaction")
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundReplyEnabled") == "1" and scope == "reply")
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundSendEnabled") == "1" and scope == "send")
        userBundleEnabled = userBundleEnabled or (Registry.read("SOFTWARE.CordOS.Events.User.OutboundGlobalEnabled") == "1" and scope == "output")
        if userBundleEnabled:
            Journaling.record("INFO", f"User event bundles enabled for {scope} scope.")
            eventBundlesContainers: list = Registry.read("SOFTWARE.CordOS.Events.EventsBundleContainer", default="").replace(", ", ",").split(",")
            Journaling.record("INFO", f"Event bundle containers: {eventBundlesContainers}")
            for eventBundle in eventBundlesContainers:
                if not os.path.isdir(eventBundle):
                    continue
                fileList: list = os.listdir(eventBundle + os.sep + scope)
                if fileList is None or len(fileList) == 0:
                    continue
                userBundles.append(eventBundle)
            for idx, eventBundle in enumerate(userBundles):
                userBundles[idx] = f"{eventBundle}/{scope}"
                Journaling.record("INFO", f"User event bundle {eventBundle} found.")

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
                executedTasks.append(asyncio.create_task(module.main(message)))
                printIfEnabled(f"Event bundle {eventBundle} started in a new thread.")
            except Exception as e:
                printIfEnabled(f"Error while running event bundle {eventBundle}: {e}")

        for task in executedTasks:
            await task

    except Exception as e:
        printIfEnabled(f"Error while running event bundles: {e}")


def onInteractiveInputEvent(message: str):
    runModule(message, "interaction")


def onPassiveInputEvent(message: str):
    runModule(message, "passive")


def onReplyOutputEvent(message: str):
    runModule(message, "reply")


def onSendOutputEvent(message: str):
    runModule(message, "send")


def onOutputEvent(message: str):
    runModule(message, "output")
