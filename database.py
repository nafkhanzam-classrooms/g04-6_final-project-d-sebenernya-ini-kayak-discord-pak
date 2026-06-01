import sqlite3
from datetime import datetime

DB_NAME = "fake_dc.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            sender TEXT NOT NULL,
            room TEXT,
            target TEXT,
            message TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database & Tabel berhasil diinisialisasi.")

def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    return user is not None #mengembalikan True jika ketemu, False jika tidak

def log_message(msg_type, sender, message, room=None, target=None, timestamp=None):
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO chat_history (type, sender, room, target, message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (msg_type, sender, room, target, message, timestamp))
        conn.commit()
    except Exception as e:
        print(f"[DB ERROR] Gagal menyimpan log: {e}")
    finally:
        conn.close()