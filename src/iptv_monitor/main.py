import asyncio
from .gui import run_app
from .config import ensure_dirs

if __name__ == '__main__':
    ensure_dirs()
    # run GTK app (which runs its own loop)
    run_app()
