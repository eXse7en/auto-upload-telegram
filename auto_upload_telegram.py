import os
import time
import logging
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

# =====================================================
# 1️⃣  Load konfigurasi dari .env
# =====================================================
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./folder_upload")

# =====================================================
# 2️⃣  Logging setup
# =====================================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendDocument"

# =====================================================
# 3️⃣  Helper fungsi
# =====================================================
def wait_until_stable(file_path, interval=1, checks=3):
    """Pastikan file selesai ditulis (ukuran stabil)."""
    stable_count = 0
    last_size = -1
    while stable_count < checks:
        if not os.path.exists(file_path):
            time.sleep(interval)
            continue
        size = os.path.getsize(file_path)
        if size == last_size:
            stable_count += 1
        else:
            stable_count = 0
        last_size = size
        time.sleep(interval)


def notify_fail(file_name):
    """Kirim pesan ke Telegram jika upload gagal total."""
    msg = f"⚠️ Upload *gagal* untuk file `{file_name}` setelah semua percobaan."
    requests.post(
        f"https://api.telegram.org/bot{API_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    )
    logging.error(f"❌ Gagal mengunggah {file_name} setelah semua percobaan.")


def send_to_telegram(file_path, caption=None, max_retries=5, retry_delay=10):
    """Kirim file ke Telegram dengan progress bar tanpa load seluruh file ke RAM."""
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Percobaan upload ke-{attempt} untuk {file_name}")

            with open(file_path, "rb") as f:
                # Siapkan multipart encoder untuk streaming upload
                encoder = MultipartEncoder(
                    fields={
                        "chat_id": str(CHAT_ID),
                        "caption": caption or file_name,
                        "document": (file_name, f, "application/octet-stream"),
                    }
                )

                # Buat progress bar
                with tqdm(
                    total=encoder.len,
                    unit="B", unit_scale=True, unit_divisor=1024,
                    desc=f"Uploading {file_name}"
                ) as progress_bar:

                    # Callback update progress
                    def progress_callback(monitor):
                        progress_bar.update(monitor.bytes_read - progress_bar.n)

                    monitor = MultipartEncoderMonitor(encoder, progress_callback)
                    headers = {"Content-Type": monitor.content_type}

                    # Kirim ke Telegram
                    response = requests.post(
                        TELEGRAM_API_URL,
                        data=monitor,
                        headers=headers,
                        timeout=600
                    )

            # Cek hasil upload
            if response.status_code == 200:
                logging.info(f"✅ File {file_name} berhasil diunggah pada percobaan ke-{attempt}.")
                return True
            else:
                logging.error(f"⚠️ Upload gagal ({response.status_code}): {response.text}")

        except Exception as e:
            logging.error(f"⚠️ Upload error pada percobaan ke-{attempt}: {e}")

        if attempt < max_retries:
            logging.info(f"Menunggu {retry_delay} detik sebelum mencoba lagi...")
            time.sleep(retry_delay)

    # Jika semua percobaan gagal
    notify_fail(file_name)
    return False

# =====================================================
# 4️⃣  Event handler Watchdog
# =====================================================
class FileHandler(FileSystemEventHandler):
    def process_zip(self, file_path):
        file_name = os.path.basename(file_path)
        if not file_name.lower().endswith(".zip"):
            logging.info(f"Melewati file non-zip: {file_name}")
            return

        wait_until_stable(file_path)
        logging.info(f"File {file_name} stabil, mulai upload...")
        send_to_telegram(file_path, caption=f"Backup baru: {file_name}")

    def on_created(self, event):
        if not event.is_directory:
            self.process_zip(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            src = os.path.basename(event.src_path)
            dest = os.path.basename(event.dest_path)
            logging.info(f"File berpindah nama: {src} → {dest}")
            if dest.lower().endswith(".zip"):
                self.process_zip(event.dest_path)

# =====================================================
# 5️⃣  Jalankan observer
# =====================================================
if __name__ == "__main__":
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_DIR, recursive=False)
    observer.start()

    logging.info(f"Bot memantau folder: {UPLOAD_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Dihentikan oleh pengguna.")
    observer.join()


