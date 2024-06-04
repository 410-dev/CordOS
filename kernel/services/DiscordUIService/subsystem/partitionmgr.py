import os
import shutil


class Data:

    @staticmethod
    def read(path: str) -> str:
        return RootFS.read(os.path.join(Data.path(), path))

    @staticmethod
    def write(path: str, content: str):
        RootFS.write(os.path.join(Data.path(), path), content)

    @staticmethod
    def isFile(path: str) -> bool:
        return RootFS.isFile(os.path.join(Data.path(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return RootFS.isDir(os.path.join(Data.path(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return RootFS.exists(os.path.join(Data.path(), path))

    @staticmethod
    def mkdir(path: str):
        RootFS.mkdir(os.path.join(Data.path(), path))

    @staticmethod
    def path(subPath: str = "") -> str:
        return "storage" + ("/" + subPath if subPath != "" else "")

    @staticmethod
    def copyDefault(path: str, existOK: bool = True):
        RootFS.copy(os.path.join(RootFS.defaults(), Data.path(), path), os.path.join(Data.path(), path), existOK)

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(Data.path(), path))

    @staticmethod
    def rm(path: str):
        return RootFS.rm(os.path.join(Data.path(), path))


class Etc:
    @staticmethod
    def read(path: str) -> str:
        return RootFS.read(os.path.join(Etc.path(), path))

    @staticmethod
    def write(path: str, content: str):
        RootFS.write(os.path.join(Etc.path(), path), content)

    @staticmethod
    def isFile(path: str) -> bool:
        return RootFS.isFile(os.path.join(Etc.path(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return RootFS.isDir(os.path.join(Etc.path(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return RootFS.exists(os.path.join(Etc.path(), path))

    @staticmethod
    def mkdir(path: str):
        RootFS.mkdir(os.path.join(Etc.path(), path))

    @staticmethod
    def path(subPath: str = "") -> str:
        return "etc" + ("/" + subPath if subPath != "" else "")

    @staticmethod
    def copyDefault(path: str, existOK: bool = True):
        RootFS.copy(os.path.join(RootFS.defaults(), Etc.path(), path), os.path.join(Etc.path(), path), existOK)

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(Etc.path(), path))

    @staticmethod
    def rm(path: str):
        return RootFS.rm(os.path.join(Etc.path(), path))


class RootFS:

    @staticmethod
    def defaults():
        return "defaults"

    @staticmethod
    def path(subDir: str) -> str:
        return "./" + subDir

    @staticmethod
    def read(path: str) -> str:
        try:
            with open(os.path.join(RootFS.path(), path), "r") as f:
                return f.read()
        except:
            return None

    @staticmethod
    def write(path: str, content: str):
        if not os.path.exists(os.path.join(RootFS.path(), os.path.dirname(path))):
            os.makedirs(os.path.join(RootFS.path(), os.path.dirname(path)), exist_ok=True)
        with open(os.path.join(RootFS.path(), path), "w") as f:
            f.write(content)

    @staticmethod
    def isFile(path: str) -> bool:
        return os.path.isfile(os.path.join(RootFS.path(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return os.path.isdir(os.path.join(RootFS.path(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(os.path.join(RootFS.path(), path))

    @staticmethod
    def mkdir(path: str):
        os.makedirs(os.path.join(RootFS.path(), path), exist_ok=True)

    @staticmethod
    def copy(src: str, dst: str, exist_ok: bool = True):
        if not os.path.exists(os.path.join(RootFS.path(), src)):
            return
        if os.path.isfile(os.path.join(RootFS.path(), src)):
            shutil.copyfile(os.path.join(RootFS.path(), src), os.path.join(RootFS.path(), dst))
        elif os.path.isdir(os.path.join(RootFS.path(), src)):
            shutil.copytree(os.path.join(RootFS.path(), src), os.path.join(RootFS.path(), dst), dirs_exist_ok=exist_ok)

    @staticmethod
    def move(src: str, dst: str):
        if not os.path.exists(os.path.join(RootFS.path(), src)):
            return
        shutil.move(os.path.join(RootFS.path(), src), os.path.join(RootFS.path(), dst))

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(RootFS.path(), path))

    @staticmethod
    def rm(path: str) -> bool:
        full_path = os.path.join(RootFS.path(), path)
        if not os.path.exists(full_path):
            return False

        def on_rm_error(func, p, exc_info):
            # Change file to be writable and then remove
            os.chmod(p, 0o777)
            func(p)

        if os.path.isfile(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path, onerror=on_rm_error)

        return True

class Cache:
    @staticmethod
    def read(path: str) -> str:
        return RootFS.read(os.path.join(Cache.path(), path))

    @staticmethod
    def write(path: str, content: str):
        RootFS.write(os.path.join(Cache.path(), path), content)

    @staticmethod
    def isFile(path: str) -> bool:
        return RootFS.isFile(os.path.join(Cache.path(), path))

    @staticmethod
    def isDir(path: str) -> bool:
        return RootFS.isDir(os.path.join(Cache.path(), path))

    @staticmethod
    def exists(path: str) -> bool:
        return RootFS.exists(os.path.join(Cache.path(), path))

    @staticmethod
    def mkdir(path: str):
        RootFS.mkdir(os.path.join(Cache.path(), path))

    @staticmethod
    def path(subPath: str = "") -> str:
        return "tmp" + ("/" + subPath if subPath != "" else "")

    @staticmethod
    def copyDefault(path: str, existOK: bool = True):
        RootFS.copy(os.path.join(RootFS.defaults(), Cache.path(), path), os.path.join(Cache.path(), path), existOK)

    @staticmethod
    def list(path: str) -> list:
        return os.listdir(os.path.join(Cache.path(), path))

    @staticmethod
    def rm(path: str):
        return RootFS.rm(os.path.join(Cache.path(), path))