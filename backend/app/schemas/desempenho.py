"""
Schema Pydantic: Desempenho (Avaliação de Toque)
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class DesempenhoBase(BaseModel):
    """Schema base para Desempenho"""
    id_matriz: int
    data_avaliacao: date
    mes_gestacao: Optional[int] = Field(None, ge=0, le=9)
    semana_provavel: Optional[int] = None
    escore_corporal: Optional[float] = Field(None, ge=1, le=5)
    veterinario: Optional[str] = None
    observacoes: Optional[str] = None


class DesempenhoCreate(DesempenhoBase):
    """Schema para criação de Desempenho"""
    pass


class DesempenhoUpdate(BaseModel):
    """Schema para atualização de Desempenho"""
    mes_gestacao: Optional[int] = None
    semana_provavel: Optional[int] = None
    escore_corporal: Optional[float] = None
    veterinario: Optional[str] = None
    observacoes: Optional[str] = None


class DesempenhoResponse(DesempenhoBase):
    """Schema de resposta para Desempenho"""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
