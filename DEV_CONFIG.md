# 🚀 CATTLE CONTROL - CONFIGURAÇÃO DESENVOLVIMENTO

# Este arquivo contém configurações e atalhos para desenvolvimento

## 📁 ESTRUTURA DO PROJETO
# cattle-control/
# ├── backend/                 # API FastAPI
# │   ├── app/
# │   │   ├── main.py         # Aplicação principal
# │   │   ├── models/         # Modelos SQLAlchemy
# │   │   ├── schemas/        # Schemas Pydantic
# │   │   ├── api/            # Endpoints (TODO)
# │   │   ├── db/             # Configuração banco
# │   │   └── config.py       # Configurações
# │   ├── tests/              # Testes (TODO)
# │   ├── pyproject.toml      # Dependências Poetry
# │   └── .env                # Variáveis ambiente
# ├── frontend/               # Vue.js (TODO)
# ├── docs/                   # Documentação
# ├── scripts/                # Scripts utilitários
# └── ROADMAP.md              # Plano de desenvolvimento

## 🛠️ COMANDOS DE DESENVOLVIMENTO

### Setup Inicial
```bash
# Executar apenas uma vez
python setup_dev.py

# Ou manualmente:
cd backend
poetry install
poetry run python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### Desenvolvimento Diário
```bash
# Ativar ambiente virtual
cd backend
poetry shell

# Iniciar API em modo desenvolvimento
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Acessar documentação
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

### Testes
```bash
# Executar todos os testes
python run_tests.py

# Ou individualmente:
cd backend
poetry run python -m pytest tests/ -v
```

### Banco de Dados
```bash
# Resetar banco (cuidado!)
cd backend
poetry run python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"

# Ver tabelas criadas
poetry run python -c "from app.db.session import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('Tabelas:', inspector.get_table_names())"
```

## 🔧 CONFIGURAÇÕES IMPORTANTES

### Variáveis de Ambiente (.env)
```
DATABASE_URL=sqlite:///./cattle_control.db
API_V1_STR=/api/v1
PROJECT_NAME=Cattle Control API
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://localhost:5173"]
```

### Poetry (pyproject.toml)
- **Python:** ^3.9
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLAlchemy + SQLite/PostgreSQL
- **Validation:** Pydantic v2
- **Excel:** OpenPyXL

## 📊 MÉTRICAS DE QUALIDADE

### Código
- **Cobertura Testes:** > 80%
- **Complexidade:** < 10 (média por função)
- **Linhas por arquivo:** < 300

### Performance
- **Tempo resposta API:** < 500ms
- **Uptime:** > 99%
- **Memória:** < 512MB

### Segurança
- **Autenticação:** JWT (planejado)
- **Validação:** Pydantic em todos os inputs
- **CORS:** Configurado para desenvolvimento

## 🎯 ROADMAP ATUAL

### Semana 1 (Atual): Backend Core ✅
- [x] Models SQLAlchemy
- [x] Schemas Pydantic
- [x] API FastAPI básica
- [x] Configuração banco
- [ ] CRUD Endpoints (em progresso)

### Semana 2: Importação + Frontend
- [ ] Script importação Excel
- [ ] Vue.js setup
- [ ] Interface básica

### Semana 3: NLP + Analytics
- [ ] Processamento linguagem natural
- [ ] Painéis de acompanhamento
- [ ] Relatórios

### Semana 4: Produção
- [ ] Autenticação JWT
- [ ] Deploy
- [ ] Documentação final

## 🚨 PROBLEMAS CONHECIDOS

### Resolvidos
- ✅ Imports circulares nos models (TYPE_CHECKING)
- ✅ Encoding PowerShell para Excel
- ✅ Dependências Poetry configuradas

### Pendentes
- 🔄 CRUD endpoints não implementados
- 🔄 Script importação Excel pendente
- 🔄 Testes unitários básicos

## 💡 DICAS DE DESENVOLVIMENTO

### FastAPI
- Use `Depends()` para injeção de dependências
- Sempre valide inputs com Pydantic
- Use `response_model` nos endpoints
- Documente com docstrings

### SQLAlchemy
- Use `session.commit()` para salvar
- `session.refresh()` após insert
- Relationships lazy loading por padrão
- Use `selectinload` para eager loading

### Git
```bash
# Commits semânticos
git commit -m "feat: adicionar endpoint CRUD matrizes"
git commit -m "fix: corrigir validação schema cria"
git commit -m "docs: atualizar README instalação"
```

### Debugging
- Use `--reload` no uvicorn
- Logs em `app/main.py`
- PDB: `import pdb; pdb.set_trace()`
- Print statements temporários

## 📞 CONTATO / SUPORTE

- **Issues:** Criar no GitHub
- **Documentação:** Ver ROADMAP.md
- **Setup:** Executar `python setup_dev.py`

---

*Configuração atualizada: 14/05/2026*