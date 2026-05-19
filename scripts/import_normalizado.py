"""
Reimporta crias a partir do template normalizado.
ATENCAO: apaga TODOS os registros de crias antes de inserir.

Estrutura esperada (linha 1 = cabecalho):
  A: Reg. Nasc.       B: Raca/Pelagem     C: Sexo
  D: Data do Parto    E: Pai              F: Status
  G: Nr Reg. Matriz   H: Vendido para     I: Data da Venda
  J: Peso (@)         K: Preco Real

Uso:
    python scripts/import_normalizado.py --dry-run
    python scripts/import_normalizado.py --yes
"""

import os, sys, argparse
from datetime import datetime, date
from collections import Counter

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
os.chdir(BACKEND_DIR)
sys.path.insert(0, BACKEND_DIR)

import openpyxl
from app.db.session import SessionLocal
from app.models.cria import Cria
from app.models.matriz import Matriz
from app.models.comprador import Comprador

EXCEL = os.path.join(os.path.dirname(__file__), "..", "data", "crias_normalizado.xlsx")

RACAS_VALIDAS  = {"Nel. Branca", "Nel. Castanho", "Nel. Pintado"}

RACA_NORMALIZE = {
    "nel.branca":   "Nel. Branca",
    "nel.castanha": "Nel. Castanho",
    "nel.castanho": "Nel. Castanho",
    "nel.pintado":  "Nel. Pintado",
    "nel.pintada":  "Nel. Pintado",
    "nelore":       "Nel. Branca",
    "nel branca":   "Nel. Branca",
    "nel castanho": "Nel. Castanho",
    "nel pintado":  "Nel. Pintado",
}
SEXOS_VALIDOS  = {"M", "F"}
STATUS_VALIDOS = {"No Pasto", "Vendido", "Morto", "SUBMAT"}

STATUS_NORMALIZE = {
    "submat": "SUBMAT", "sub mat": "SUBMAT", "sub-mat": "SUBMAT",
    "vendido": "Vendido", "morto": "Morto", "no pasto": "No Pasto",
}

# Valores que devem ser tratados como ausente
NULOS = {"none", "nan", "-", "", "s/r", "n/a", "nao registrado",
         "não registrado", "sem registro", "sr"}


def to_date(val):
    if isinstance(val, (datetime, date)):
        return val.date() if isinstance(val, datetime) else val
    if isinstance(val, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(val.strip(), fmt).date()
            except ValueError:
                continue
    return None


def to_num(val):
    if val is None:
        return None
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def clean(val):
    if val is None:
        return None
    s = str(val).strip()
    return None if s.lower() in NULOS else s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", "-y", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(EXCEL):
        print(f"ERRO: arquivo nao encontrado em {os.path.abspath(EXCEL)}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 1. Leitura
    # ------------------------------------------------------------------
    wb = openpyxl.load_workbook(EXCEL, read_only=True, data_only=True)
    ws = wb["Crias"]

    erros = []
    avisos = []
    linhas = []
    reg_vistos = set()

    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or row[6] is None:   # Nr Reg. Matriz (col G) obrigatorio
            continue

        reg_nasc     = clean(row[0])
        raca_raw     = clean(row[1])
        raca         = RACA_NORMALIZE.get(raca_raw.lower(), raca_raw) if raca_raw else None
        sexo         = clean(row[2])
        data_parto_s = row[3]
        pai          = clean(row[4])
        status_raw   = clean(row[5]) or "No Pasto"
        status       = STATUS_NORMALIZE.get(status_raw.lower(), status_raw)
        reg_matriz   = clean(str(int(row[6])) if isinstance(row[6], float) else row[6])
        vendido_para = clean(row[7])  if len(row) > 7  else None
        data_venda_s = row[8]         if len(row) > 8  else None
        peso_venda   = to_num(row[9]  if len(row) > 9  else None)
        valor_venda  = to_num(row[10] if len(row) > 10 else None)

        # Validações
        linha_ok = True
        if raca and raca not in RACAS_VALIDAS:
            erros.append(f"Linha {i}: Raca invalida '{raca}'")
            linha_ok = False
        if sexo and sexo not in SEXOS_VALIDOS:
            erros.append(f"Linha {i}: Sexo invalido '{sexo}'")
            linha_ok = False
        if status not in STATUS_VALIDOS:
            erros.append(f"Linha {i}: Status invalido '{status}'")
            linha_ok = False

        data_parto = to_date(data_parto_s)
        if data_parto is None:
            erros.append(f"Linha {i}: Data do parto invalida '{data_parto_s}'")
            linha_ok = False

        data_venda = to_date(data_venda_s)
        if data_venda_s and data_venda is None:
            avisos.append(f"Linha {i}: Data da venda ignorada '{data_venda_s}'")

        if reg_nasc:
            if reg_nasc in reg_vistos:
                avisos.append(f"Linha {i}: Reg. Nasc. '{reg_nasc}' duplicado — segunda ocorrencia ignorada")
                reg_nasc = None
            else:
                reg_vistos.add(reg_nasc)

        if linha_ok:
            linhas.append({
                "linha": i, "reg_nasc": reg_nasc, "raca": raca,
                "sexo": sexo, "data_parto": data_parto, "pai": pai,
                "status": status, "reg_matriz": reg_matriz,
                "vendido_para": vendido_para, "data_venda": data_venda,
                "peso_venda": peso_venda, "valor_venda": valor_venda,
            })

    if erros:
        print(f"\n{len(erros)} linha(s) com erro serao puladas:")
        for e in erros[:20]:
            print(f"  {e}")
        if len(erros) > 20:
            print(f"  ... e mais {len(erros)-20} erros")
    if avisos:
        print(f"\n{len(avisos)} aviso(s):")
        for a in avisos[:10]:
            print(f"  {a}")

    print(f"\nRegistros validos para importar: {len(linhas)}")

    # ------------------------------------------------------------------
    # 2. Dry-run
    # ------------------------------------------------------------------
    if args.dry_run:
        status_cnt = Counter(l["status"] for l in linhas)
        raca_cnt   = Counter(l["raca"] for l in linhas if l["raca"])
        print("\nResumo:")
        print(f"  Por status:       {dict(status_cnt)}")
        print(f"  Por raca:         {dict(raca_cnt)}")
        print(f"  Com pai:          {sum(1 for l in linhas if l['pai'])}")
        print(f"  Com vendido_para: {sum(1 for l in linhas if l['vendido_para'])}")
        print(f"  Com data_venda:   {sum(1 for l in linhas if l['data_venda'])}")
        print(f"  Com valor_venda:  {sum(1 for l in linhas if l['valor_venda'])}")
        print("\nExecute sem --dry-run para aplicar.")
        return

    # ------------------------------------------------------------------
    # 3. Confirmação
    # ------------------------------------------------------------------
    print(f"\nATENCAO: todos os registros de crias serao apagados e {len(linhas)} inseridos.")
    if not args.yes:
        resp = input("Confirma? (s/N): ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            sys.exit(0)

    # ------------------------------------------------------------------
    # 4. Truncate + Insert
    # ------------------------------------------------------------------
    db = SessionLocal()
    try:
        matrizes_map    = {m.numero_registro: m.id for m in db.query(Matriz).all()}
        compradores_map = {c.nome: c.id for c in db.query(Comprador).all()}

        ausentes = {l["reg_matriz"] for l in linhas if l["reg_matriz"] not in matrizes_map}
        if ausentes:
            print(f"\nAVISO: {len(ausentes)} Nr. Reg. Matriz nao encontrados — crias dessas matrizes serao puladas:")
            for a in sorted(ausentes):
                print(f"  {a}")
            linhas = [l for l in linhas if l["reg_matriz"] in matrizes_map]
            print(f"Registros a inserir apos filtro: {len(linhas)}")

        deletados = db.query(Cria).delete()
        print(f"Apagados: {deletados} registros.")

        inseridos = 0
        reg_insert = set()

        for l in linhas:
            nr = l["reg_nasc"]
            if nr and nr in reg_insert:
                nr = None
            elif nr:
                reg_insert.add(nr)

            db.add(Cria(
                id_matriz       = matrizes_map[l["reg_matriz"]],
                numero_registro = nr,
                raca_pelagem    = l["raca"],
                sexo            = l["sexo"],
                data_nascimento = l["data_parto"],
                pai             = l["pai"],
                status          = l["status"],
                vendido_para    = l["vendido_para"],
                data_venda      = l["data_venda"],
                peso_venda      = l["peso_venda"],
                valor_venda     = l["valor_venda"],
                id_comprador    = compradores_map.get(l["vendido_para"]) if l["vendido_para"] else None,
            ))
            inseridos += 1
            if inseridos % 200 == 0:
                db.flush()
                print(f"  {inseridos} inseridos...")

        db.commit()
        print(f"Inseridos: {inseridos} registros.")
        print("Concluido.")

    except Exception as e:
        db.rollback()
        print(f"\nERRO: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
