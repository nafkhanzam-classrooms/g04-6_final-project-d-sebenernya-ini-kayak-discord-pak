import socket
import threading
import os
import base64
import json
import ssl

HOST = "127.0.0.1"
PORT = 5000


def receive(sock):

    buffer = ""

    while True:

        try:
            data = sock.recv(4096)

            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                 
                if not line.strip():
                    continue

                msg = json.loads(line)

                if msg["type"] == "MESSAGE":
                    print(f'\n[{msg["timestamp"]}] {msg["sender"]}: {msg["message"]}')
                    print("> ", end="", flush=True)

                elif msg["type"] == "SYSTEM":
                    print(f"\n[SYSTEM] {msg['message']}")
                    print("> ", end="", flush=True)

                elif msg["type"] == "HISTORY_RESPONSE":
                    print("\n--- CHAT HISTORY ---")
                    for chat in msg["chats"]:
                        print(f"[{chat['timestamp']}] {chat['sender']}: {chat['message']}")
                    print("--------------------")
                    print("> ", end="", flush=True)

                elif msg["type"] == "FILE":
                    filename = msg["filename"]
                    file_data_b64 = msg["file_data"]
                    sender = msg["sender"]

                    if not os.path.exists("downloads"):
                        os.makedirs("downloads")

                    filepath = os.path.join("downloads", filename)

                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(file_data_b64.encode()))

                    print(
                        f"\n[{msg['timestamp']}] [FILE] {sender} sending: '{filename}'"
                    )
                    print(f"[SYSTEM] File received: {filepath}")
                    print("> ", end="", flush=True)

        except:
            break

def send(sock, payload):
    sock.send((json.dumps(payload) + "\n").encode())

def start_client():

    context = ssl.create_default_context()

    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock = context.wrap_socket(
        sock,
        server_hostname=HOST
    )

    sock.connect((HOST, PORT))

    username = input("Username: ")
    password = input("Password: ")

    send(sock, {
        "type": "LOGIN",
        "sender": username,
        "password": password
    })

    data = sock.recv(4096)
    msg = json.loads(data.decode())

    print(f"[SERVER] {msg['message']}")

    if msg["type"] != "LOGIN":
        sock.close()
        return
    
    print(f"[SYSTEM] {msg.get('welcome')}")

    thread = threading.Thread(target=receive, args=(sock,), daemon=True)
    thread.start()

    while True:

        msg = input("> ")

        if msg == "/help":
            print("""
            [SYSTEM COMMANDS]
            /help                   - List system commands
            /users                  - List online users in current room
            /rooms                  - List available rooms
            /create <room>          - Create a new room
            /history <number>       - Show last <number> messages in current room
            /join <room>            - Join an existing room
            /dm <user> <message>    - Sends a private/Direct message
            /file <file_path>       - Sends a file to the current room
            /bc <message>           - Sends a message to all rooms
            /exit or /logout        - Quit the program
                    """)
            continue

        if msg in ["/exit", "/logout"]:
            send(sock, {
                "type": "LOGOUT",
                "sender": username
            })

            sock.close()
            print("[SYSTEM] Disconnected from server")
            break

        if msg == "/users":
            send(sock, {
                "type": "USERS",
                "sender": username
            })
            continue


        if msg == "/rooms":
            send(sock, {
                "type": "ROOMS",
                "sender": username
            })
            continue


        if msg.startswith("/dm "):
            send(sock,{
                "type": "DM",
                "sender": username,
                "message": msg
            })
            continue


        if msg.startswith("/bc "):
            send(sock, {
                "type": "BC",
                "sender": username,
                "message": msg
            })
            continue

        if msg.startswith("/create "):
            room = msg.split(" ", 1)[1]

            send(sock, {
                "type": "CREATE_ROOM",
                "sender": username,
                "room": room
            })
            continue

        if msg.startswith("/history "):
            try:
                limit = int(msg.split(" ", 1)[1].strip())
                
                send(sock, {
                    "type": "HISTORY",
                    "sender": username,
                    "limit": limit
                })
            except ValueError:
                print("[SYSTEM] Failed!")
            continue

        if msg.startswith("/file "):
            filepath = msg.split(" ", 1)[1].strip()

            if not os.path.exists(filepath):
                print(f"[SYSTEM] File '{filepath}' Not Found!")
                continue

            try:
                filename = os.path.basename(filepath)
                with open(filepath, "rb") as f:
                    file_data_b64 = base64.b64encode(f.read()).decode()

                payload = {
                    "type": "FILE",
                    "sender": username,
                    "filename": filename,
                    "file_data": file_data_b64,
                    "room": "",
                    "timestamp": "",
                }

                packet = json.dumps(payload) + "\n"
                sock.sendall(packet.encode())

                print(f"[SYSTEM] File '{filename}' Sent.")
            except Exception as e:
                print(f"[SYSTEM] Failed to read/send file: {e}")
            continue

        if msg.startswith("/join "):
            room = msg.split(" ", 1)[1]

            send(sock, {
                "type": "JOIN_ROOM",
                "sender": username,
                "room": room
            })
            continue

        send(sock, {
            "type": "MESSAGE",
            "sender": username,
            "message": msg,
            "room": "",
            "timestamp": ""

        })



if __name__ == "__main__":
    start_client()