"""
Schema Pydantic: Comprador
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


class CompradorBase(BaseModel):
    """Schema base para Comprador"""
    nome: str
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    observacoes: Optional[str] = None


class CompradorCreate(CompradorBase):
    """Schema para criação de Comprador"""
    pass


class CompradorUpdate(BaseModel):
    """Schema para atualização de Comprador"""
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    cep: Optional[str] = None
    observacoes: Optional[str] = None


class CompradorResponse(CompradorBase):
    """Schema de resposta para Comprador"""
    id: int
    data_cadastro: Optional[date]
    
    class Config:
        from_attributes = True
