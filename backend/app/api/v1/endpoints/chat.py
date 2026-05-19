"""
Endpoint de chat em linguagem natural para o Cattle Control.
Usa Claude para interpretar perguntas e gerar ações (toque / cria).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Optional
from datetime import date, timedelta
import json

from app.db.session import get_db
from app.config import settings
from app.models.matriz import Matriz
from app.models.cria import Cria
from app.models.exame_toque import ExameToque
from app.models.toque_matriz import ToqueMatriz

router = APIRouter()

GESTACAO_DIAS = 285


# ── schemas ──────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str       # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

class ActionItem(BaseModel):
    type: str                       # create_toque | create_cria | create_exame
    label: str                      # descrição legível para o usuário
    payload: dict[str, Any]

class ChatResponse(BaseModel):
    message: str
    actions: list[ActionItem] = []


# ── helpers de contexto ───────────────────────────────────────────────────────

def _build_context(db: Session) -> str:
    hoje = date.today()

    # Matrizes ativas
    ativas = db.query(Matriz).filter(Matriz.status.in_(["ativa", "inativa"])).all()
    matrizes_info = [
        f"{m.numero_registro} (última cria: {m.ultima_cria_data or 'S/R'}, total: {m.total_crias})"
        for m in ativas[:80]
    ]

    # Último exame de toque
    ultimo_exame = (
        db.query(ExameToque)
        .order_by(ExameToque.data_realizacao.desc())
        .first()
    )
    exame_info = "Nenhum exame cadastrado"
    cheias_info = []
    if ultimo_exame:
        exame_info = (
            f"ID={ultimo_exame.id}, data={ultimo_exame.data_realizacao}, "
            f"veterinário={ultimo_exame.veterinario or 'não informado'}"
        )
        toques = db.query(ToqueMatriz).filter(
            ToqueMatriz.id_exame_toque == ultimo_exame.id
        ).all()
        for t in toques:
            m = db.get(Matriz, t.id_matriz)
            nr = m.numero_registro if m else f"id={t.id_matriz}"
            data_prev = None
            if t.dias_estimados_fecundacao and ultimo_exame.data_realizacao:
                dias_restantes = GESTACAO_DIAS - t.dias_estimados_fecundacao
                data_prev = ultimo_exame.data_realizacao + timedelta(days=dias_restantes)
            cheias_info.append(
                f"  Matriz {nr}: {t.resultado}, {t.dias_estimados_fecundacao} dias fecundação"
                + (f", parto previsto ≈ {data_prev}" if data_prev else "")
            )

    # Crias recentes (últimos 60 dias)
    recente = hoje - timedelta(days=60)
    crias_rec = (
        db.query(Cria)
        .filter(Cria.data_nascimento >= recente)
        .order_by(Cria.data_nascimento.desc())
        .limit(20)
        .all()
    )
    crias_info = [
        f"Cria {c.numero_registro or '?'} | matriz {c.id_matriz} | {c.data_nascimento} | {c.sexo or '?'} | status: {c.status}"
        for c in crias_rec
    ]

    ctx = f"""
DATA ATUAL: {hoje}
GESTAÇÃO MÉDIA: {GESTACAO_DIAS} dias

MATRIZES ATIVAS ({len(ativas)}):
{chr(10).join(matrizes_info)}

ÚLTIMO EXAME DE TOQUE: {exame_info}
RESULTADOS (cheias e vazias):
{chr(10).join(cheias_info) if cheias_info else "  Nenhum resultado registrado"}

CRIAS RECENTES (últimos 60 dias):
{chr(10).join(crias_info) if crias_info else "  Nenhuma cria recente"}
""".strip()
    return ctx


# ── system prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
Você é um assistente especializado em controle de reprodução do rebanho Nelore (Fazendas Tangará/Almas).
Gestação média: {GESTACAO_DIAS} dias.

Responda SEMPRE em JSON com a seguinte estrutura (não inclua nada fora do JSON):
{{
  "message": "<resposta em texto para o usuário, em português>",
  "actions": [
    {{
      "type": "<tipo>",
      "label": "<descrição legível>",
      "payload": {{ <dados> }}
    }}
  ]
}}

Tipos de ação disponíveis:
- "create_exame_toque":  payload: {{ "periodo_inicio": "YYYY-MM-DD", "periodo_fim": "YYYY-MM-DD", "data_realizacao": "YYYY-MM-DD", "veterinario": "nome ou null" }}
- "create_toque_resultado": payload: {{ "numero_registro": "NNN", "id_exame_toque": N, "resultado": "Cheia"|"Vazia", "dias_estimados_fecundacao": N_ou_null, "observacoes": "texto ou null" }}
- "create_cria": payload: {{ "numero_registro_matriz": "NNN", "data_nascimento": "YYYY-MM-DD", "sexo": "M"|"F"|null, "numero_registro_cria": "NNN ou null", "raca_pelagem": "texto ou null", "pai": "texto ou null", "status": "No Pasto" }}

Regras:
- Se o usuário pede para registrar eventos, gere as actions correspondentes e explique o que será criado.
- Se for apenas uma pergunta, responda em "message" e deixe "actions" vazio.
- Para calcular data de parto previsto: data_realizacao_exame + (GESTACAO_DIAS - dias_fecundacao_no_toque).
- Para calcular dias de fecundação no momento do toque: (data_toque - data_fecundacao).days.
- Sempre confirme os dados que interpretou antes de sugerir a criação.
- Se faltar informação essencial, peça ao usuário.

CONTEXTO DO BANCO DE DADOS:
{context}
""".replace("{GESTACAO_DIAS}", str(GESTACAO_DIAS))


# ── endpoint ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY não configurada")

    try:
        import anthropic
    except ImportError:
        raise HTTPException(status_code=503, detail="SDK Anthropic não instalado")

    context = _build_context(db)
    system = SYSTEM_PROMPT.replace("{context}", context)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Monta histórico + mensagem atual
    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system,
            messages=messages,
        )
        raw = resp.content[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro na API Anthropic: {e}")

    # Parse JSON
    try:
        # Remove possível markdown ```json ... ```
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
    except Exception:
        # Fallback: trata como texto puro
        data = {"message": raw, "actions": []}

    return ChatResponse(
        message=data.get("message", raw),
        actions=[ActionItem(**a) for a in data.get("actions", [])],
    )


# ── endpoint de execução das ações confirmadas ────────────────────────────────

class ExecuteRequest(BaseModel):
    actions: list[ActionItem]

class ExecuteResponse(BaseModel):
    results: list[str]

@router.post("/execute", response_model=ExecuteResponse)
def execute_actions(req: ExecuteRequest, db: Session = Depends(get_db)):
    results = []

    for action in req.actions:
        p = action.payload

        if action.type == "create_exame_toque":
            exame = ExameToque(
                periodo_inicio=p["periodo_inicio"],
                periodo_fim=p["periodo_fim"],
                data_realizacao=p["data_realizacao"],
                veterinario=p.get("veterinario"),
            )
            db.add(exame)
            db.flush()
            results.append(f"Exame de toque criado: id={exame.id}, data={exame.data_realizacao}")

        elif action.type == "create_toque_resultado":
            matriz = db.query(Matriz).filter(
                Matriz.numero_registro == str(p["numero_registro"])
            ).first()
            if not matriz:
                results.append(f"ERRO: Matriz {p['numero_registro']} não encontrada")
                continue
            toque = ToqueMatriz(
                id_matriz=matriz.id,
                id_exame_toque=int(p["id_exame_toque"]),
                resultado=p["resultado"],
                dias_estimados_fecundacao=p.get("dias_estimados_fecundacao"),
                observacoes=p.get("observacoes"),
            )
            db.add(toque)
            results.append(
                f"Toque registrado: Matriz {p['numero_registro']} → {p['resultado']}"
                + (f" ({p.get('dias_estimados_fecundacao')} dias)" if p.get("dias_estimados_fecundacao") else "")
            )

        elif action.type == "create_cria":
            matriz = db.query(Matriz).filter(
                Matriz.numero_registro == str(p["numero_registro_matriz"])
            ).first()
            if not matriz:
                results.append(f"ERRO: Matriz {p['numero_registro_matriz']} não encontrada")
                continue
            cria = Cria(
                id_matriz=matriz.id,
                data_nascimento=p["data_nascimento"],
                sexo=p.get("sexo"),
                numero_registro=p.get("numero_registro_cria"),
                raca_pelagem=p.get("raca_pelagem"),
                pai=p.get("pai"),
                status=p.get("status", "No Pasto"),
            )
            db.add(cria)
            results.append(
                f"Cria registrada: Matriz {p['numero_registro_matriz']}, "
                f"nascimento {p['data_nascimento']}, sexo {p.get('sexo') or '?'}"
            )

        else:
            results.append(f"Ação desconhecida: {action.type}")

    db.commit()
    return ExecuteResponse(results=results)
