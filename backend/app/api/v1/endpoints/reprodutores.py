from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.reprodutor import Reprodutor
from app.schemas.reprodutor import ReprodutorCreate, ReprodutorUpdate, ReprodutorResponse, ReprodutorListResponse

router = APIRouter()


@router.get("/", response_model=List[ReprodutorListResponse])
def list_reprodutores(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    return db.query(Reprodutor).offset(skip).limit(limit).all()


@router.post("/", response_model=ReprodutorResponse, status_code=201)
def create_reprodutor(data: ReprodutorCreate, db: Session = Depends(get_db)):
    if db.query(Reprodutor).filter(Reprodutor.brinco == data.brinco).first():
        raise HTTPException(status_code=400, detail="Brinco já cadastrado")
    reprodutor = Reprodutor(**data.model_dump())
    db.add(reprodutor)
    db.commit()
    db.refresh(reprodutor)
    return reprodutor


@router.get("/{id}", response_model=ReprodutorResponse)
def get_reprodutor(id: int, db: Session = Depends(get_db)):
    reprodutor = db.get(Reprodutor, id)
    if not reprodutor:
        raise HTTPException(status_code=404, detail="Reprodutor não encontrado")
    return reprodutor


@router.put("/{id}", response_model=ReprodutorResponse)
def update_reprodutor(id: int, data: ReprodutorUpdate, db: Session = Depends(get_db)):
    reprodutor = db.get(Reprodutor, id)
    if not reprodutor:
        raise HTTPException(status_code=404, detail="Reprodutor não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(reprodutor, field, value)
    db.commit()
    db.refresh(reprodutor)
    return reprodutor


@router.delete("/{id}", status_code=204)
def delete_reprodutor(id: int, db: Session = Depends(get_db)):
    reprodutor = db.get(Reprodutor, id)
    if not reprodutor:
        raise HTTPException(status_code=404, detail="Reprodutor não encontrado")
    db.delete(reprodutor)
    db.commit()
