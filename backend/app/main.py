"""
Aplicação FastAPI - Cattle Control
"""
import os, sys, threading, webbrowser, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.db.base import Base
from app.db.session import engine
import app.models


# ── Frontend estático ─────────────────────────────────────────────────────────

def _frontend_dist() -> str | None:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "frontend_dist")
    # Desenvolvimento: pasta dist do Vite (se já buildada)
    dev_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
    )
    return dev_path if os.path.isdir(dev_path) else None


FRONTEND_DIST = _frontend_dist()


def _open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")


def _ensure_appdata_config():
    """Cria .env padrão em %APPDATA%/CattleControl na primeira execução."""
    if not getattr(sys, "frozen", False):
        return
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    data_dir = os.path.join(appdata, "CattleControl")
    os.makedirs(data_dir, exist_ok=True)
    env_path = os.path.join(data_dir, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("# Cattle Control — configurações\n")
            f.write("ANTHROPIC_API_KEY=\n")
            f.write("SYNC_SECRET=\n")
            f.write("CLOUD_SYNC_URL=\n")


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_appdata_config()
    Base.metadata.create_all(bind=engine)
    if getattr(sys, "frozen", False):
        threading.Thread(target=_open_browser, daemon=True).start()
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs" if not getattr(sys, "frozen", False) else None,
    redoc_url=None,
)

# CORS: dev (Vite :5173 → API :8000) e Railway (sync entre instâncias)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not getattr(sys, "frozen", False) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": settings.PROJECT_VERSION}


# Rotas da API
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)


# ── Serve SPA (deve ser o último) ─────────────────────────────────────────────

if FRONTEND_DIST:
    @app.get("/{full_path:path}")
    async def spa(full_path: str, request: Request):
        # Servir arquivo estático se existir
        if full_path:
            file_path = os.path.join(FRONTEND_DIST, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
        # Fallback para index.html (Vue Router trata as rotas)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
