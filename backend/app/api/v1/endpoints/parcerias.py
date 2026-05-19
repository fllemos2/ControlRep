from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import re

from app.db.session import get_db
from app.models.matriz import Matriz
from app.models.cria import Cria

router = APIRouter()


def _nome_parceria(m: Matriz) -> str:
    if m.parceria:
        return m.parceria
    obs = (m.observacoes or '').lower()
    if 'fabio' in obs:
        return 'Fabio'
    if re.search(r'mary|mari', obs):
        return 'Mariana'
    return 'Fazenda'


@router.get("/resumo")
def resumo_parcerias(db: Session = Depends(get_db)):
    matrizes = db.query(Matriz).all()
    grupos: dict[str, dict] = {}

    for m in matrizes:
        nome = _nome_parceria(m)
        if nome not in grupos:
            grupos[nome] = {
                "nome": nome,
                "matrizes": [],
                "total_matrizes": 0,
                "total_crias": 0,
                "total_crias_no_pasto": 0,
                "total_valor_vendido": 0.0,
            }

        crias = db.query(Cria).filter(Cria.id_matriz == m.id).all()
        crias_no_pasto = sum(1 for c in crias if c.status == 'No Pasto')
        crias_vendidas = sum(1 for c in crias if c.status == 'Vendido')
        valor_vendido = sum(float(c.valor_venda) for c in crias if c.valor_venda)

        grupos[nome]["matrizes"].append({
            "id": m.id,
            "numero_registro": m.numero_registro,
            "brinco": m.brinco,
            "status": m.status,
            "total_crias": len(crias),
            "crias_no_pasto": crias_no_pasto,
            "crias_vendidas": crias_vendidas,
            "valor_vendido": round(valor_vendido, 2),
        })
        grupos[nome]["total_matrizes"] += 1
        grupos[nome]["total_crias"] += len(crias)
        grupos[nome]["total_crias_no_pasto"] += crias_no_pasto
        grupos[nome]["total_valor_vendido"] = round(
            grupos[nome]["total_valor_vendido"] + valor_vendido, 2
        )

    return sorted(grupos.values(), key=lambda x: x["nome"])
