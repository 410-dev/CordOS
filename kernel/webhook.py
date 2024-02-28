import kernel.registry as Registry

import os
from discord_webhook import DiscordWebhook

def list() -> list:
    path: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.RegistrationPath")
    l: list = os.listdir(path)
    for i, element in enumerate(l):
        if not os.path.isfile(os.path.join(path, element)):
            l.pop(i)
    for i, element in enumerate(l):
        l[i] = element.split(".")[0]
    return l

def send(webhookURL: str, message: str) -> None:
    webhook = DiscordWebhook(url=webhookURL, content=message)
    response = webhook.execute()
    print(response)

def getLibrary(webhookID: str) -> str:
    libraryPath: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.LibraryPath")
    libraryPath = libraryPath.replace("<id>", webhookID)
    os.makedirs(libraryPath, exist_ok=True)
    os.makedirs(f"{libraryPath}/linkages", exist_ok=True)
    return libraryPath