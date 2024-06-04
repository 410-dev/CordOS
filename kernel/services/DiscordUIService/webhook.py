import kernel.registry as Registry
import kernel.journaling as Journaling
from kernel.services.DiscordUIService.objects.embedmsg import EmbeddedMessage

import os
from discord_webhook import DiscordWebhook, DiscordEmbed


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
    Journaling.record("INFO", f"Webhook response: {response} for url {webhookURL}")


def sendEmbed(webhookURL: str, embedContent: EmbeddedMessage) -> None:
    webhook = DiscordWebhook(url=webhookURL)
    embed = DiscordEmbed(
        title=embedContent.get("title"),
        description=embedContent.get("description"),
        color=embedContent.get("color")
    )
    webhook.add_embed(embed)
    response = webhook.execute()
    Journaling.record("INFO", f"Webhook response: {response} for url {webhookURL}")


def getLibrary(webhookID: str) -> str:
    libraryPath: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.Webhook.LibraryPath")
    libraryPath = libraryPath.replace("<id>", webhookID)
    os.makedirs(libraryPath, exist_ok=True)
    os.makedirs(f"{libraryPath}/linkages", exist_ok=True)
    return libraryPath

def getLinkages(webhookID: str) -> list:
    libraryPath: str = getLibrary(webhookID)
    linkagesPath: str = f"{libraryPath}/linkages"
    l: list = os.listdir(linkagesPath)
    webhookURLs: list = []
    for i, element in enumerate(l):
        if not os.path.isfile(os.path.join(linkagesPath, element)):
            continue
        with open(os.path.join(linkagesPath, element), "r") as f:
            webhookURLs.append(f.read().strip())
    return webhookURLs

def removeLinkage(webhookID: str, webhookURL: str) -> bool:
    specialChars: list = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", " ", "-"]
    url = webhookURL[1]
    url = url.split("webhooks/")[1]
    for char in specialChars:
        url = url.replace(char, "")
    linkagesPath: str = f"{getLibrary(webhookID)}/linkages"
    try:
        os.remove(f"{linkagesPath}/{url}")
        return True
    except:
        return False

def setLinkage(webhookID: str, webhookURL: str) -> None:
    specialChars: list = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", " ", "-"]
    url = webhookURL.split("webhooks/")[1]
    for char in specialChars:
        url = url.replace(char, "")

    os.makedirs(f"{getLibrary(webhookID)}/linkages", exist_ok=True)
    
    with open(f"{getLibrary(webhookID)}/linkages/{url}", 'w') as f:
        f.write(webhookURL)

# def getLinkages(webhookID: str) -> list:
#     specialChars: list = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", " ", "-"]
#     url = webhookID
#     for char in specialChars:
#         url = url.replace(char, "")
#     linkagesPath: str = f"{getLibrary(webhookID)}/linkages"
#     l: list = os.listdir(linkagesPath)
#     webhookURLs: list = []
#     for i, element in enumerate(l):
#         if not os.path.isfile(os.path.join(linkagesPath, element)):
#             continue
#         with open(os.path.join(linkagesPath, element), "r") as f:
#             webhookURLs.append(f.read().strip())
#     return webhookURLs