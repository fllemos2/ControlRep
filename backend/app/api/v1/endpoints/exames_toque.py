from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.exame_toque import ExameToque
from app.schemas.exame_toque import ExameToqueCreate, ExameToqueUpdate, ExameToqueResponse

router = APIRouter()


@router.get("/ultimo", response_model=ExameToqueResponse)
def get_ultimo(db: Session = Depends(get_db)):
    exame = db.query(ExameToque).order_by(ExameToque.data_realizacao.desc(), ExameToque.id.desc()).first()
    if not exame:
        raise HTTPException(status_code=404, detail="Nenhum exame de toque cadastrado")
    return exame


@router.get("/", response_model=List[ExameToqueResponse])
def list_exames(db: Session = Depends(get_db)):
    return db.query(ExameToque).order_by(ExameToque.data_realizacao.desc(), ExameToque.id.desc()).all()


@router.post("/", response_model=ExameToqueResponse, status_code=201)
def create_exame(data: ExameToqueCreate, db: Session = Depends(get_db)):
    exame = ExameToque(**data.model_dump())
    db.add(exame)
    db.commit()
    db.refresh(exame)
    return exame


@router.get("/{id}", response_model=ExameToqueResponse)
def get_exame(id: int, db: Session = Depends(get_db)):
    exame = db.get(ExameToque, id)
    if not exame:
        raise HTTPException(status_code=404, detail="Exame não encontrado")
    return exame


@router.put("/{id}", response_model=ExameToqueResponse)
def update_exame(id: int, data: ExameToqueUpdate, db: Session = Depends(get_db)):
    exame = db.get(ExameToque, id)
    if not exame:
        raise HTTPException(status_code=404, detail="Exame não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exame, field, value)
    db.commit()
    db.refresh(exame)
    return exame


@router.delete("/{id}", status_code=204)
def delete_exame(id: int, db: Session = Depends(get_db)):
    exame = db.get(ExameToque, id)
    if not exame:
        raise HTTPException(status_code=404, detail="Exame não encontrado")
    db.delete(exame)
    db.commit()
