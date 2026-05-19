import sys
sys.path.insert(0, ".")
from app.db.session import SessionLocal
from app.models.matriz import Matriz

AUSENTES = ["868", "890", "900", "928", "929", "951", "968", "986", "991"]

db = SessionLocal()
criadas = []
ja_existiam = []

for nr in AUSENTES:
    if db.query(Matriz).filter(Matriz.numero_registro == nr).first():
        ja_existiam.append(nr)
        continue
    db.add(Matriz(
        numero_registro=nr,
        brinco=nr,
        raca="Nelore",
        status="ativa",
    ))
    criadas.append(nr)

db.commit()
db.close()

print(f"Criadas ({len(criadas)}): {criadas}")
if ja_existiam:
    print(f"Ja existiam ({len(ja_existiam)}): {ja_existiam}")
print("Concluido.")
