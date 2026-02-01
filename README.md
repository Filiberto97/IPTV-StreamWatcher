# IPTV Monitor — Xubuntu GUI

This repository now contains a local GTK desktop application for Xubuntu that monitors HLS channels and M3U playlists on your machine. It performs periodic checks (no FFmpeg), stores history in a local SQLite database, and provides a native GTK UI for configuration and viewing results.

Quick start (development)

1. Install system packages on Xubuntu:
   sudo apt update && sudo apt install -y python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0

2. Create a virtual environment and install Python dependencies:
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt

3. Run the app:
   python -m iptv_monitor.main

Install for daily use (recommended)

1. Run the installer (creates venv, installs deps, adds desktop entry and systemd user service):
   ./install.sh

2. Start the background service (user-level systemd) to run periodic checks:
   systemctl --user enable --now iptv-monitor.service

3. Launch the GUI from your Applications menu.

Configuration & storage
- Config: `~/.config/iptv-monitor/config.json`
- DB: `~/.local/share/iptv-monitor/data.sqlite`
- Logs: `~/.local/share/iptv-monitor/app.log`

Notes
- This app is local-only. For 24/7 monitoring while your PC is off, consider running the service on a VPS (not included in this repo).
- The app avoids FFmpeg and uses HTTP requests to evaluate HLS manifests and segments.

Files of interest
- `src/iptv_monitor/` — Python source (GUI, worker, DB helpers)
- `install.sh` — installer script (user-level install)
- `iptv-monitor.service` — systemd user service template

License: MIT
