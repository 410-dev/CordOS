import kernel.profile as Profile
import kernel.registry as Registry

import requests


lifeData = {
    "format": "nanopy-systemlife-1.0",
    "states": {
        "bootable": True,
        "signed": True
    },
    "end-of-life": {
        "epoch": 0,
    }
}


def main():
    url = ["https://hysong.dev/"]
