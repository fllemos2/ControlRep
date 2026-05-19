"""
Endpoints de sincronização do banco de dados (SQLite ↔ nuvem).
"""
from fastapi import APIRouter, UploadFile, HTTPException, Header
from fastapi.responses import FileResponse
from app.db.session import db_file_path, engine
from app.config import settings
import os, shutil, datetime
import httpx

router = APIRouter()


def _check_secret(x_sync_secret: str | None):
    if settings.SYNC_SECRET and x_sync_secret != settings.SYNC_SECRET:
        raise HTTPException(status_code=401, detail="Sync secret inválido.")


def _require_sqlite():
    path = db_file_path()
    if path is None:
        raise HTTPException(status_code=400, detail="Sync de arquivo disponível apenas para SQLite.")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Arquivo do banco não encontrado.")
    return path


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/status")
def sync_status():
    path = db_file_path()
    if path and os.path.exists(path):
        mtime = os.path.getmtime(path)
        return {
            "type": "sqlite",
            "last_modified": mtime,
            "last_modified_iso": datetime.datetime.fromtimestamp(mtime).isoformat(),
            "size_bytes": os.path.getsize(path),
            "cloud_configured": bool(settings.CLOUD_SYNC_URL),
        }
    return {"type": "other", "cloud_configured": bool(settings.CLOUD_SYNC_URL)}


# ── Export / Import ───────────────────────────────────────────────────────────

@router.get("/export")
def export_db(x_sync_secret: str | None = Header(default=None)):
    """Baixa o arquivo .db completo."""
    _check_secret(x_sync_secret)
    path = _require_sqlite()
    # Checkpoint WAL antes de exportar (garante arquivo consistente)
    try:
        with engine.connect() as conn:
            conn.execute(engine.dialect.dbapi.sqlite3.connect(path).cursor().__class__.__mro__[0].__init__)
    except Exception:
        pass
    return FileResponse(
        path,
        filename="cattle_control.db",
        media_type="application/octet-stream",
        headers={"X-DB-Modified": str(os.path.getmtime(path))},
    )


@router.post("/import")
async def import_db(
    file: UploadFile,
    x_sync_secret: str | None = Header(default=None),
):
    """Substitui o banco local pelo arquivo enviado."""
    _check_secret(x_sync_secret)
    path = _require_sqlite()
    content = await file.read()
    # Fecha todas as conexões do pool antes de substituir
    engine.dispose()
    backup = path + ".bak"
    shutil.copy2(path, backup)
    with open(path, "wb") as f:
        f.write(content)
    return {"status": "ok", "size_bytes": len(content)}


# ── Push / Pull para nuvem ────────────────────────────────────────────────────

@router.post("/push")
def push_to_cloud(x_sync_secret: str | None = Header(default=None)):
    """Envia o banco local para a instância na nuvem."""
    _check_secret(x_sync_secret)
    if not settings.CLOUD_SYNC_URL:
        raise HTTPException(status_code=503, detail="CLOUD_SYNC_URL não configurada.")
    path = _require_sqlite()

    with open(path, "rb") as f:
        data = f.read()

    headers = {}
    if settings.SYNC_SECRET:
        headers["x-sync-secret"] = settings.SYNC_SECRET

    try:
        r = httpx.post(
            f"{settings.CLOUD_SYNC_URL.rstrip('/')}/api/v1/sync/import",
            files={"file": ("cattle_control.db", data, "application/octet-stream")},
            headers=headers,
            timeout=60,
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Nuvem retornou {e.response.status_code}.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao enviar: {e}")

    return {"status": "ok", "pushed_bytes": len(data)}


@router.post("/pull")
def pull_from_cloud(x_sync_secret: str | None = Header(default=None)):
    """Baixa o banco da nuvem e substitui o local."""
    _check_secret(x_sync_secret)
    if not settings.CLOUD_SYNC_URL:
        raise HTTPException(status_code=503, detail="CLOUD_SYNC_URL não configurada.")
    path = _require_sqlite()

    headers = {}
    if settings.SYNC_SECRET:
        headers["x-sync-secret"] = settings.SYNC_SECRET

    try:
        r = httpx.get(
            f"{settings.CLOUD_SYNC_URL.rstrip('/')}/api/v1/sync/export",
            headers=headers,
            timeout=60,
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Nuvem retornou {e.response.status_code}.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao baixar: {e}")

    engine.dispose()
    backup = path + ".bak"
    if os.path.exists(path):
        shutil.copy2(path, backup)
    with open(path, "wb") as f:
        f.write(r.content)

    return {"status": "ok", "pulled_bytes": len(r.content)}
