import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 5000


def receive(sock):

    while True:

        try:
            data = sock.recv(4096)

            if not data:
                break

            msg = json.loads(data.decode())

            if msg["type"] == "MESSAGE":
                print(f'\n[{msg["timestamp"]}] {msg["sender"]}: {msg["message"]}')
                print("> ", end="", flush=True)

            if msg["type"] == "SYSTEM":
                print(f"\n[SYSTEM] {msg['message']}")
                print("> ", end="", flush=True)

        except:
            break


def start_client():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    username = input("Username: ")

    sock.send(json.dumps({
        "type": "LOGIN",
        "sender": username

    }).encode())

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
            /join <room>            - Join an existing room
            /dm <user> <message>    - Sends a private/Direct message
            /bc <message>           - Sends a message to all rooms
            /exit or /logout        - Quit the program
                    """)
            continue

        if msg in ["/exit", "/logout"]:
            sock.send(json.dumps({
                "type": "LOGOUT",
                "sender": username
            }).encode())

            sock.close()
            print("[SYSTEM] Disconnected from server")
            break

        if msg == "/users":
            sock.send(json.dumps({
                "type": "USERS",
                "sender": username
            }).encode())
            continue


        if msg == "/rooms":
            sock.send(json.dumps({
                "type": "ROOMS",
                "sender": username
            }).encode())
            continue


        if msg.startswith("/dm "):
            sock.send(json.dumps({
                "type": "DM",
                "sender": username,
                "message": msg
            }).encode())
            continue


        if msg.startswith("/bc "):
            sock.send(json.dumps({
                "type": "BC",
                "sender": username,
                "message": msg
            }).encode())
            continue

        if msg.startswith("/create "):
            room = msg.split(" ", 1)[1]

            sock.send(json.dumps({
                "type": "CREATE_ROOM",
                "sender": username,
                "room": room
            }).encode())
            continue

        if msg.startswith("/join "):
            room = msg.split(" ", 1)[1]

            sock.send(json.dumps({
                "type": "JOIN_ROOM",
                "sender": username,
                "room": room
            }).encode())
            continue

        sock.send(json.dumps({
            "type": "MESSAGE",
            "sender": username,
            "message": msg,
            "room": "",
            "timestamp": ""

        }).encode())



if __name__ == "__main__":
    start_client()