"""
Schema Pydantic: Cria
"""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class CriaBase(BaseModel):
    id_matriz: int
    id_reprodutor: Optional[int] = None
    numero_registro: Optional[str] = None
    sexo: Optional[str] = None
    raca_pelagem: Optional[str] = None
    pai: Optional[str] = None
    data_nascimento: date
    status: str = "No Pasto"
    observacoes: Optional[str] = None


class CriaCreate(CriaBase):
    brinco: Optional[str] = None
    numero_ordem: Optional[int] = None


class CriaUpdate(BaseModel):
    numero_registro: Optional[str] = None
    brinco: Optional[str] = None
    sexo: Optional[str] = None
    raca_pelagem: Optional[str] = None
    pai: Optional[str] = None
    data_nascimento: Optional[date] = None
    status: Optional[str] = None
    id_comprador: Optional[int] = None
    vendido_para: Optional[str] = None
    data_venda: Optional[date] = None
    valor_venda: Optional[float] = None
    peso_venda: Optional[float] = None
    observacoes: Optional[str] = None


class CriaResponse(CriaBase):
    id: int
    brinco: Optional[str] = None
    numero_ordem: Optional[int] = None
    id_comprador: Optional[int] = None
    vendido_para: Optional[str] = None
    data_venda: Optional[date] = None
    valor_venda: Optional[float] = None
    peso_nascimento: Optional[float] = None
    peso_venda: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
