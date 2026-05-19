"""
Model: Matriz
"""
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class StatusMatrizEnum(str, enum.Enum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    DESCARTADA = "descartada"
    MORTA = "morta"


class Matriz(Base):
    __tablename__ = "matrizes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_registro = Column(String(50), unique=True, index=True, nullable=False)
    brinco = Column(String(50), unique=True, index=True, nullable=False)
    nome = Column(String(255))
    
    # Datas importantes
    data_nascimento = Column(Date)
    data_aquisicao = Column(Date)
    
    # Classificação
    raca = Column(String(50), default="Nelore")
    status = Column(String(20), default=StatusMatrizEnum.ATIVA)
    parceria = Column(String(20))  # Fabio | Mariana | Fazenda
    
    # Histórico reprodutivo
    total_crias = Column(Integer, default=0)
    primeira_cria_data = Column(Date)
    ultima_cria_data = Column(Date)
    media_dias_intervalo = Column(Integer)  # Dias entre parições
    
    # Metadata
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    crias = relationship("Cria", back_populates="matriz", cascade="all, delete-orphan")
    desempenhos = relationship("Desempenho", back_populates="matriz", cascade="all, delete-orphan")
    
    class Config:
        from_attributes = True
