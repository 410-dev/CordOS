import kernel.ipc as IPC
import kernel.registry as Registry
import kernel.journaling as Journaling
import kernel.io as IO

import kernel.services.SystemUI.Authorization as Authorization
import kernel.services.SystemUI.execute as Launcher

import socket
import time
import random
import string

from kernel.drivers.IOCaptureDevice import IOCaptureDevice

def main():

    port = Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.RemoteServices.RemoteSystemUI.ListenPort", default=50000)
    port = int(port)
    allowedIPs: list = Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.RemoteServices.RemoteSystemUI.ListenAddress", default="127.0.0.1,").split(",")
    excludeInternalConnectionLimit = Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.RemoteServices.RemoteSystemUI.ExcludeInternalFromMaxConnections", default="1") == "1"
    excludeInternalTimeout = Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.RemoteServices.RemoteSystemUI.ExcludeInternalTimeout", default="1") == "1"
    timeout = Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.RemoteServices.RemoteSystemUI.DropConnectionTimeout", default=300)
    timeout = int(timeout) # seconds
    maxConnections = Registry.read("SOFTWARE.NanoPyOS.Kernel.Services.RemoteServices.RemoteSystemUI.MaxConnections", default=2)
    maxConnections = int(maxConnections)

    # Open a socket to listen for incoming connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if len(allowedIPs) > 1:
        server.bind(("0.0.0.0", port))
    else:
        server.bind((allowedIPs[0], port))
    server.listen(maxConnections)

    Journaling.record("INFO", f"Listening on {allowedIPs}:{port} with a maximum of {maxConnections} connections.")
    IO.println(f"Listening on {allowedIPs}:{port} with a maximum of {maxConnections} connections.")

    connections = [
        # {
        #     "address": "127.0.0.1",
        #     "lastConnection": 0,
        #     "internal": True,
        #     "username": "Administrator"
        # }
    ]

    IPC.set("remotesystemui.publisher.id", ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)))
    IPC.set("remotesystemui.publisher.auth", ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)))

    def getConnection(username: str, address: str):
        for connection in connections:
            # Check last connection time. If it is greater than the timeout, remove the connection
            timeDiff = time.time() - connection["lastConnection"]
            if timeDiff > timeout:
                if connection["internal"] and excludeInternalTimeout:
                    pass
                else:
                    connections.remove(connection)
                    Journaling.record("INFO", f"Removed connection from {address} due to timeout")

            else:
                connection["lastConnection"] = int(time.time())
                Journaling.record("INFO", f"Updated connection from {address}")

            if connection["address"] == address and connection["username"] == username:
                return connection
        return None

    def loop():
        try:
            client, address = server.accept()
            Journaling.record("INFO", f"Connection from {address}")

            # Check if connection is listening
            connectionIP = address[0]
            if connectionIP not in allowedIPs:
                Journaling.record("WARNING", f"Unauthorized connection from {address}")
                return

            with client:  # Ensures the client socket is closed properly
                data = client.recv(1024)
                responseData = ""
                if not data:
                    return

                stringVar = data.decode("utf-8")
                Journaling.record("INFO", f"Received: {stringVar}")

                # Format of authorization string
                # NPYOSAUTH_1.0:<username>:<capability>:<authmethod>:<authdata>:<data>
                # Example authorization string
                # NPYOSAUTH_1.0:admin:free:_:echo hello
                # NPYOSAUTH_1.0:admin:password:54c5b3dd459d5ef778bb2fa1e23a5fb0e1b62ae66970bcb436e8f81a1a1a8e41:echo hello

                version = stringVar.split(":")[0]
                if version != "NPYOSAUTH_1.0":
                    Journaling.record("WARNING", f"Invalid authorization version from {address}: {version}")
                    client.sendall("Invalid data header.".encode("utf-8"))
                    return

                username = stringVar.split(":")[1]
                authmethod = stringVar.split(":")[2]
                authdata = stringVar.split(":")[3]
                data = stringVar.split(":")[4:]
                data = ":".join(data)

                ipcPublisher: bool = (username == IPC.read("remotesystemui.publisher.id") and authdata == IPC.read("remotesystemui.publisher.auth"))

                # Data header is always authorization
                Journaling.record("INFO", f"Checking authorization from {address} as {username} with method {authmethod}")
                if not Authorization.authorize("login.remote", authmethod, username, authdata, encodeDataToSHA256=False) and not ipcPublisher:
                    Journaling.record("WARNING", f"Unauthorized access from {address}")
                    responseData = "Unauthorized access - Invalid credentials."
                # If data is "login", add the connection
                elif data == "login":
                    Journaling.record("INFO", f"Authorized access from {address} as {username} with method {authmethod}")
                    # Check if the connection is internal
                    internal = False
                    if address[0] == "127.0.0.1":
                        internal = True

                    # Check if the connection is already in the list
                    found = getConnection(username, address[0]) is not None

                    # If not found, construct connection object
                    if not found:
                        if (len(connections) >= maxConnections) and not (internal and excludeInternalConnectionLimit):
                            Journaling.record("WARNING", f"Connection limit reached from {address} as {username}")
                            responseData = "Connection limit reached."

                        else:
                            connection = {
                                "address": address[0],
                                "lastConnection": 0,
                                "internal": internal,
                                "username": username
                            }
                            connections.append(connection)
                            Journaling.record("INFO", f"Login success: Added connection from {address} as {username}")
                            responseData = "NPYOSAUTH_1.0:OK"
                    else:
                        Journaling.record("WARNING", f"Connection already exists from {address} as {username}")
                        responseData = "NPYOSAUTH_1.0:OK:Warning: Connection already exists."

                # If data is "logout", remove the connection
                elif data == "logout":
                    Journaling.record("INFO", f"Authorized access from {address} as {username} with method {authmethod}")
                    # Check if the connection is in the list
                    connectionObject = getConnection(username, address[0])
                    if connectionObject is not None:
                        connections.remove(connectionObject)
                        Journaling.record("INFO", f"Logout success: Removed connection from {address} of {username}")
                        responseData = f"CLOSE:{username}:Logout success and connection removed."
                    else:
                        Journaling.record("WARNING", f"Connection not found from {address} of {username}")
                        responseData = "Unauthorized access - connection session not found."

                # If data is "terminate", terminate the socket and close the connection
                elif data == "terminate":
                    Journaling.record("INFO", f"Authorized access from {address} as {username} with method {authmethod}")
                    client.sendall(f"CLOSE:{username}:Terminating connection.".encode("utf-8"))
                    Journaling.record("INFO", f"Terminating connection from {address} of {username}")
                    IPC.set("remotesystemui.shutdown", True)
                    return

                # Otherwise, check for connection.
                else:
                    Journaling.record("INFO",  f"Authorized access from {address} as {username} with method {authmethod}")
                    connectionObject = getConnection(username, address[0])
                    if connectionObject is None:
                        Journaling.record("WARNING", f"Connection not found from {address} of {username}")
                        responseData = "Unauthorized access - connection session not found."
                    else:
                        # Execute the command
                        Journaling.record("INFO", f"Command executed from {address} as {username}: {data}")

                        outputCaptureDevice = IOCaptureDevice()

                        IO.setOutput(outputCaptureDevice.capture_output)
                        Launcher.run(data)

                        outputData = outputCaptureDevice.getOutputAsString()
                        IO.restoreOutput()
                        Journaling.record("INFO", f"Execution success. Output: {outputData}")
                        responseData = outputData

                client.sendall(responseData.encode("utf-8"))
                Journaling.record("INFO", f"Sent: {responseData}")

        except Exception as e:
            Journaling.record("ERROR", f"An error occurred: {e}")

    # Assuming IPC.repeatUntilShutdown handles the loop and server shutdown properly
    IPC.repeatUntilShutdown(0.05, loop, terminateIfAnyOf=[("power.off", True), ("remotesystemui.shutdown", True)])

