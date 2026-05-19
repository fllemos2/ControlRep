from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ToqueMatrizBase(BaseModel):
    id_matriz: int
    id_exame_toque: int
    resultado: str
    dias_estimados_fecundacao: Optional[int] = None
    observacoes: Optional[str] = None


class ToqueMatrizCreate(ToqueMatrizBase):
    pass


class ToqueMatrizUpdate(BaseModel):
    id_exame_toque: Optional[int] = None
    resultado: Optional[str] = None
    dias_estimados_fecundacao: Optional[int] = None
    observacoes: Optional[str] = None


class ToqueMatrizResponse(ToqueMatrizBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
