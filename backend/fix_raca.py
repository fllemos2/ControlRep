import sqlite3

MAPA = {
    "nel.branca":   "Nel. Branca",
    "nel.castanha": "Nel. Castanho",
    "nel.castanho": "Nel. Castanho",
    "nel.pintado":  "Nel. Pintado",
    "nel.pintada":  "Nel. Pintado",
    "nelore":       "Nel. Branca",
}

conn = sqlite3.connect("cattle_control.db")
cur = conn.cursor()

for antigo, novo in MAPA.items():
    n = cur.execute(
        "UPDATE crias SET raca_pelagem = ? WHERE LOWER(raca_pelagem) = ?",
        (novo, antigo)
    ).rowcount
    if n:
        print(f"  '{antigo}' -> '{novo}': {n} registros")

conn.commit()

# Verificação final
print("\nDistribuição final:")
for r in cur.execute("SELECT raca_pelagem, COUNT(*) FROM crias WHERE raca_pelagem IS NOT NULL GROUP BY raca_pelagem ORDER BY 2 DESC").fetchall():
    print(" ", r)

conn.close()
print("\nConcluído.")
