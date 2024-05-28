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


def default() -> str:
    return f"defaults"


def root() -> str:
    return f"./"

class Data:
    @staticmethod
    def read(path: str) -> str:
        return RootFS.read(os.path.join(data(), path))

    @staticmethod
    def write(path: str, content: str):
        RootFS.write(os.path.join(data(), path), content)

    @staticmethod
    def isFile(path: str) -> bool:
        return RootFS.isFile(os.path.join(data(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return RootFS.isDir(os.path.join(data(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return RootFS.exists(os.path.join(data(), path))

    @staticmethod
    def mkdir(path: str):
        RootFS.mkdir(os.path.join(data(), path))

    @staticmethod
    def path(subPath: str = "") -> str:
        return data() + ("/" + subPath if subPath != "" else "")

    @staticmethod
    def copyDefault(path: str, existOK: bool = True):
        RootFS.copy(os.path.join(default(), data(), path), os.path.join(data(), path), existOK)

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(data(), path))

class Etc:
    @staticmethod
    def read(path: str) -> str:
        return RootFS.read(os.path.join(etc(), path))

    @staticmethod
    def write(path: str, content: str):
        RootFS.write(os.path.join(etc(), path), content)

    @staticmethod
    def isFile(path: str) -> bool:
        return RootFS.isFile(os.path.join(etc(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return RootFS.isDir(os.path.join(etc(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return RootFS.exists(os.path.join(etc(), path))

    @staticmethod
    def mkdir(path: str):
        RootFS.mkdir(os.path.join(etc(), path))

    @staticmethod
    def path(subPath: str = "") -> str:
        return etc() + ("/" + subPath if subPath != "" else "")

    @staticmethod
    def copyDefault(path: str, existOK: bool = True):
        RootFS.copy(os.path.join(default(), etc(), path), os.path.join(etc(), path), existOK)

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(etc(), path))


class RootFS:
    @staticmethod
    def read(path: str) -> str:
        try:
            with open(os.path.join(root(), path), "r") as f:
                return f.read()
        except:
            return None

    @staticmethod
    def write(path: str, content: str):
        if not os.path.exists(os.path.join(root(), os.path.dirname(path))):
            os.makedirs(os.path.join(root(), os.path.dirname(path)), exist_ok=True)
        with open(os.path.join(root(), path), "w") as f:
            f.write(content)

    @staticmethod
    def isFile(path: str) -> bool:
        return os.path.isfile(os.path.join(root(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return os.path.isdir(os.path.join(root(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(os.path.join(root(), path))

    @staticmethod
    def mkdir(path: str):
        os.makedirs(os.path.join(root(), path), exist_ok=True)

    @staticmethod
    def copy(src: str, dst: str, exist_ok: bool = True):
        if not os.path.exists(os.path.join(root(), src)):
            return
        if os.path.isfile(os.path.join(root(), src)):
            shutil.copyfile(os.path.join(root(), src), os.path.join(root(), dst))
        elif os.path.isdir(os.path.join(root(), src)):
            shutil.copytree(os.path.join(root(), src), os.path.join(root(), dst), dirs_exist_ok=exist_ok)

    @staticmethod
    def move(src: str, dst: str):
        if not os.path.exists(os.path.join(root(), src)):
            return
        shutil.move(os.path.join(root(), src), os.path.join(root(), dst))

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(root(), path))


class Cache:
    @staticmethod
    def read(path: str) -> str:
        return RootFS.read(os.path.join(cache(), path))

    @staticmethod
    def write(path: str, content: str):
        RootFS.write(os.path.join(cache(), path), content)

    @staticmethod
    def isFile(path: str) -> bool:
        return RootFS.isFile(os.path.join(cache(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return RootFS.isDir(os.path.join(cache(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return RootFS.exists(os.path.join(cache(), path))

    @staticmethod
    def mkdir(path: str):
        RootFS.mkdir(os.path.join(cache(), path))

    @staticmethod
    def path(subPath: str = "") -> str:
        return cache() + ("/" + subPath if subPath != "" else "")

    @staticmethod
    def copyDefault(path: str, existOK: bool = True):
        RootFS.copy(os.path.join(default(), cache(), path), os.path.join(cache(), path), existOK)

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(cache(), path))