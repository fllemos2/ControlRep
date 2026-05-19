"""
Model: Desempenho (Avaliação de Toque Veterinário)
"""
from sqlalchemy import Column, Integer, Date, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Desempenho(Base):
    __tablename__ = "desempenhos"
    
    id = Column(Integer, primary_key=True, index=True)
    id_matriz = Column(Integer, ForeignKey("matrizes.id"), nullable=False, index=True)
    
    # Data da avaliação
    data_avaliacao = Column(Date, nullable=False, index=True)
    
    # Avaliação de gestação
    mes_gestacao = Column(Integer)  # 1-9
    semana_provavel = Column(Integer)  # Semana prevista de nascimento
    
    # Condição corporal
    escore_corporal = Column(Numeric(3, 1))  # 1-5
    
    # Dados veterinários
    veterinario = Column(Text)  # Nome do veterinário
    
    # Metadata
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    matriz = relationship("Matriz", back_populates="desempenhos")
    
    class Config:
        from_attributes = True
