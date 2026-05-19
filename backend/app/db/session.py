"""
Configuração de banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os, sys


def _resolve_db_url() -> str:
    # Variável de ambiente explícita tem prioridade (Railway/Render)
    if os.environ.get("DATABASE_URL"):
        url = os.environ["DATABASE_URL"]
        # Railway usa "postgres://" — SQLAlchemy 2.x requer "postgresql+psycopg2://"
        if url.startswith("postgres://"):
            url = "postgresql+psycopg2://" + url[len("postgres://"):]
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg2://" + url[len("postgresql://"):]
        return url
    if getattr(sys, "frozen", False):
        # App empacotado: usa %APPDATA%/CattleControl/
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        data_dir = os.path.join(appdata, "CattleControl")
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, "cattle_control.db").replace("\\", "/")
        return f"sqlite:///{db_path}"
    # Desenvolvimento: relativo ao diretório de execução
    return "sqlite:///./cattle_control.db"


def db_file_path() -> str | None:
    """Caminho absoluto ao arquivo SQLite, ou None se não for SQLite."""
    url = DATABASE_URL
    if not url.startswith("sqlite:///"):
        return None
    path = url[len("sqlite:///"):]
    if path.startswith("./"):
        path = os.path.abspath(path[2:])
    return path


DATABASE_URL = _resolve_db_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
