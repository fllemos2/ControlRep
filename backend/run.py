"""Entry point para o executável PyInstaller."""
import sys, os

if getattr(sys, "frozen", False):
    # Garante que o MEIPASS está no path de importação
    sys.path.insert(0, sys._MEIPASS)

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
