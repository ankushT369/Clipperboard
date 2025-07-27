import os
import yaml
import time
import platform
import requests
import subprocess

# ============ CONFIGURATION =============
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

client_cfg = cfg.get("client", {})

SERVER_URL = client_cfg.get("server_url", "http://127.0.0.1:8000")
DEVICE_NAME = client_cfg.get("device_name") or f"{platform.system().lower()}-{platform.node()}"
CHECK_INTERVAL = client_cfg.get("check_interval", 2)

# Track last clipboard states
last_clipboard = ""
last_received = ""
last_handled_id = None

# ============ CLIPBOARD FUNCTIONS ============
def get_clipboard():
    """Read current clipboard content (text only)."""
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
            finally:
                win32clipboard.CloseClipboard()

        elif system == "Darwin":
            return subprocess.check_output("pbpaste", text=True).strip()

        elif system == "Linux":
            if "com.termux" in os.environ.get("PREFIX", ""):
                return subprocess.check_output(["termux-clipboard-get"], text=True).strip()
            else:
                return subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], text=True).strip()

    except Exception as e:
        print("Clipboard read error:", e)
    return ""

def set_clipboard(text):
    """Write text to clipboard."""
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
            if "com.termux" in os.environ.get("PREFIX", ""):
                subprocess.run(["termux-clipboard-set"], input=text, text=True)
            else:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True)
    except Exception as e:
        print("Clipboard write error:", e)

# ============ SERVER INTERACTION ============
def send_clipboard(content):
    try:
        res = requests.post(f"{SERVER_URL}/send", json={
            "type": "text",
            "content": content,
            "device": DEVICE_NAME
        })
        if res.ok:
            print(f"<-> Sent clipboard to server.")
    except Exception as e:
        print(">-< Failed to send to server:", e)

def fetch_clipboard():
    try:
        return requests.get(f"{SERVER_URL}/get").json()
    except:
        return None

# ============ MAIN LOOP ============
print(f"Clipboard sync started on {DEVICE_NAME}")

while True:
    try:
        current = get_clipboard()

        # If clipboard changed locally → send to server
        if current and current != last_clipboard and current != last_received:
            send_clipboard(current)
            last_clipboard = current

        # Fetch new clipboard from server
        data = fetch_clipboard()
        if data:
            c_type = data.get("type")
            content = data.get("content")
            sender = data.get("device")
            clipboard_id = f"{c_type}:{content}"

            if sender != DEVICE_NAME and clipboard_id != last_handled_id:
                if c_type == "text":
                    set_clipboard(content)
                    last_received = content
                    print(f"[0]-[0] Clipboard updated: {content[:40]}...")
                last_handled_id = clipboard_id

    except Exception as e:
        print("[x]-[x] Error:", e)

    time.sleep(CHECK_INTERVAL)

