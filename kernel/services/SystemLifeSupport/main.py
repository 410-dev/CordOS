import kernel.profile as Profile
import kernel.registry as Registry
import kernel.io as IO
import kernel.ipc as IPC

import kernel.services.power.configure as power

import requests

def main():

    # Build-specific signature check
    url = Registry.read("SOFTWARE.CordOS.Security.SystemLifeSupport.StateFileServers", default="https://hysong.dev/keystore/api/cordos/{build}.lifesupport")
    url = url.replace("{build}", Profile.getKernelBuild())
    response = requests.get(url)
    message = ["", ""] # Yes, No
    bootable = True

    if response.status_code != 200 and response.status_code != 404:
        IO.println(f"Failed to check system bootability. The system may be unstable or severely vulnerable. Server returned {response.status_code}.")
        return
    elif response.status_code == 200:
        textContent = response.text
        lines = textContent.split("\n")

        for line in lines:
            if line.startswith("#") or line == "":
                continue

            if line.startswith("bootable="):
                values: str = line.split("=")[1]
                if values == "no":
                    bootable = False

            elif line.startswith("bootable.yes.message="):
                message[0] = line.split("=")[1]
            elif line.startswith("bootable.no.message="):
                message[1] = line.split("=")[1]
            elif line.startswith("bootable.warning.message="):
                IO.println(f"Warning: {line.split('=')[1]}")
                IPC.set("kernel.bootable.warning", line.split('=')[1])

    # Global bootlock check
    url = Registry.read("SOFTWARE.CordOS.Security.SystemLifeSupport.Bootlock", default="https://hysong.dev/keystore/api/cordos/bootlocklist")
    response = requests.get(url)
    if response.status_code != 200 and response.status_code != 404:
        IO.println(f"Failed to check system bootability. The system may be unstable or severely vulnerable. Server returned {response.status_code}.")
        return
    elif response.status_code == 200:
        textContent = response.text
        lines = textContent.split("\n")
        for line in lines:
            if line.startswith("#") or line == "":
                continue

            if line.startswith(f"{Profile.getKernelBuild()}:"):
                bootable = False
                message[1] = "System is not bootable due to bootlock - " + line.split(":")[1]

        if not bootable:
            IO.println(f"System is not bootable. {message[1]}")
            power.main(["halt"])

        else:
            # IO.println(f"System is bootable.")
            pass
