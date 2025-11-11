# 🗂️ Auto Upload Telegram Bot

> 🚀 Sistem otomatis untuk memantau folder backup dan mengirim file `.zip` ke Telegram, lengkap dengan progress bar upload dan auto-restart via systemd.

---

## ✨ Fitur Utama

- 📡 **Monitoring Otomatis** — Deteksi file `.zip` baru di folder target  
- 📤 **Upload ke Telegram** — Kirim file langsung ke chat bot  
- 📊 **Progress Bar Real-Time** — Melihat status upload tanpa full load RAM  
- 🔁 **Auto-Restart & Persisten** — Aktif kembali otomatis setelah reboot  
- 🧩 **Terisolasi di Virtual Environment (venv)**  

---

## ⚙️ Prasyarat

- Python **3.8+**
- Token dan Chat ID dari **Telegram Bot**
- Akses `sudo` (untuk systemd setup)

---

## 🧱 Instalasi

### 1️⃣ Clone & Masuk ke Folder
```bash
git clone https://github.com/eXse7en/auto-upload-telegram.git
cd auto-upload-telegram
```

### 2️⃣ Buat Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests requests_toolbelt tqdm python-dotenv watchdog
deactivate
```
### 3️⃣ Buat Bot Telegram

Buka Telegram
Cari @BotFather
Kirim perintah: /newbot
Ikuti instruksi — nanti kamu dapat token seperti:123456789:ABCDEFghijklmnopqrstuvwxyz

Dapatkan CHAT_ID kamu:
Buka Telegram Web
Cari https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
Kirim pesan ke bot kamu dulu
Lalu buka link itu di browser
Lihat JSON hasilnya → chat: { "id": 123456789 }
👉 Itulah CHAT_ID.

### 4️⃣ Konfigurasi `.env`
Buat file `.env` di root folder:

```env
API_TOKEN=123456789:ABCDEFghijklmnopqrstuvwxyz
CHAT_ID=123456789
UPLOAD_DIR=/var/www/html/sirama/backup (Sesuaikan direktori File kamu)
```

---

## 🐍 Jalankan Manual (opsional)

```bash
source venv/bin/activate
python auto_upload_telegram.py
```

Skrip akan mulai memantau folder `UPLOAD_DIR` dan otomatis mengirim file `.zip` baru ke Telegram.

---

## ⚙️ Setup Otomatis via systemd

Buat file:
```bash
sudo nano /etc/systemd/system/auto_upload_telegram.service
```

Isi dengan:

```ini
[Unit]
Description=Auto Upload Telegram Backup Bot (via venv)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/html/sirama
ExecStart=/var/www/html/sirama/venv/bin/python /var/www/html/sirama/auto_upload_telegram.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/auto_upload_telegram.log
StandardError=append:/var/log/auto_upload_telegram.log

[Install]
WantedBy=multi-user.target
```

Aktifkan service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable auto_upload_telegram.service
sudo systemctl start auto_upload_telegram.service
```

---

## 🧭 Monitoring & Log

Cek status:
```bash
sudo systemctl status auto_upload_telegram.service
```

Pantau log real-time:
```bash
sudo journalctl -u auto_upload_telegram -f
```

Atau lihat file log:
```bash
sudo tail -f /var/log/auto_upload_telegram.log
```

---

## 🧰 Maintenance

| Tugas | Perintah |
|-------|-----------|
| 🔄 Restart service | `sudo systemctl restart auto_upload_telegram` |
| ⏹️ Stop sementara | `sudo systemctl stop auto_upload_telegram` |
| ❌ Hapus service | `sudo systemctl disable auto_upload_telegram && sudo rm /etc/systemd/system/auto_upload_telegram.service && sudo systemctl daemon-reload` |
| 📦 Update library | `source venv/bin/activate && pip install -U requests requests_toolbelt tqdm python-dotenv watchdog && deactivate` |

---

## 🧩 Struktur Folder

```
/var/www/html/sirama/
├── venv/
├── backup/
├── auto_upload_telegram.py
└── .env
```

---

## 💡 Catatan

- Sistem hanya memproses **file `.zip`**
- File dianggap siap diunggah setelah ukuran stabil beberapa detik
- Upload dijalankan **chunked** (hemat RAM)
- Gagal upload akan dikirimkan notifikasi teks ke Telegram

---

## 🪪 Lisensi

MIT License © 2025  
Dikembangkan oleh Tim SiRama internal.

---

## 🤝 Kontribusi

Pull Request dan issue sangat diterima!  
Pastikan kode kamu teruji dan mengikuti standar Pythonic (PEP8).

---

## 📬 Kontak

Untuk pertanyaan atau bantuan teknis, hubungi:
- Tim SiRama
