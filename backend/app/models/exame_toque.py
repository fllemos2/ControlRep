from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from app.db.base import Base


class ExameToque(Base):
    __tablename__ = "exames_toque"

    id = Column(Integer, primary_key=True, index=True)
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    veterinario = Column(String(150))
    data_realizacao = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
