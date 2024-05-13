import os
import shutil


def corestorage() -> str:
    return "etc"

def etc() -> str:
    return corestorage()


def data() -> str:
    return "storage"


def cache() -> str:
    return "tmp"


def appdata() -> str:
    return f"{data()}/ApplicationData"


def root() -> str:
    return f"./"

class DataPartition:
    @staticmethod
    def read(path: str) -> str:
        with open(os.path.join(data(), path), "r") as f:
            return f.read()

    @staticmethod
    def write(path: str, content: str):
        with open(os.path.join(data(), path), "w") as f:
            f.write(content)

    @staticmethod
    def isFile(path: str) -> bool:
        return os.path.isfile(os.path.join(data(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return os.path.isdir(os.path.join(data(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(os.path.join(data(), path))

    @staticmethod
    def mkdir(path: str):
        os.makedirs(os.path.join(data(), path), exist_ok=True)
