import os
import time
import platform
import requests
from tqdm import tqdm
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
import subprocess

# ============ CONFIGURATION =============
SERVER_URL = "http://192.168.0.194:8000"  # <-- Replace this
DEVICE_NAME = f"{platform.system().lower()}-{platform.node()}"
CHECK_INTERVAL = 2  # seconds
DOWNLOAD_DIR = os.path.expanduser("~/ClipboardDownloads")

# Create download dir if missing
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Track last events
last_clipboard = ""
last_received = ""

# OS-based clipboard
def get_clipboard():
    system = platform.system()
    try:
        if system == "Windows":
            import win32clipboard
            import win32con
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                    data = win32clipboard.GetClipboardData()
                    return data.strip()
                elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
                    return win32clipboard.GetClipboardData(win32con.CF_HDROP)[0]
            finally:
                win32clipboard.CloseClipboard()

        elif system == "Darwin":
            return subprocess.check_output("pbpaste", text=True).strip()

        elif system == "Linux":
            return subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True).strip()

    except Exception as e:
        print("Clipboard read error:", e)
    return ""

def set_clipboard(text):
    system = platform.system()
    try:
        if system == "Windows":
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
        elif system == "Darwin":
            subprocess.run("pbcopy", input=text, text=True)
        elif system == "Linux":
            subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True)
    except Exception as e:
        print("Clipboard write error:", e)

# ================= FILE UPLOAD ==================
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm
import time

def upload_file(filepath):
    try:
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        url = f"{SERVER_URL}/upload"

        with open(filepath, 'rb') as f:
            encoder = MultipartEncoder(fields={'file': (filename, f, 'application/octet-stream')})
            progress_bar = tqdm(
                total=encoder.len,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f"->> Uploading {filename}",
                dynamic_ncols=True
            )

            last_time = time.time()
            last_bytes = 0

            def callback(monitor):
                nonlocal last_time, last_bytes
                now = time.time()
                elapsed = now - last_time
                bytes_sent = monitor.bytes_read - last_bytes
                if elapsed > 0:
                    speed = bytes_sent / elapsed  # bytes/sec
                    progress_bar.set_postfix_str(f"{speed / 1024 / 1024:.2f} MB/s")
                last_time = now
                last_bytes = monitor.bytes_read
                progress_bar.update(monitor.bytes_read - progress_bar.n)

            monitor = MultipartEncoderMonitor(encoder, callback)
            headers = {'Content-Type': monitor.content_type}
            response = requests.post(url, data=monitor, headers=headers)

            progress_bar.close()

            if response.ok:
                print(f"(+) Uploaded {filename}")
                return filename
            else:
                print("(-) Upload failed:", response.text)

    except Exception as e:
        print("(-) Upload error:", e)

    return None


# ============== FILE DOWNLOAD ===================
def download_file(filename):
    url = f"{SERVER_URL}/download/{filename}"
    dest_path = os.path.join(DOWNLOAD_DIR, filename)

    print(f"\n(+_+) File received: {filename}")
    choice = input("|?| Download this file? (y/n): ").strip().lower()
    if choice != 'y':
        print("(-_-) Skipped.")
        return None

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(dest_path, 'wb') as f, tqdm(
                total=total, unit='B', unit_scale=True, desc=f"📥 Downloading {filename}"
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        print(f"(+_+)(+_+) Saved to: {dest_path}")
        return dest_path
    except Exception as e:
        print("(-_-)(-_-) Download error:", e)
        return None

# ============== SERVER INTERACTION ================
def send_clipboard(content_type, content):
    try:
        res = requests.post(f"{SERVER_URL}/send", json={
            "type": content_type,
            "content": content,
            "device": DEVICE_NAME
        })
        if res.ok:
            print(f"<-> Sent clipboard to server ({content_type})")
    except Exception as e:
        print(">-< Failed to send to server:", e)

def fetch_clipboard():
    try:
        res = requests.get(f"{SERVER_URL}/get").json()
        return res
    except:
        return None

# ============== MAIN LOOP =====================
print(f".......... Clipboard helper started on {DEVICE_NAME}")
last_handled_id = None

while True:
    try:
        current = get_clipboard()

        # Check if it's a file and not previously sent/received
        if current and current != last_clipboard and current != last_received:
            if os.path.isfile(current):
                uploaded = upload_file(current)
                if uploaded:
                    send_clipboard("file", uploaded)
                    last_clipboard = current
            else:
                send_clipboard("text", current)
                last_clipboard = current

        # Get from server
        data = fetch_clipboard()
        if data:
            c_type = data.get("type")
            content = data.get("content")
            sender = data.get("device")

            # Unique ID per clipboard entry
            clipboard_id = f"{c_type}:{content}"

            if sender != DEVICE_NAME and clipboard_id != last_handled_id:
                if c_type == "file":
                    path = download_file(content)
                    if path:
                        set_clipboard(path)
                        last_received = path
                elif c_type == "text":
                    set_clipboard(content)
                    last_received = content
                    print(f"[0]-[0] Clipboard updated: {content[:40]}...")

                # ✅ Mark as handled so we don't repeat
                last_handled_id = clipboard_id

    except Exception as e:
        print("[x]-[x] Error:", e)

    time.sleep(CHECK_INTERVAL)
