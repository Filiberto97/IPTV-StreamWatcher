import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'iptv-monitor'
DATA_DIR = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'iptv-monitor'
CONFIG_FILE = CONFIG_DIR / 'config.json'
DB_FILE = DATA_DIR / 'data.sqlite'
LOG_FILE = DATA_DIR / 'app.log'

DEFAULTS = {
    'check_interval_sec': 900,  # 15 minutes
    'window_hours': 24,
}

def ensure_dirs():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

ensure_dirs()
