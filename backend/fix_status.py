import sys
sys.path.insert(0, ".")
from app.db.session import SessionLocal
from app.models.matriz import Matriz

db = SessionLocal()

morta_kw = ["morreu", "sacrificada", "perdida no bambuzal", "mor.", "morr."]
descartada_kw = ["descart"]

updated_morta = []
updated_descartada = []

matrizes = db.query(Matriz).all()
for m in matrizes:
    obs = (m.observacoes or "").lower()
    if any(kw in obs for kw in morta_kw):
        if m.status != "morta":
            m.status = "morta"
            updated_morta.append(m.numero_registro)
    elif any(kw in obs for kw in descartada_kw):
        if m.status != "descartada":
            m.status = "descartada"
            updated_descartada.append(m.numero_registro)

db.commit()
print(f"Mortas atualizadas ({len(updated_morta)}): {updated_morta}")
print(f"Descartadas atualizadas ({len(updated_descartada)}): {updated_descartada}")
db.close()
