import sqlite3
conn = sqlite3.connect("cattle_control.db")

print("Total:", conn.execute("SELECT COUNT(*) FROM crias").fetchone()[0])
print("\nPor status:")
for r in conn.execute("SELECT status, COUNT(*) FROM crias GROUP BY status").fetchall():
    print(" ", r)

print("\nCom raca_pelagem:", conn.execute("SELECT COUNT(*) FROM crias WHERE raca_pelagem IS NOT NULL AND raca_pelagem != ''").fetchone()[0])
print("Com pai:", conn.execute("SELECT COUNT(*) FROM crias WHERE pai IS NOT NULL AND pai != ''").fetchone()[0])
print("Com sexo:", conn.execute("SELECT COUNT(*) FROM crias WHERE sexo IS NOT NULL").fetchone()[0])

print("\nExemplos de raca_pelagem distintas:")
for r in conn.execute("SELECT DISTINCT raca_pelagem FROM crias WHERE raca_pelagem IS NOT NULL LIMIT 10").fetchall():
    print(" ", r)

print("\nExemplos de No Pasto:")
for r in conn.execute("SELECT id, numero_registro, sexo, raca_pelagem, data_nascimento FROM crias WHERE status = 'No Pasto' LIMIT 5").fetchall():
    print(" ", r)

conn.close()
