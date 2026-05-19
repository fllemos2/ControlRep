from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReprodutorBase(BaseModel):
    brinco: str
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    raca: str = "Nelore"
    pelagem: Optional[str] = None
    proveniencia: Optional[str] = None
    observacoes: Optional[str] = None


class ReprodutorCreate(ReprodutorBase):
    numero_registro: Optional[str] = None
    data_aquisicao: Optional[date] = None


class ReprodutorUpdate(BaseModel):
    nome: Optional[str] = None
    pelagem: Optional[str] = None
    proveniencia: Optional[str] = None
    observacoes: Optional[str] = None


class ReprodutorResponse(ReprodutorBase):
    id: int
    numero_registro: Optional[str] = None
    data_aquisicao: Optional[date] = None

    class Config:
        from_attributes = True


class ReprodutorListResponse(BaseModel):
    id: int
    brinco: str
    nome: Optional[str] = None
    raca: str

    class Config:
        from_attributes = True
