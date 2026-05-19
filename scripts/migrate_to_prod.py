"""
Migra dados do SQLite local para a API de produção.
Uso: python scripts/migrate_to_prod.py https://web-production-afb90.up.railway.app
"""
import sqlite3, sys, requests

PROD_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else "https://web-production-afb90.up.railway.app"
DB_PATH  = "backend/cattle_control.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

def api(method, path, **kwargs):
    r = requests.request(method, f"{PROD_URL}/api/v1{path}", **kwargs)
    if not r.ok:
        print(f"  ERRO {r.status_code}: {r.text[:200]}")
    return r

def rows(table, order="id"):
    cur = conn.execute(f"SELECT * FROM {table} ORDER BY {order}")
    return [dict(r) for r in cur.fetchall()]

def clean(d, *drop):
    """Remove campos calculados/autonull que a API não aceita no POST."""
    for k in drop:
        d.pop(k, None)
    # Remove None values para não sobrescrever defaults
    return {k: v for k, v in d.items() if v is not None}

# Mapas de ID local -> ID produção
rep_map, comp_map, mat_map, exam_map = {}, {}, {}, {}

# ── 1. Reprodutores ───────────────────────────────────────────────────────────
print("\n=== Reprodutores ===")
for r in rows("reprodutores"):
    local_id = r.pop("id")
    r.pop("created_at", None); r.pop("updated_at", None)
    res = api("POST", "/reprodutores/", json=clean(r))
    if res.ok:
        rep_map[local_id] = res.json()["id"]
        print(f"  {r['brinco']} -> id {rep_map[local_id]}")

# ── 2. Compradores ────────────────────────────────────────────────────────────
print("\n=== Compradores ===")
for r in rows("compradores"):
    local_id = r.pop("id")
    r.pop("created_at", None); r.pop("updated_at", None)
    res = api("POST", "/compradores/", json=clean(r))
    if res.ok:
        comp_map[local_id] = res.json()["id"]
        print(f"  {r['nome']} -> id {comp_map[local_id]}")

# ── 3. Matrizes ───────────────────────────────────────────────────────────────
print("\n=== Matrizes ===")
for r in rows("matrizes"):
    local_id = r.pop("id")
    r.pop("created_at", None); r.pop("updated_at", None)
    res = api("POST", "/matrizes/", json=clean(r))
    if res.ok:
        mat_map[local_id] = res.json()["id"]
        print(f"  {r['numero_registro']} -> id {mat_map[local_id]}")

# ── 4. Exames de Toque ────────────────────────────────────────────────────────
print("\n=== Exames de Toque ===")
for r in rows("exames_toque"):
    local_id = r.pop("id")
    r.pop("created_at", None); r.pop("updated_at", None)
    res = api("POST", "/exames-toque/", json=clean(r))
    if res.ok:
        exam_map[local_id] = res.json()["id"]
        print(f"  exame {local_id} -> id {exam_map[local_id]}")

# ── 5. Crias ──────────────────────────────────────────────────────────────────
print("\n=== Crias ===")
ok = err = 0
for r in rows("crias"):
    r.pop("id")
    r.pop("created_at", None); r.pop("updated_at", None)
    # Remapeia FKs
    if r.get("id_matriz"):
        r["id_matriz"] = mat_map.get(r["id_matriz"], r["id_matriz"])
    if r.get("id_reprodutor"):
        r["id_reprodutor"] = rep_map.get(r["id_reprodutor"], r["id_reprodutor"])
    if r.get("id_comprador"):
        r["id_comprador"] = comp_map.get(r["id_comprador"], r["id_comprador"])
    res = api("POST", "/crias/", json=clean(r))
    if res.ok: ok += 1
    else: err += 1
print(f"  {ok} ok, {err} erros")

# ── 6. Toques Matrizes ────────────────────────────────────────────────────────
print("\n=== Toques Matrizes ===")
ok = err = 0
for r in rows("toques_matrizes"):
    r.pop("id")
    r.pop("created_at", None); r.pop("updated_at", None)
    if r.get("id_matriz"):
        r["id_matriz"] = mat_map.get(r["id_matriz"], r["id_matriz"])
    if r.get("id_exame_toque"):
        r["id_exame_toque"] = exam_map.get(r["id_exame_toque"], r["id_exame_toque"])
    res = api("POST", "/toques-matrizes/", json=clean(r))
    if res.ok: ok += 1
    else: err += 1
print(f"  {ok} ok, {err} erros")

conn.close()
print("\nMigracao concluida")
