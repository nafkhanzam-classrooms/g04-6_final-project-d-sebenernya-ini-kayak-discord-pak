import socket
import threading
import json
from datetime import datetime
import database

HOST = "0.0.0.0"
PORT = 5000

clients = {}
rooms = {
    "general": set(),
}

# Inisialisasi database
database.init_db()

def send(sock, data):

    try:
        sock.send(json.dumps(data).encode())
    except:
        pass


def send_system(username, message):

    send(clients[username]["sock"], {
        "type": "SYSTEM",
        "message": message
    })


def handle_register(data, conn):
    username = data["username"]
    password = data.get("password", "")

    if not username or not password:
        send(conn, {
            "type": "REGISTER_FAILED",
            "message": "Username and password required"
        })
        return False

    # Register ke database
    if database.register_user(username, password):
        send(conn, {
            "type": "REGISTER_SUCCESS",
            "message": "Registration successful, please login"
        })
        print(f"[REGISTER] {username} registered")
        return True
    else:
        send(conn, {
            "type": "REGISTER_FAILED",
            "message": "Username already exists"
        })
        print(f"[REGISTER FAILED] {username} already exists")
        return False


def handle_login(data, conn):

    username = data["sender"]
    password = data.get("password", "")

    # Verifikasi user dari database
    if not database.verify_user(username, password):
        send(conn, {
            "type": "LOGIN_FAILED",
            "message": "Invalid username or password"
        })
        conn.close()
        return None

    if username in clients:
        send(conn, {
            "type": "LOGIN_FAILED",
            "message": "Username already online"
        })
        conn.close()
        return None
    
    rooms.setdefault("general", set())
    
    clients[username] = {
        "sock": conn,
        "room": "general"
    }

    rooms["general"].add(username)

    send(conn, {
        "type": "LOGIN",
        "message": "Login successful",
        "welcome": f"Welcome {username}, Type /help for commands"
    })

    print(f"[LOGIN] {username}")
    return username


def handle_message(data):

    sender = data["sender"]
    msg = data["message"]

    room = clients[sender]["room"]

    payload = {
        "type": "MESSAGE",
        "sender": sender,
        "message": msg,
        "room": room,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    }

    print(f"[MSG] [ {room} | {payload['timestamp']}] {sender}: {msg}")

    # Log pesan ke database
    database.log_message("MESSAGE", sender, msg, room=room, timestamp=payload['timestamp'])

    for user in rooms.get(room, []):
        send(clients[user]["sock"], payload)


def handle_logout(username):

    if username not in clients:
        return

    room = clients[username]["room"]

    if room in rooms:
        rooms[room].discard(username)

    del clients[username]

    print(f"[LOGOUT] {username}")


def handle_users(username):

    room = clients[username]["room"]

    users = list(rooms.get(room, []))

    user_list = ", ".join(users) if users else "empty"

    send_system(username, f"Users in {room}: {user_list}")


def handle_rooms(username):
    room_list = list(rooms.keys())

    send_system(username, f"Rooms: {', '.join(room_list)}")


def handle_dm(data, username): #Private Message/Direct Message

    parts = data["message"].split(" ", 2)

    if len(parts) < 3:
        send_system(username, "Format: /dm <user> <message>")
        return
    
    target, message = parts[1], parts[2]

    if target not in clients:
        send_system(username, "User not found")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    send(clients[target]["sock"], {
        "type": "MESSAGE",
        "sender": f"[DM] {username}",
        "message": message,
        "timestamp": timestamp
    })

    # Log DM ke database
    database.log_message("DM", username, message, target=target, timestamp=timestamp)

    send_system(username, f"DM sent to {target}")

    print(f"[DM] {username} to {target}")


def handle_broadcast(data, username):

    msg = data["message"].split(" ", 1)

    if len(msg) < 2:
        send_system(username, "Format /bc <message>")
        return
    
    message = msg[1]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log broadcast ke database
    database.log_message("BROADCAST", username, message, timestamp=timestamp)

    payload = {
        "type": "MESSAGE",
        "sender": f"[BC] {username}",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    for user, info in list(clients.items()):
        try:
            send(info["sock"], payload)
            print(f"[BC] {username}: {message}")
        except:
            del clients[user]

    

def handle_create_room(data, username):
    
    room = data["room"]

    if room in rooms:
        send_system(username, "Room already exists")
        return
    
    rooms[room] = set()

    send_system(username, f"{room} room created")

    print(f"[ROOM CREATED] {room}")


def handle_join_room(data, username):

    new_room = data["room"]
    old_room = clients[username]["room"]

    if old_room in rooms:
        rooms[old_room].discard(username)

    if new_room not in rooms:
        send_system(username, "Room not found, use /rooms to see list of rooms")
        return

    rooms[new_room].add(username)
    clients[username]["room"] = new_room

    send_system(username, f"Joined {new_room} room")

    print(f"[ROOM] {username}: Moved from {old_room} room to {new_room} room")


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")

    username = None

    while True:
        try:
            data = conn.recv(4096)

            if not data:
                print(f"[EMPTY] {addr}")
                break

            try: 
                msg = json.loads(data.decode())

            except json.JSONDecodeError:
                print(f"[BAD JSON] {addr}")
                continue    

            if msg["type"] == "REGISTER":
                handle_register(msg, conn)

            elif msg["type"] == "LOGIN":
                username = handle_login(msg, conn)

                if username == None:
                    print("[LOGIN FAILED]")
                    break

            elif msg["type"] == "MESSAGE":
                if username:
                    handle_message(msg)

            elif msg["type"] == "CREATE_ROOM":
                handle_create_room(msg, username)

            elif msg["type"] == "JOIN_ROOM":
                handle_join_room(msg, username)

            elif msg["type"] == "USERS":
                handle_users(username)

            elif msg["type"] == "ROOMS":
                handle_rooms(username)

            elif msg["type"] == "DM":
                handle_dm(msg, username)

            elif msg["type"] == "BC":
                handle_broadcast(msg, username)

            elif msg["type"] == "LOGOUT":
                handle_logout(username)
                break

        except Exception as e:
            print(f"[ERROR] {addr} -> {e}")
            break

    if username and username in clients:
        room = clients[username]["room"]

        if room in rooms:
            rooms[room].discard(username)

        del clients[username]

    conn.close()
    print(f"[DISCONNECTED] {addr}")


def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[LISTENING] {HOST}:{PORT}")

    while True:

        conn, addr = server.accept()

        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)

        thread.start()


if __name__ == "__main__":
    start_server()