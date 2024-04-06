import os
import shutil
import kernel.registry as Registry
import kernel.host as Host

"""

This service runs sync mode - Be careful!

"""

def cp(src: str, dest: str):
    for root, dirs, files in os.walk(src, topdown=True):
        # Ensure the directory structure is mirrored in dest
        for dir_name in dirs:
            source_dir = os.path.join(root, dir_name)
            relative_path = os.path.relpath(source_dir, src)
            destination_dir = os.path.join(dest, relative_path)

            try:
                os.makedirs(destination_dir)
                print(f"Directory created: {destination_dir}")
            except FileExistsError:
                print(f"Directory already exists: {destination_dir}")

        # Copy each file
        for file_name in files:
            source_file = os.path.join(root, file_name)
            relative_path = os.path.relpath(source_file, src)
            destination_file = os.path.join(dest, relative_path)

            shutil.copy2(source_file, destination_file)
            print(f"File copied: {source_file} to {destination_file}")


def main():
    if Registry.read("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeQueue", default="0") == "0":
        return

    print("Upgrade service started.")
    print("Removing upgrade queue flag.")
    Registry.write("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeQueue", "0")

    try:
        print("Starting upgrade process.")
        upgradeFile: str = Registry.read("SOFTWARE.CordOS.Boot.VersioningIssue.UpgradeMode")
        upgradeFile = os.path.join(os.getcwd(), upgradeFile)

        print(f"Overwriting files from {upgradeFile} to root directory.")
        cp(upgradeFile, os.getcwd())

        # If posix
        if Host.isHostPOSIX():
            print("Setting bootable.")
            Host.executeCommand("chmod +x boot.sh")

        print(f"Upgrade complete.")

    except Exception as e:
        print(f"Error upgrading system. e: {e}")
        pass

    print("Upgrade service stopped, and will restart.")
    exit(1)

