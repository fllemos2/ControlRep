"""
Model: Comprador
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Comprador(Base):
    __tablename__ = "compradores"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    telefone = Column(String(20))
    
    # Endereço
    endereco = Column(String(255))
    cidade = Column(String(100))
    uf = Column(String(2))
    cep = Column(String(10))
    
    # Metadata
    data_cadastro = Column(Date, default=datetime.utcnow)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    crias_compradas = relationship("Cria", back_populates="comprador")
    
    class Config:
        from_attributes = True
