from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ExameToqueBase(BaseModel):
    periodo_inicio: date
    periodo_fim: date
    veterinario: Optional[str] = None
    data_realizacao: date


class ExameToqueCreate(ExameToqueBase):
    pass


class ExameToqueUpdate(BaseModel):
    periodo_inicio: Optional[date] = None
    periodo_fim: Optional[date] = None
    veterinario: Optional[str] = None
    data_realizacao: Optional[date] = None


class ExameToqueResponse(ExameToqueBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
