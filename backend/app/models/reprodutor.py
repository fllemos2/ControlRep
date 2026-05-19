"""
Model: Reprodutor (Touro)
"""
from sqlalchemy import Column, Integer, String, Date, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Reprodutor(Base):
    __tablename__ = "reprodutores"
    
    id = Column(Integer, primary_key=True, index=True)
    brinco = Column(String(50), unique=True, index=True, nullable=False)
    nome = Column(String(255))
    numero_registro = Column(String(50), unique=True)
    
    # Características
    data_nascimento = Column(Date)
    raca = Column(String(50), default="Nelore")
    pelagem = Column(String(100))
    
    # Proveniência
    proveniencia = Column(String(255))
    data_aquisicao = Column(Date)
    
    # Metadata
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    crias = relationship("Cria", back_populates="reprodutor")
    
    class Config:
        from_attributes = True
