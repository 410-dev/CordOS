import os
import shutil


def data() -> str:
    return "storage"


def cache() -> str:
    return f"{data()}/cache"


def files() -> str:
    return f"{data()}/files"


def root() -> str:
    return f"./"


def write(path: str, content: str):
    with open(os.path.join(data(), path), "w") as f:
        f.write(content)


def read(path: str) -> str:
    with open(os.path.join(data(), path), "r") as f:
        return f.read()


def isFile(path: str) -> bool:
    return os.path.isfile(os.path.join(data(), path))


def isDir(path: str) -> bool:
    return os.path.isdir(os.path.join(data(), path))


def exists(path: str) -> bool:
    return os.path.exists(os.path.join(data(), path))


def mkdir(path: str):
    os.makedirs(os.path.join(data(), path), exist_ok=True)
