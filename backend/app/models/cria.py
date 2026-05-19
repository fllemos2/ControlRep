"""
Model: Cria
"""
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.matriz import Matriz
    from app.models.reprodutor import Reprodutor
    from app.models.comprador import Comprador


class Cria(Base):
    __tablename__ = "crias"
    
    id = Column(Integer, primary_key=True, index=True)
    id_matriz = Column(Integer, ForeignKey("matrizes.id"), nullable=False, index=True)
    id_reprodutor = Column(Integer, ForeignKey("reprodutores.id"))
    
    # Identificação
    brinco = Column(String(50), unique=True, index=True)
    numero_ordem = Column(Integer)
    numero_registro = Column(String(50), unique=True)
    
    # Características
    sexo = Column(String(1))  # M ou F
    raca_pelagem = Column(String(100))
    cor = Column(String(100))
    
    # Status e paternidade
    status = Column(String(20), default="No Pasto")
    pai = Column(String(100))

    # Datas
    data_nascimento = Column(Date, nullable=False, index=True)

    # Dados de venda
    id_comprador = Column(Integer, ForeignKey("compradores.id"))
    vendido_para = Column(String(150))
    data_venda = Column(Date)
    valor_venda = Column(Numeric(10, 2))
    
    # Pesos e índices
    peso_nascimento = Column(Numeric(5, 2))
    peso_venda = Column(Numeric(5, 2))
    indice_ganho = Column(Numeric(5, 2))
    
    # Origem
    origem = Column(String(255), default="Cria da Fazenda")
    
    # Metadata
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    matriz = relationship("Matriz", back_populates="crias")
    reprodutor = relationship("Reprodutor", back_populates="crias")
    comprador = relationship("Comprador", back_populates="crias_compradas")
    
    class Config:
        from_attributes = True
