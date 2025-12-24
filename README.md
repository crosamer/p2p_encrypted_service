> **Project Akhir Sistem Terdistribusi**  
> Mata Kuliah: Sistem Terdistribusi Semester Ganjil 2025  
> Kelas B  
> Mohammad Adzka Crosamer (L0123083)  

# 🔐 Pure P2P Encrypted Messaging Service

Sebuah **aplikasi chatting terenkripsi end-to-end berbasis Peer-to-Peer (P2P)** yang dibuat menggunakan **Python, Flask, dan WebSocket**.  
Proyek ini berfokus pada **konsep Sistem Terdistribusi dan Keamanan & Kriptografi**, tanpa menggunakan server pusat untuk penyimpanan pesan.

Setiap peer berperan sebagai **client dan server secara bersamaan**.

---

## ✨ Fitur Utama

- 🔒 **End-to-End Encryption (E2EE)**
- 🤝 **Arsitektur Pure Peer-to-Peer**
- ⚡ **Realtime Chat (WebSocket)**
- 👥 **Multi-peer / Group Chat**
- 🧩 **Manual Input IP & Port**
- 🛡 **Identity Fingerprint Verification (Anti-MITM)**
- 🔑 **Authenticated Encryption (AES-GCM)**
- 🔁 **Fault Tolerance (Reconnect Otomatis)**
- 💬 **UI Website Chatting Modern**
- 🖥 **Mendukung Localhost & LAN**

---

## 🧠 Arsitektur Sistem

Sistem ini menggunakan **arsitektur P2P murni**, tanpa server pusat:

- Setiap peer menjalankan:
  - Flask Web Server (UI)
  - Socket Listener (P2P Connection)
- Pertukaran pesan dilakukan **langsung antar peer**
- Tidak ada penyimpanan pesan di server pusat




---

## 🔐 Desain Keamanan & Kriptografi

### 🔑 Pertukaran Kunci
- Algoritma: **Elliptic Curve Diffie-Hellman (ECDH)**
- Kurva: `SECP384R1`
- Derivasi kunci menggunakan **HKDF (SHA-256)**

### 🔒 Enkripsi Pesan
- Algoritma: **AES-256-GCM**
- Menyediakan:
  - Kerahasiaan
  - Integritas
  - Autentikasi pesan

### 🛡 Anti Man-In-The-Middle (MITM)
- Setiap peer memiliki **fingerprint public key**
- Fingerprint dapat diverifikasi secara manual

### 🔁 Forward Secrecy
- Kunci sesi dibuat secara dinamis
- Kebocoran kunci jangka panjang tidak membocorkan pesan lama

---

## 🧰 Tech Stack

### Backend
- Python 3
- Flask
- Flask-SocketIO
- Socket TCP

### Kriptografi
- cryptography (Python library)
- ECDH
- HKDF
- AES-GCM

### Frontend
- HTML5
- CSS3
- JavaScript
- Socket.IO Client

---

## 🚀 Instalasi

### 1️⃣ Clone Repository
```bash
git clone https://github.com/username/p2p-encrypted-chat.git
cd p2p-encrypted-chat

pip install flask flask-socketio cryptography


python peer.py
