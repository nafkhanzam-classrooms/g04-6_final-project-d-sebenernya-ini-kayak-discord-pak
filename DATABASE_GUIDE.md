# 📚 Database Usage Guide

## Overview
Sistem ini menggunakan **SQLite** untuk:
- ✅ Autentikasi user (register & login)
- ✅ Menyimpan history chat di room
- ✅ Menyimpan Direct Messages (DM)
- ✅ Menyimpan Broadcast messages

Database file: `fake_dc.db`

---

## 📋 Database Structure

### Tabel 1: `users` (untuk autentikasi)
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
```

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `username` | TEXT | Username (Primary Key) |
| `password` | TEXT | Password (belum di-hash, bisa dikembangkan) |

**Contoh:**
```
username: "alice"
password: "pass123"
```

### Tabel 2: `chat_history` (untuk menyimpan semua pesan)
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    sender TEXT NOT NULL,
    room TEXT,
    target TEXT,
    message TEXT,
    timestamp TEXT NOT NULL
)
```

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | INTEGER | Auto-increment ID |
| `type` | TEXT | Tipe pesan: "MESSAGE", "DM", "BROADCAST" |
| `sender` | TEXT | Username pengirim |
| `room` | TEXT | Nama room (hanya untuk MESSAGE) |
| `target` | TEXT | Username target (hanya untuk DM) |
| `message` | TEXT | Isi pesan |
| `timestamp` | TEXT | Waktu pesan (format: YYYY-MM-DD HH:MM:SS) |

**Contoh data:**
```
id=1, type="MESSAGE", sender="alice", room="general", message="Halo semua", timestamp="2024-06-02 10:30:45"
id=2, type="DM", sender="alice", target="bob", message="Apa kabar?", timestamp="2024-06-02 10:31:20"
id=3, type="BROADCAST", sender="alice", message="Pengumuman penting", timestamp="2024-06-02 10:32:00"
```

---

## 🔧 Fungsi-fungsi Database

### 1. `init_db()`
Inisialisasi database dan membuat tabel jika belum ada.

```python
from database import init_db

init_db()  # Jalankan sekali saat server start
```

**Server otomatis memanggil ini di awal startup.**

---

### 2. `register_user(username, password)`
Register user baru ke database.

```python
from database import register_user

# Success: return True
result = register_user("alice", "pass123")

# Failed (username sudah ada): return False
result = register_user("alice", "pass456")
```

---

### 3. `verify_user(username, password)`
Verifikasi username & password (untuk login).

```python
from database import verify_user

# Success (credentials benar): return True
is_valid = verify_user("alice", "pass123")

# Failed (password salah): return False
is_valid = verify_user("alice", "wrong_password")
```

---

### 4. `log_message(msg_type, sender, message, room=None, target=None, timestamp=None)`
Menyimpan pesan ke database.

```python
from database import log_message
from datetime import datetime

# Menyimpan MESSAGE di room
log_message(
    msg_type="MESSAGE",
    sender="alice",
    message="Halo semua",
    room="general",
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)

# Menyimpan DM
log_message(
    msg_type="DM",
    sender="alice",
    message="Apa kabar?",
    target="bob",
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)

# Menyimpan BROADCAST
log_message(
    msg_type="BROADCAST",
    sender="alice",
    message="Pengumuman penting",
    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)
```

---

### 5. `get_room_history(room_name, limit=20)`
Mengambil history chat dari room tertentu.

```python
from database import get_room_history

# Ambil 20 pesan terakhir dari room "general"
history = get_room_history("general", limit=20)

# Output: List of dict
# [
#   {"type": "MESSAGE", "sender": "alice", "message": "Halo", "timestamp": "2024-06-02 10:30:45"},
#   {"type": "MESSAGE", "sender": "bob", "message": "Halo juga", "timestamp": "2024-06-02 10:31:00"},
#   ...
# ]

for msg in history:
    print(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}")
```

---

### 6. `get_dm_history(user1, user2, limit=20)`
Mengambil history DM antara dua user.

```python
from database import get_dm_history

# Ambil DM antara alice dan bob
history = get_dm_history("alice", "bob", limit=20)

# Output: List of dict (urutan kronologis)
# [
#   {"type": "DM", "sender": "alice", "message": "Halo", "timestamp": "2024-06-02 10:30:45"},
#   {"type": "DM", "sender": "bob", "message": "Halo juga", "timestamp": "2024-06-02 10:31:00"},
#   ...
# ]

for msg in history:
    print(f"[{msg['timestamp']}] {msg['sender']}: {msg['message']}")
```

---

## 🔄 Flow Integrasi di Server

### Register Flow
```
Client: {type: "REGISTER", username: "alice", password: "pass123"}
  ↓
Server: handle_register() → database.register_user()
  ↓
Server: Send REGISTER_SUCCESS atau REGISTER_FAILED
```

### Login Flow
```
Client: {type: "LOGIN", sender: "alice", password: "pass123"}
  ↓
Server: handle_login() → database.verify_user()
  ↓
Server: Send LOGIN success atau LOGIN_FAILED
```

### Message Flow
```
Client: {type: "MESSAGE", sender: "alice", message: "Halo"}
  ↓
Server: handle_message() → database.log_message()
  ↓
Server: Broadcast ke semua user di room + print log
```

---

## 💾 Database Examples

### Tampilkan semua user:
```python
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(user)
conn.close()
```

### Tampilkan semua chat di room "general":
```python
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT sender, message, timestamp FROM chat_history 
    WHERE type='MESSAGE' AND room='general' 
    ORDER BY timestamp DESC LIMIT 10
""")
messages = cursor.fetchall()
for msg in messages:
    print(msg)
conn.close()
```

### Delete history tertentu:
```python
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM chat_history WHERE room='general'")
conn.commit()
conn.close()
```

---

## ⚠️ Catatan Penting

1. **Password belum di-hash** → Untuk produksi, gunakan bcrypt atau argon2
2. **SQLite single-threaded** → Sudah pakai `check_same_thread=False` tapi tetap hati-hati dengan race conditions
3. **Database auto-create** → Jika `fake_dc.db` tidak ada, akan dibuat otomatis
4. **Timestamp format** → Selalu gunakan format `"%Y-%m-%d %H:%M:%S"`

---

## 🚀 Testing Database

Jalankan script ini untuk test database:

```python
from database import *

# Init DB
init_db()

# Test Register
print("=== Test Register ===")
print(register_user("alice", "pass123"))  # True
print(register_user("bob", "pass456"))    # True
print(register_user("alice", "pass789"))  # False (sudah ada)

# Test Login
print("\n=== Test Login ===")
print(verify_user("alice", "pass123"))    # True
print(verify_user("alice", "wrong"))      # False

# Test Log Message
print("\n=== Test Log Message ===")
log_message("MESSAGE", "alice", "Halo semua", room="general")
log_message("DM", "alice", "Halo bob", target="bob")
log_message("BROADCAST", "alice", "Pengumuman")

# Test Get History
print("\n=== Test Get Room History ===")
room_history = get_room_history("general")
for msg in room_history:
    print(msg)

print("\n=== Test Get DM History ===")
dm_history = get_dm_history("alice", "bob")
for msg in dm_history:
    print(msg)
```

---

Semua sudah siap digunakan! 🎉
