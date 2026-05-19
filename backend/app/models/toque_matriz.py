from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base


class ToqueMatriz(Base):
    __tablename__ = "toques_matrizes"

    id = Column(Integer, primary_key=True, index=True)
    id_matriz = Column(Integer, ForeignKey("matrizes.id"), nullable=False)
    id_exame_toque = Column(Integer, ForeignKey("exames_toque.id"), nullable=False)
    resultado = Column(String(10))        # "Cheia" | "Vazia"
    dias_estimados_fecundacao = Column(Integer)
    observacoes = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
