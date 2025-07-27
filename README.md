# Universal Clipboard Sync (Mac, Windows, Linux, Android)

A Python-based clipboard synchronization tool that works across multiple devices and operating systems. 

This tool allows you to sync your clipboard content across devices using a Flask server and a Python-based clipboard client.


## Features

- Share text clipboard across devices
- Auto clipboard detection (text and file path)
- Works on Windows, macOS, Linux, Android


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
   - Updates clipboard accordingly


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


## Configuration
 edit needed

## Folder Structure

```
[ankush@cognitive Clipperboard]$ tree
.
├── client
│   ├── clipboard.py
│   └── config.yaml
├── README.md
└── server
    ├── config.yaml
    ├── instance
    │   └── clipboard.db
    ├── server.py
    ├── server_setup.sh
    └── uploads

4 directories, 7 files
```


## To Do

- Android native GUI app
- Auto-start support on Windows/macOS/Linux
- Image clipboard support
- Sync history or logs
- LAN-only secure access or token authentication


## Contributing

Pull requests are welcome. If you have suggestions for features or improvements, please open an issue.


## Credits

Built with Python, Flask, requests, tqdm, and requests-toolbelt.
