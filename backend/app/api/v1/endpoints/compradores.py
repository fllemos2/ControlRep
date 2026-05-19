from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.comprador import Comprador
from app.schemas.comprador import CompradorCreate, CompradorUpdate, CompradorResponse

router = APIRouter()


@router.get("/", response_model=List[CompradorResponse])
def list_compradores(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    return db.query(Comprador).offset(skip).limit(limit).all()


@router.post("/", response_model=CompradorResponse, status_code=201)
def create_comprador(data: CompradorCreate, db: Session = Depends(get_db)):
    if data.email and db.query(Comprador).filter(Comprador.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    comprador = Comprador(**data.model_dump())
    db.add(comprador)
    db.commit()
    db.refresh(comprador)
    return comprador


@router.get("/{id}", response_model=CompradorResponse)
def get_comprador(id: int, db: Session = Depends(get_db)):
    comprador = db.get(Comprador, id)
    if not comprador:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    return comprador


@router.put("/{id}", response_model=CompradorResponse)
def update_comprador(id: int, data: CompradorUpdate, db: Session = Depends(get_db)):
    comprador = db.get(Comprador, id)
    if not comprador:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(comprador, field, value)
    db.commit()
    db.refresh(comprador)
    return comprador


@router.delete("/{id}", status_code=204)
def delete_comprador(id: int, db: Session = Depends(get_db)):
    comprador = db.get(Comprador, id)
    if not comprador:
        raise HTTPException(status_code=404, detail="Comprador não encontrado")
    db.delete(comprador)
    db.commit()
