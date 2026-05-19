from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.models.matriz import Matriz
from app.models.cria import Cria
from app.models.exame_toque import ExameToque
from app.models.toque_matriz import ToqueMatriz

router = APIRouter()


@router.get("/")
def dashboard_stats(db: Session = Depends(get_db)):
    # ── Matrizes ──────────────────────────────────────────────────────────────
    ativas = db.query(Matriz).filter(Matriz.status == "ativa").all()
    ids_ativas = {m.id for m in ativas}

    ultimo_exame = (
        db.query(ExameToque)
        .order_by(ExameToque.data_realizacao.desc())
        .first()
    )

    cheias = vazias = paridas = 0

    if ultimo_exame:
        toques = (
            db.query(ToqueMatriz)
            .filter(ToqueMatriz.id_exame_toque == ultimo_exame.id)
            .all()
        )
        toque_map = {t.id_matriz: (t.resultado or "").lower() for t in toques}

        for mid in ids_ativas:
            res = toque_map.get(mid, "")
            if "cheia" in res or "prenha" in res or "gestante" in res:
                cheias += 1
            elif "vazia" in res:
                vazias += 1

        # Paridas: cria nascida após a data do último exame
        paridas = (
            db.query(Cria.id_matriz)
            .filter(
                Cria.id_matriz.in_(ids_ativas),
                Cria.data_nascimento > ultimo_exame.data_realizacao,
            )
            .distinct()
            .count()
        )

    # ── Crias ─────────────────────────────────────────────────────────────────
    crias_pasto = db.query(Cria).filter(Cria.status == "No Pasto").all()
    hoje = date.today()

    idades_meses = [
        (hoje - c.data_nascimento).days / 30.44
        for c in crias_pasto
        if c.data_nascimento
    ]
    idade_media = round(sum(idades_meses) / len(idades_meses), 1) if idades_meses else 0

    machos = sum(1 for c in crias_pasto if c.sexo == "M")
    femeas = sum(1 for c in crias_pasto if c.sexo == "F")

    return {
        "matrizes": {
            "ativas": len(ativas),
            "cheias": cheias,
            "vazias": vazias,
            "paridas": paridas,
        },
        "crias": {
            "no_pasto": len(crias_pasto),
            "idade_media_meses": idade_media,
            "machos": machos,
            "femeas": femeas,
        },
    }
