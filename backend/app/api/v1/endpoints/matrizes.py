from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.models.matriz import Matriz
from app.models.cria import Cria
from app.schemas.matriz import MatrizCreate, MatrizUpdate, MatrizResponse, MatrizListResponse
from app.services.ipca import fator_correcao, ipca_disponivel

router = APIRouter()


@router.get("/", response_model=List[MatrizResponse])
def list_matrizes(
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Matriz)
    if status:
        query = query.filter(Matriz.status == status)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=MatrizResponse, status_code=201)
def create_matriz(data: MatrizCreate, db: Session = Depends(get_db)):
    if db.query(Matriz).filter(Matriz.brinco == data.brinco).first():
        raise HTTPException(status_code=400, detail="Brinco já cadastrado")
    if db.query(Matriz).filter(Matriz.numero_registro == data.numero_registro).first():
        raise HTTPException(status_code=400, detail="Número de registro já cadastrado")
    matriz = Matriz(**data.model_dump())
    db.add(matriz)
    db.commit()
    db.refresh(matriz)
    return matriz


@router.get("/{id}", response_model=MatrizResponse)
def get_matriz(id: int, db: Session = Depends(get_db)):
    matriz = db.get(Matriz, id)
    if not matriz:
        raise HTTPException(status_code=404, detail="Matriz não encontrada")
    return matriz


@router.put("/{id}", response_model=MatrizResponse)
def update_matriz(id: int, data: MatrizUpdate, db: Session = Depends(get_db)):
    matriz = db.get(Matriz, id)
    if not matriz:
        raise HTTPException(status_code=404, detail="Matriz não encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(matriz, field, value)
    db.commit()
    db.refresh(matriz)
    return matriz


@router.get("/{id}/financeiro")
def get_financeiro(id: int, db: Session = Depends(get_db)):
    matriz = db.get(Matriz, id)
    if not matriz:
        raise HTTPException(status_code=404, detail="Matriz não encontrada")

    crias = db.query(Cria).filter(Cria.id_matriz == id).all()
    hoje = date.today()

    com_valor  = [c for c in crias if c.valor_venda]
    sem_valor  = [c for c in crias if not c.valor_venda and c.status == 'Vendido']

    # Idade média (dias) das crias que têm data_venda E data_nascimento
    idades = [
        (c.data_venda - c.data_nascimento).days
        for c in com_valor
        if c.data_venda and c.data_nascimento
    ]
    idade_media_dias = int(sum(idades) / len(idades)) if idades else None

    # Corrige cada venda pelo IPCA até hoje
    itens = []
    for c in com_valor:
        if c.data_venda:
            ref = c.data_venda
        elif c.data_nascimento and idade_media_dias is not None:
            from datetime import timedelta
            ref = c.data_nascimento + timedelta(days=idade_media_dias)
        else:
            ref = c.data_nascimento

        fator = fator_correcao(ref, hoje) if ref else 1.0
        vn    = float(c.valor_venda)
        itens.append({
            "id": c.id,
            "numero_registro": c.numero_registro,
            "data_ref": ref.isoformat() if ref else None,
            "data_ref_estimada": c.data_venda is None,
            "valor_nominal": round(vn, 2),
            "fator_ipca": round(fator, 6),
            "valor_corrigido": round(vn * fator, 2),
        })

    total_nominal   = sum(i["valor_nominal"]   for i in itens)
    total_corrigido = sum(i["valor_corrigido"] for i in itens)
    n_com           = len(itens)

    media_nominal   = total_nominal   / n_com if n_com else None
    media_corrigida = total_corrigido / n_com if n_com else None

    # Estimativa para crias sem valor registrado
    n_sem           = len(sem_valor)
    est_por_cria    = media_corrigida or 0.0
    total_estimado  = round(est_por_cria * n_sem, 2)
    total_geral     = round(total_corrigido + total_estimado, 2)

    # Valor por ano produtivo
    anos_produtivos = None
    valor_por_ano = None
    if matriz.primeira_cria_data:
        data_inicio = matriz.primeira_cria_data
        if matriz.status in ("descartada", "morta") and matriz.ultima_cria_data:
            data_fim_prod = matriz.ultima_cria_data
        else:
            data_fim_prod = hoje
        delta_anos = (data_fim_prod - data_inicio).days / 365.25
        if delta_anos > 0:
            anos_produtivos = round(delta_anos, 2)
            valor_por_ano = round(total_geral / delta_anos, 2)

    return {
        "total_crias":            len(crias),
        "crias_com_valor":        n_com,
        "crias_sem_valor":        n_sem,
        "media_nominal":          round(media_nominal,   2) if media_nominal   else None,
        "media_corrigida":        round(media_corrigida, 2) if media_corrigida else None,
        "total_nominal":          round(total_nominal,   2),
        "total_corrigido":        round(total_corrigido, 2),
        "total_estimado":         total_estimado,
        "total_geral":            total_geral,
        "idade_media_venda_dias": idade_media_dias,
        "anos_produtivos":        anos_produtivos,
        "valor_por_ano":          valor_por_ano,
        "data_referencia":        hoje.isoformat(),
        "ipca_disponivel":        ipca_disponivel(),
        "detalhes":               itens,
    }


@router.delete("/{id}", status_code=204)
def delete_matriz(id: int, db: Session = Depends(get_db)):
    matriz = db.get(Matriz, id)
    if not matriz:
        raise HTTPException(status_code=404, detail="Matriz não encontrada")
    db.delete(matriz)
    db.commit()
