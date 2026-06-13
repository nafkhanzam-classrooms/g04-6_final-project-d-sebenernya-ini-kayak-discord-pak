[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4SHtB1vz)

# Network Programming - Final Project: Let'sChat

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Rifat Qurratu Aini Irwandi               | 5025241233           | D          |
| Mayandra Suhaira Frisiandi               | 5025241240           | D          |

## Video Demo

```
https://youtu.be/aiQi-zqvHlc
```
## Daftar Isi

- [Deskripsi Singkat](#deskripsi-singkat)
- [Fitur-Fitur](#fitur-fitur)
- [Materi yang Diterapkan](#materi-yang-diterapkan)
- [Struktur Project](#struktur-project)
- [Arsitektur](#arsitektur)
- [Enskripsi TLS](#enskripsi-tls)
- [Akun Default](#akun-default)
- [Instalasi](#instalasi)
- [Commands yang Tersedia](#commands-yang-tersedia)
- [Serialisasi Pesan](#serialisasi-pesan)
- [Screenshots](#screenshots)

## Deskripsi Singkat

Let'sChat adalah aplikasi Multi-Chat Rooms berbasis Command Line Interface (CLI) yang dibangun menggunakan Python, TCP Socket, Multithreading, JSON Serialization, dan SQLite Database.

Aplikasi ini menerapkan arsitektur client-server sehingga banyak pengguna dapat terhubung ke server secara bersamaan dan berkomunikasi dalam room chat yang tersedia.

## Fitur-Fitur

- User Authentication
- Multi Chat Rooms
- Create Room
- Join Room
- Online User List
- Room List
- Broadcast Message
- Private Message (Direct Message)
- Chat History
- Message Timestamp
- Server Logging
- JSON Serialization
- SQLite Database Storage
- Multithreaded Server

## Materi yang Diterapkan

| Materi    | Implementasi |
| ---       | --- |
| Konsep client-server | Server menangani koneksi dan komunikasi dari banyak client |
| Protokol application layer | Command seperti `/join`, `/dm`, `/bc`, dan `/history` dirancang pada application layer |
| Perancangan protokol komunikasi aplikasi | Pesan menggunakan format JSON dengan field seperti `type`, `sender`, dan `message` |
| Parsing dan format data jaringan | Menggunakan `json.dumps()` dan `json.loads()` |
| TCP socket programming | Komunikasi menggunakan TCP Socket (`SOCK_STREAM`) |
| Multithreading dan concurrency | Setiap client ditangani oleh thread yang berbeda |
| Pengujian dan simulasi beban server | Dilakukan dengan menjalankan beberapa client secara bersamaan |

## Struktur Project

```
├── server/
│   ├── server.py
│   └── database.py
├── client/
│   └── client.py
└── README.md
```

Deskripsi File
| File          | Deskripsi                         |
| ---           | ---                               |
| server.py     | Aplikasi Server                   |
| client.py     | Aplikasi client berbasis terminal |
| database.py   | Inisialisasi database dan utilitas |

SQLite database `fake_dc.db` akan dibuat secara otomatis saat server pertama kali dijalankan.

## Arsitektur

<img width="601" height="181" alt="letschatarchi" src="https://github.com/user-attachments/assets/01c35997-bc0a-41d1-a0d0-1f5034d7d4e0" />

## Enskripsi TLS

Aplikasi ini menggunakan TLS (Transport Layer Security) untuk mengenkripsi komunikasi antara client dan server.

Server menggunakan SSL context:
```
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
```

Client menggunakan secure socket:
```
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
sock = context.wrap_socket(sock, server_hostname=HOST)
```

Fungsi TLS dalam aplikasi ini:
- Mengenkripsi seluruh komunikasi TCP
- Mencegah packet sniffing (data tidak bisa dibaca saat ditangkap)
- Melindungi login credentials (username & password)
- Mengamankan file transfer dan chat messages

## Akun Default

Aplikasi tidak menyediakan fitur registrasi akun. Seluruh akun disimpan secara manual pada database SQLite.
| Username  | Password  |
| ---       | ---       |
| ami       | 123       |
| andra     | 123       |
| ara       | 555       |

## Instalasi

Clone repository:
```
git clone https://github.com/nafkhanzam-classrooms/g04-6_final-project-d-sebenernya-ini-kayak-discord-pak
cd g04-6_final-project-d-sebenernya-ini-kayak-discord-pak
```
Pastikan python sudah terinstalasi:
```
python --version
```
Generate sertifikasi SSL:
```
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
```
Saat diminta input:
- Country / State / etc → bebas (boleh ENTER saja)

File yang dihasilkan:
- server.key (private key)
- server.crt (certificate)

Letakkan file ini di `/server`, karena server akan memanggil:
```
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
```

### Menjalankan server

Mulai server:
```
python server/server.py
```

Ouput:
```
[DB] Database initialized.
[LISTENING] 0.0.0.0:5000
```

Saat server dijalankan pertama kali, aplikasi akan otomatis:

- Membuat database SQLite
- Membuat tabel users
- Membuat tabel messages
- Menambahkan akun default

### Menjalankan Client

Mulai client:
```
python client/client.py
```
Login menggunakan salah satu akun pada [Akun Default](#akun-default).

## Commands yang Tersedia

| Command               | Deskripsi                                             |
| ---                   | ---                                                   |
| /help                 | Menampilkan daftar command                            |
| /users                | Menampilkan pengguna pada room saat ini               |
| /rooms                | Menampilkan daftar room yang tersedia                 |
| /create <room>        | Membuat room baru                                     |  
| /join <room>          | Bergabung ke room tertentu                            |
| /history <jumlah>     | Menampilkan sejumlah pesan terakhir dari room aktif   |
| /file <file path>     | Mengirim File                                         |
| /dm <user> <message>  | Mengirim private message                              |
| /bc <message>         | Mengirim broadcast message ke seluruh pengguna online |
| /logout               | Keluar dari aplikasi                                  |
| /exit                 | Keluar dari aplikasi                                  |

### Perilaku Room

- Semua pengguna memasuki room `general` setelah login.
- Satu pengguna hanya dapat berada dalam 1 room dalam satu waktu.
- Menggunakan `/join <room>` membuat pengguna meninggalkan room lama.
- Pesan hanya muncul jika pengguna berada dalam ruangan yang sama

### Serialisasi Pesan

Komunikasi antara server dan client menggunakan serialisasi JSON
Contoh request login:
```
{
    "type": "LOGIN",
    "sender": "ami",
    "password": "123" 
}
```

contoh pesan:
```
{ 
    "type": "MESSAGE", 
    "sender": "ami", 
    "message": "Hello everyone" 
}
```
### Riwayat pesan

Pesan-pesan disimpan dalam database SQLite.
Gunakan:
```
/history <number>
```
Contoh:
```
/history 10
```

Command ini akan menampilkan 10 pesan terbaru dari room yang sedang ditempati pengguna.

### Bertukar file

Gunakan:
```
/file <file_path>
```
Contoh:
```
/file ../README.md
```
## Screenshots

### Login
<img width="313" height="173" alt="Screenshot 2026-06-05 164352" src="https://github.com/user-attachments/assets/0901eacf-1003-42fa-8850-e79930b9ab5d" />

### Create Room
<img width="267" height="145" alt="Screenshot 2026-06-05 164445" src="https://github.com/user-attachments/assets/1ad4dfda-7c84-4157-8d44-abad8ed94378" />

### Private Message
<img width="819" height="333" alt="image" src="https://github.com/user-attachments/assets/6cd6ad29-b00b-485b-b236-2315518be9c3" />

### Chat History
<img width="508" height="370" alt="image" src="https://github.com/user-attachments/assets/6dd2a098-dc4a-4b39-a076-37792c6bf958" />

### File Transfer
<img width="1463" height="288" alt="image" src="https://github.com/user-attachments/assets/832303fd-354f-4472-9e97-4b30814211b3" />
<img width="206" height="107" alt="image" src="https://github.com/user-attachments/assets/05a01149-38a8-41ee-9f8a-dc4876afcb83" />
