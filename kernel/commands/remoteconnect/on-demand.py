import socket
import hashlib


def send_message(ip, message) -> (bool, str):
    # Define server address and port
    server_address = (ip, 50000)

    # Create a TCP/IP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            # Connect to the server
            sock.connect(server_address)

            # Send data
            sock.sendall(message.encode())

            # Receive response
            data = sock.recv(1024)
            return True, data.decode()

        except Exception as e:
            print(f"Error: {e}")
            return False, str(e)


def main(args: list):
    args.pop(0)
    if len(args) < 1:
        print("Usage: remoteconnect <username>@<ip> [message raw including authorization header - optional]")
        return

    username, ip = args[0].split("@")

    if len(args) > 1:
        message = args[1]
        success, message = send_message(ip, message)
        if success:
            print(f"{message}")
        else:
            print(f"Internal Error: {message}")
    else:
        message = "NPYOSAUTH_1.0:"
        auth = input("Enter your password: ")
        auth = hashlib.sha256(auth.encode()).hexdigest()
        message += f"{username}:password:{auth}:"
        header = message
        message += "login"
        success, message = send_message(ip, message)
        if success and "NPYOSAUTH_1.0:OK" in message:
            if "NPYOSAUTH_1.0:OK:Warning:" in message:
                print(f"Warning: {message.replace('NPYOSAUTH_1.0:OK:Warning:', '')}")
            print("Authorization successful.")
            print("Type 'exit' to disconnect.")
            while True:
                message = input(f">> (remote) {username}@{ip} >> ")
                if message == "exit":
                    send_message(ip, header + "logout")
                    break
                success, message = send_message(ip, header + message)
                if success:
                    if message.startswith(f"CLOSE:{username}:"):
                        message = message.replace(f"CLOSE:{username}:", "")
                        print(f"{message}")
                        break
                    print(f"{message}")
                else:
                    errList = ["Connection refused", "Connection reset by peer", "Connection timed out", "Internal Error", "Connection closed"]
                    if any(err in message for err in errList):
                        print(f"{message}")
                        break
                    print(f"Error: {message}")
        else:
            print(f"Authorization failed. Error: {message}")
            return


main(input("Start command: ").split(" "))
