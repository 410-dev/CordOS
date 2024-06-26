import sys

import kernel.registry as Registry
import kernel.services.power.configure as Power
import kernel.services.versioning.configure as Versioning
import requests


async def mainAsync(args: list, message):
    try:
        branch: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.versioning.Branch", default="stable")
        imageurl: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.versioning.ImageURL", default="https://github.com/410-dev/CordOS/archive/<branch>.zip")
        metaURL: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.versioning.MetaURL", default="https://raw.githubusercontent.com/410-dev/CordOS/<branch>/defaults/registry.cordreg")
        forceReboot: str = Registry.read("SOFTWARE.CordOS.Kernel.Services.versioning.ForceReboot", default="1")

        imageurl = imageurl.replace("<branch>", branch)
        metaURL = metaURL.replace("<branch>", branch)

        if args[0] == "upgrade":
            if not (len(args) > 1 and args[1] == "--reinstall") and (Versioning.getBuild(metaURL) == Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Build") and Versioning.getVersion(metaURL) == Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")):
                await message.reply("You are already on the latest version.")
                return

            if Versioning.getBuild(metaURL) == "N/A" or Versioning.getVersion(metaURL) == "N/A":
                await message.reply("Failed to get latest version information.")
                return

            print("Upgrade procedure started.")
            print("Process 1/2: Downloading and extracting image...", end="")
            await message.reply("Upgrade procedure started. Detailed logs will be available in the console.")
            import os
            import zipfile
            import shutil

            try:
                imageurl = imageurl.replace("<branch>", branch)
                response = requests.get(imageurl)
                if response.status_code != 200:
                    print("Failed.")
                    await message.reply("Failed to download image.")
                    return

                with open("tmp/tmpimg.zip", 'wb') as file:
                    file.write(response.content)

            except Exception as e:
                print(f"Failed. Error: {e}")
                await message.reply(f"Failed to download image. Error: {e}")
                return

            print("Success.")
            print("Process 2/2: Extracting image...", end="")
            try:
                with zipfile.ZipFile("tmp/tmpimg.zip", 'r') as file:
                    for member in file.namelist():
                        if not member.endswith('/'):
                            path_to_extract = os.path.join("etc/UPGRADE_IMAGE", '/'.join(member.split('/')[1:]))
                            os.makedirs(os.path.dirname(path_to_extract), exist_ok=True)
                            with file.open(member) as source, open(path_to_extract, 'wb') as target:
                                target.write(source.read())
            except Exception as e:
                print(f"Failed. Error: {e}")
                await message.reply(f"Failed to extract image. Error: {e}")
                return

            print("Success.")

            print(f"Update is ready to go, and will be rebooted {'once services are closed' if forceReboot != '1' else 'forcefully'}. Check the console for detailed logs.")
            await message.reply(f"Update is ready to go, and will be rebooted {'once services are closed' if forceReboot != '1' else 'forcefully'}. Check the console for detailed logs.")


            Registry.write("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeMode", "etc/UPGRADE_IMAGE")
            Registry.write("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeQueue", "1")
            Power.reboot()

            if forceReboot == "1":
                sys.exit(1)

        elif args[0] == "latest":
            try:
                latestVersion = Versioning.getVersion(metaURL)
                latestBuild = Versioning.getBuild(metaURL)
                currentVersion = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Version")
                currentBuild = Registry.read("SOFTWARE.CordOS.Kernel.Profiles.Build")

                if latestVersion == "N/A" or latestBuild == "N/A":
                    await message.reply("Failed to get latest version information.")
                    return

                if latestVersion == currentVersion and latestBuild == currentBuild:
                    text = "You are up to date."
                else:
                    text = f"Update available."

                await message.reply(f"{text}\nLatest version: {latestVersion} (build {latestBuild})\nCurrent version: {currentVersion} (build {currentBuild})")
            except:
                await message.reply("Failed to get latest version information.")

        elif args[0] == "branch":
            if len(args) < 2:
                await message.reply(f"Current branch: {branch}")
                return

            branches: list = ["stable", "beta", "dev"]
            if args[1] not in branches and not (len(args) > 2 and args[2] == "--force"):
                await message.reply(f"Invalid branch. Valid branches: {', '.join(branches)}")
                return

            Registry.write("SOFTWARE.CordOS.Kernel.Services.versioning.Branch", args[1])
            await message.reply(f"Branch set to {args[1]}.")

        else:
            await message.reply("Usage: versioning <upgrade|latest|branch>\n\nWarning: Once upgrade is triggered, it will force reboot the system and may cause etc loss.")

    except Exception as e:
        await message.reply("Usage: versioning <upgrade|latest|branch>\n\nWarning: Once upgrade is triggered, it will force reboot the system and may cause etc loss.")
        return
