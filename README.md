[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/4SHtB1vz)

# Network Programming - Final Project: Let'sChat

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Rifat Qurratu Aini Irwandi               | 5025241233           | D          |
| Mayandra Suhaira Frisiandi               | 5025241240           | D          |

## Video Demo

```
otw
```


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

drop diagram

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
### Menjalankan server

Mulai server:
```
python server/server.py
```

Ouput:
```
[DB] Database & Tabel berhasil diinisialisasi.
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

## Screenshots

### Login


### Create Room


### Private Message


### Chat History

