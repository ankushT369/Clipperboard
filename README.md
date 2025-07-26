# Universal Clipboard Sync (Mac, Windows, Linux, Android)

A Python-based clipboard synchronization tool that works across multiple devices and operating systems. It supports text, file path, and file content sharing (with upload/download progress bars) over a shared network.

This tool allows you to sync your clipboard content across devices using a Flask server and a Python-based clipboard client.

---

## Features

- Share text clipboard across devices
- Upload and share files between devices
- Prompt user before downloading files
- Upload/Download progress bars with speed display
- Auto clipboard detection (text and file path)
- Works on Windows, macOS, Linux

---

## How It Works

1. One device runs the **Flask server**:
   ```bash
   python3 server.py
   ```

2. All devices run the **clipboard helper**:
   ```bash
   python3 clipboard.py
   ```

3. Automatically:
   - Detects clipboard changes
   - Uploads file or text if changed
   - Prompts other devices to download
   - Updates clipboard accordingly

---

## Installation

### Dependencies (All Platforms)
```bash
pip install requests tqdm requests-toolbelt
```

### Windows-only
```bash
pip install pywin32
```

### Linux-only
```bash
sudo apt install xclip
```

### macOS
No extra dependencies required.

---

## File Uploads/Downloads

- Uploads show a real-time progress bar and speed (MB/s)
- Downloads prompt before saving
- Files are saved to `~/ClipboardDownloads` (changeable)

---

## Example Output

```
Clipboard helper started on macbook.local
Uploading test.pdf: 100%|██████████| 3.2M/3.2M [00:01<00:00, 3.17MB/s]
Uploaded test.pdf
File received from another device: test.pdf
Download this file? (y/n): y
Downloading test.pdf: 100%|██████████| 3.2M/3.2M [00:01<00:00, 3.18MB/s]
Downloaded: ~/ClipboardDownloads/test.pdf
```

---

## Configuration

Open `clipboard_helper.py` and set:

```python
SERVER_URL = "http://<your-server-ip>:5000"  # Use your actual server IP
DEVICE_NAME = platform.node()                # Auto-detected device name
```

Make sure all devices point to the correct IP.

---

## Folder Structure

```
project/
├── clipboard_server.py      # Flask-based server
├── clipboard_helper.py      # Python client for clipboard sync
├── uploads/                 # Server folder for shared files
└── README.md
```

---

## To Do

- Android native GUI app
- Auto-start support on Windows/macOS/Linux
- Image clipboard support
- Sync history or logs
- LAN-only secure access or token authentication

---

## Contributing

Pull requests are welcome. If you have suggestions for features or improvements, please open an issue.

---

## Credits

Built with Python, Flask, requests, tqdm, and requests-toolbelt.
