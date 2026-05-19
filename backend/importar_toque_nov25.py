"""
Importa os resultados do Exame de Toque Nov/2025
Arquivo: data/Atualza Toque Nov-25.xlsx
Colunas: N. Reg | Toque (dias estimados de fecundação)
Todas as matrizes listadas = Cheia
"""
import sys, os
sys.path.insert(0, ".")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import openpyxl
from datetime import date
from app.db.session import SessionLocal
from app.models.matriz import Matriz
from app.models.exame_toque import ExameToque
from app.models.toque_matriz import ToqueMatriz

ARQUIVO = r"C:\01-Pessoais\01-ControleReprodução\data\Atualza Toque Nov-25.xlsx"

# Data de realização do exame (Nov/2025)
DATA_REALIZACAO  = date(2025, 11, 25)
PERIODO_INICIO   = date(2025, 2, 1)   # fertilização mais antiga (~270 dias antes)
PERIODO_FIM      = date(2025, 11, 25)
VETERINARIO      = None               # não informado no arquivo

db = SessionLocal()

# ── 1. Criar (ou reutilizar) o Exame de Toque ────────────────────────────────
exame = (
    db.query(ExameToque)
    .filter(ExameToque.data_realizacao == DATA_REALIZACAO)
    .first()
)
if not exame:
    exame = ExameToque(
        periodo_inicio=PERIODO_INICIO,
        periodo_fim=PERIODO_FIM,
        veterinario=VETERINARIO,
        data_realizacao=DATA_REALIZACAO,
    )
    db.add(exame)
    db.commit()
    db.refresh(exame)
    print(f"Exame criado  -> id={exame.id}  data={DATA_REALIZACAO}")
else:
    print(f"Exame existente -> id={exame.id}  data={DATA_REALIZACAO}")

# ── 2. Ler planilha ───────────────────────────────────────────────────────────
wb = openpyxl.load_workbook(ARQUIVO)
ws = wb.active

linhas = list(ws.iter_rows(min_row=2, values_only=True))   # pula cabeçalho
print(f"\n{len(linhas)} registros na planilha\n")

ok = err = skip = 0

for nr_reg, dias in linhas:
    if nr_reg is None:
        continue

    nr_str = str(int(nr_reg))
    matriz = db.query(Matriz).filter(Matriz.numero_registro == nr_str).first()
    if not matriz:
        print(f"  [SKIP] Matriz '{nr_str}' não encontrada")
        skip += 1
        continue

    dias_int = int(dias) if dias is not None else None

    # Remove toque anterior deste mesmo exame para esta matriz (evita duplicata)
    db.query(ToqueMatriz).filter(
        ToqueMatriz.id_matriz == matriz.id,
        ToqueMatriz.id_exame_toque == exame.id,
    ).delete()

    toque = ToqueMatriz(
        id_matriz=matriz.id,
        id_exame_toque=exame.id,
        resultado="Cheia",
        dias_estimados_fecundacao=dias_int,
    )
    db.add(toque)
    ok += 1
    print(f"  [OK] Matriz {nr_str:>5}  ->  Cheia  |  {dias_int} dias")

db.commit()
db.close()

print(f"\nConcluído: {ok} inseridos, {skip} não encontrados, {err} erros")
