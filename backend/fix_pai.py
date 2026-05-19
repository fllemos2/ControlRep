import sqlite3

conn = sqlite3.connect("cattle_control.db")
cur = conn.cursor()

# Popula pai a partir do brinco do reprodutor via id_reprodutor
n = cur.execute("""
    UPDATE crias
    SET pai = (
        SELECT reprodutores.brinco
        FROM reprodutores
        WHERE reprodutores.id = crias.id_reprodutor
    )
    WHERE id_reprodutor IS NOT NULL
      AND (pai IS NULL OR pai = '')
""").rowcount

conn.commit()

print(f"Pai preenchido em {n} registros.")

# Verificacao
total_pai = cur.execute("SELECT COUNT(*) FROM crias WHERE pai IS NOT NULL AND pai != ''").fetchone()[0]
total = cur.execute("SELECT COUNT(*) FROM crias").fetchone()[0]
print(f"Com pai: {total_pai} de {total}")

print("\nExemplos de pais distintos (top 10):")
for r in cur.execute("SELECT pai, COUNT(*) c FROM crias WHERE pai IS NOT NULL GROUP BY pai ORDER BY c DESC LIMIT 10").fetchall():
    print(" ", r)

conn.close()
