from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.cria import Cria
from app.models.matriz import Matriz
from app.schemas.cria import CriaCreate, CriaUpdate, CriaResponse

router = APIRouter()


@router.get("/", response_model=List[CriaResponse])
def list_crias(
    skip: int = 0,
    limit: int = Query(default=100, le=2000),
    id_matriz: Optional[int] = None,
    sexo: Optional[str] = None,
    status: Optional[str] = None,
    sem_venda: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Cria)
    if id_matriz:
        query = query.filter(Cria.id_matriz == id_matriz)
    if sexo:
        query = query.filter(Cria.sexo == sexo.upper())
    if status:
        query = query.filter(Cria.status == status)
    if sem_venda:
        query = query.filter(Cria.id_comprador == None)
    return query.order_by(Cria.data_nascimento, Cria.id).offset(skip).limit(limit).all()


@router.post("/", response_model=CriaResponse, status_code=201)
def create_cria(data: CriaCreate, db: Session = Depends(get_db)):
    if not db.get(Matriz, data.id_matriz):
        raise HTTPException(status_code=404, detail="Matriz não encontrada")
    if data.brinco and db.query(Cria).filter(Cria.brinco == data.brinco).first():
        raise HTTPException(status_code=400, detail="Brinco já cadastrado")
    if data.numero_registro and db.query(Cria).filter(Cria.numero_registro == data.numero_registro).first():
        raise HTTPException(status_code=400, detail="Reg. Nasc. já cadastrado")
    cria = Cria(**data.model_dump())
    db.add(cria)
    db.commit()
    db.refresh(cria)
    return cria


@router.get("/{id}", response_model=CriaResponse)
def get_cria(id: int, db: Session = Depends(get_db)):
    cria = db.get(Cria, id)
    if not cria:
        raise HTTPException(status_code=404, detail="Cria não encontrada")
    return cria


@router.put("/{id}", response_model=CriaResponse)
def update_cria(id: int, data: CriaUpdate, db: Session = Depends(get_db)):
    cria = db.get(Cria, id)
    if not cria:
        raise HTTPException(status_code=404, detail="Cria não encontrada")
    if data.numero_registro and data.numero_registro != cria.numero_registro:
        if db.query(Cria).filter(Cria.numero_registro == data.numero_registro).first():
            raise HTTPException(status_code=400, detail="Reg. Nasc. já cadastrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cria, field, value)
    db.commit()
    db.refresh(cria)
    return cria


@router.delete("/{id}", status_code=204)
def delete_cria(id: int, db: Session = Depends(get_db)):
    cria = db.get(Cria, id)
    if not cria:
        raise HTTPException(status_code=404, detail="Cria não encontrada")
    db.delete(cria)
    db.commit()
