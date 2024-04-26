import traceback
import kernel.registry as Registry
import kernel.io as IO

def main(args: list):

    try:

        # Remove first index of args if the length is greater than 0
        if len(args) > 0:
            args.pop(0)

        # Check number of arguments
        if len(args) == 2:
            if args[0] == "-d":
                key = args[1]
                var = Registry.read(key)
                if var == None:
                    IO.println(f"Registry key `{key}` does not exist.")
                else:
                    Registry.delete(key)
                    IO.println(f"Registry `{key}` erased.")
            elif args[0] == "-df":
                key = args[1]
                var = Registry.read(key)
                if var == None:
                    IO.println(f"Registry key `{key}` does not exist.")
                else:
                    Registry.delete(key, deleteSubkeys=True)
                    IO.println(f"Registry `{key}` erased.")
            else:
                key = args[0]
                val = args[1]
                var = Registry.read(key)
                Registry.write(key, val)
                IO.println(f"Registry Updated\n`{key}` = `{var}` -> `{val}`")

        elif len(args) == 1:
            key = args[0]
            regType = Registry.isKey(key)
            if regType == 2:
                IO.println(f"Registry value `{key}` is `{Registry.read(key)}`")
            elif regType == 1:
                l = Registry.read(key)
                for i in range(len(l)):
                    if l[i].find("=") != -1:
                        l[i] = "[Val] " + l[i].replace("=", ": ")
                    else:
                        l[i] = "[Key] " + l[i]
                l = "\n".join(l)
                IO.println(f"Registry key `{key}` contains:\n\n```{l}```")
            else:
                IO.println(f"Registry key does not exist.")

        else:
            IO.println(f"Invalid number of arguments. Expected 1 or 2, got {len(args)}")

    except Exception as e:
        if Registry.read("SOFTWARE.CordOS.Kernel.PrintTraceback") == "1": traceback.print_exc()
        IO.println(f"Error in settings. e: {e}")
