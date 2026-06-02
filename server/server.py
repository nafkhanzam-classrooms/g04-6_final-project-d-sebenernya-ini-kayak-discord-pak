import socket
import threading
import json
from datetime import datetime
import database

HOST = "0.0.0.0"
PORT = 5000

database.init_db()

clients = {}
rooms = {
    "general": set(),
}

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


def handle_login(data, conn):

    username = data["sender"]

    if username in clients:
        send(conn, {
            "type": "LOGIN_FAILED",
            "message": "Username already taken"
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

    database.log_message(msg_type="public", sender=sender, message=msg, room=room)

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
    
    send(clients[target]["sock"], {
        "type": "MESSAGE",
        "sender": f"[DM] {username}",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    send_system(username, f"DM sent to {target}")

    print(f"[DM] {username} to {target}")

    database.log_message(msg_type="private", sender=username, message=message, target=target, timestamp=timestamp_now)


def handle_broadcast(data, username):

    msg = data["message"].split(" ", 1)

    if len(msg) < 2:
        send_system(username, "Format /bc <message>")
        return
    
    message = msg[1]

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

    database.log_message(msg_type="broadcast", sender=username, message=message, room="ALL", timestamp=timestamp_now)

    

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

def handle_history(data, username):
    limit = data["limit"]
    room = clients[username]["room"]

    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT sender, message, timestamp FROM (
                SELECT sender, message, timestamp, id FROM messages 
                WHERE room = ? AND type = 'public'
                ORDER BY id DESC LIMIT ?
            ) ORDER BY id ASC
        ''', (room, limit))
        
        rows = cursor.fetchall()
        
        chats = []
        for row in rows:
            chats.append({
                "sender": row["sender"],
                "message": row["message"],
                "timestamp": row["timestamp"]
            })
            
        send(clients[username]["sock"], {
            "type": "HISTORY_RESPONSE",
            "chats": chats
        })
        print(f"[HISTORY] Sent {len(chats)} messages to {username} in {room}")
        
    except Exception as e:
        print(f"[SERVER ERROR] Gagal mengambil history: {e}")
        send_system(username, "Gagal memuat history chat.")
    finally:
        conn.close()

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

            if msg["type"] == "LOGIN":
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

            elif msg["type"] == "HISTORY":
                if username:
                    handle_history(msg, username)

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