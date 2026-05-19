from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.toque_matriz import ToqueMatriz
from app.schemas.toque_matriz import ToqueMatrizCreate, ToqueMatrizUpdate, ToqueMatrizResponse

router = APIRouter()


@router.get("/", response_model=List[ToqueMatrizResponse])
def list_toques(
    id_matriz: Optional[int] = None,
    id_exame_toque: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(ToqueMatriz)
    if id_matriz:
        q = q.filter(ToqueMatriz.id_matriz == id_matriz)
    if id_exame_toque:
        q = q.filter(ToqueMatriz.id_exame_toque == id_exame_toque)
    return q.order_by(ToqueMatriz.id.desc()).all()


@router.post("/", response_model=ToqueMatrizResponse, status_code=201)
def create_toque(data: ToqueMatrizCreate, db: Session = Depends(get_db)):
    toque = ToqueMatriz(**data.model_dump())
    db.add(toque)
    db.commit()
    db.refresh(toque)
    return toque


@router.get("/{id}", response_model=ToqueMatrizResponse)
def get_toque(id: int, db: Session = Depends(get_db)):
    toque = db.get(ToqueMatriz, id)
    if not toque:
        raise HTTPException(status_code=404, detail="Toque não encontrado")
    return toque


@router.put("/{id}", response_model=ToqueMatrizResponse)
def update_toque(id: int, data: ToqueMatrizUpdate, db: Session = Depends(get_db)):
    toque = db.get(ToqueMatriz, id)
    if not toque:
        raise HTTPException(status_code=404, detail="Toque não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(toque, field, value)
    db.commit()
    db.refresh(toque)
    return toque


@router.delete("/{id}", status_code=204)
def delete_toque(id: int, db: Session = Depends(get_db)):
    toque = db.get(ToqueMatriz, id)
    if not toque:
        raise HTTPException(status_code=404, detail="Toque não encontrado")
    db.delete(toque)
    db.commit()
