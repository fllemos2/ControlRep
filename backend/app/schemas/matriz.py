"""
Schema Pydantic: Matriz
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class MatrizBase(BaseModel):
    """Schema base para Matriz"""
    numero_registro: str = Field(..., min_length=1, max_length=50)
    brinco: str = Field(..., min_length=1, max_length=50)
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    data_aquisicao: Optional[date] = None
    raca: str = "Nelore"
    status: str = "ativa"
    parceria: Optional[str] = None
    observacoes: Optional[str] = None


class MatrizCreate(MatrizBase):
    """Schema para criação de Matriz"""
    pass


class MatrizUpdate(BaseModel):
    """Schema para atualização de Matriz"""
    brinco: Optional[str] = None
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    status: Optional[str] = None
    parceria: Optional[str] = None
    observacoes: Optional[str] = None
    total_crias: Optional[int] = None
    primeira_cria_data: Optional[date] = None
    ultima_cria_data: Optional[date] = None
    media_dias_intervalo: Optional[int] = None


class MatrizResponse(MatrizBase):
    """Schema de resposta para Matriz"""
    id: int
    total_crias: int = 0
    primeira_cria_data: Optional[date] = None
    ultima_cria_data: Optional[date] = None
    media_dias_intervalo: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MatrizListResponse(BaseModel):
    """Schema de resposta para listagem de Matrizes"""
    id: int
    numero_registro: str
    brinco: str
    nome: Optional[str]
    status: str
    total_crias: int
    
    class Config:
        from_attributes = True
