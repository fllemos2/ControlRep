import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "cattle_control.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

cols = [r[1] for r in cur.execute("PRAGMA table_info(crias)").fetchall()]

if "status" not in cols:
    cur.execute("ALTER TABLE crias ADD COLUMN status VARCHAR DEFAULT 'No Pasto'")
    print("Coluna 'status' adicionada.")
else:
    print("Coluna 'status' já existe.")

if "pai" not in cols:
    cur.execute("ALTER TABLE crias ADD COLUMN pai VARCHAR")
    print("Coluna 'pai' adicionada.")
else:
    print("Coluna 'pai' já existe.")

# Registros com comprador cadastrado = Vendido
updated = cur.execute(
    "UPDATE crias SET status = 'Vendido' WHERE id_comprador IS NOT NULL AND (status IS NULL OR status = 'No Pasto')"
).rowcount
print(f"{updated} crias marcadas como 'Vendido'.")

conn.commit()
conn.close()
print("Migração concluída.")
