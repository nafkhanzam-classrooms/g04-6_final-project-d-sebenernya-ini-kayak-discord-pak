import sqlite3
from datetime import datetime

DB_NAME = "fake_dc.db"

def get_db_connection():
    """
    Membuat koneksi ke database.
    check_same_thread=False mengizinkan SQLite digunakan di aplikasi multithread.
    """
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Agar hasil query bisa diakses seperti dictionary
    return conn

def init_db():
    """Membuat tabel jika belum ada."""
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
    
    conn.commit()
    conn.close()
    print("[DB] Database & Tabel berhasil diinisialisasi.")

def log_message(msg_type, sender, message, room=None, target=None, timestamp=None):
    """Fungsi universal untuk mencatat segala jenis pesan ke database."""
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