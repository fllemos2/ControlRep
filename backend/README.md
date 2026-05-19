# Cattle Breeding Control - Backend API

Sistema de API REST para gerenciar controle de reprodução de rebanho Nelore.

## Setup

```bash
# Instalar Poetry (se não tiver)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell

# Executar migrations (quando houver)
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

## Estrutura de Pastas

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI
│   ├── config.py            # Configurações
│   ├── core/
│   │   ├── security.py      # JWT, hash, etc
│   │   └── deps.py          # Dependências
│   ├── db/
│   │   ├── base.py          # Base declarativa SQLAlchemy
│   │   ├── session.py       # Engine e SessionLocal
│   │   └── init_db.py       # Inicialização DB
│   ├── models/
│   │   ├── __init__.py
│   │   ├── matriz.py        # Model Matriz
│   │   ├── cria.py          # Model Cria
│   │   ├── reprodutor.py    # Model Reprodutor
│   │   ├── comprador.py     # Model Comprador
│   │   └── desempenho.py    # Model Desempenho
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── matriz.py        # Pydantic schema
│   │   ├── cria.py
│   │   └── ...
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── api.py       # Router agregador
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── matrizes.py
│   │   │   │   ├── crias.py
│   │   │   │   └── ...
│   │   └── deps.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py          # CRUD base genérico
│   │   ├── matriz.py
│   │   ├── cria.py
│   │   └── ...
│   └── utils/
│       ├── __init__.py
│       ├── excel_importer.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── migrations/
│   └── env.py (alembic)
├── pyproject.toml
├── README.md
└── .env.example
```

## APIs Disponíveis

### Matrizes
- `GET /api/v1/matrizes` - Listar
- `GET /api/v1/matrizes/{id}` - Obter
- `POST /api/v1/matrizes` - Criar
- `PUT /api/v1/matrizes/{id}` - Atualizar
- `DELETE /api/v1/matrizes/{id}` - Deletar

### Crias
- `GET /api/v1/crias` - Listar
- `POST /api/v1/crias` - Criar
- Etc...

## Variáveis de Ambiente

Criar arquivo `.env` com:
```env
DATABASE_URL=postgresql://user:password@localhost/cattle_control
SECRET_KEY=sua-chave-secreta-muito-longa
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Documentação API

Depois de iniciar o servidor, acessar:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=app
```

## Database

### Criar Database PostgreSQL
```sql
CREATE DATABASE cattle_control;
CREATE USER cattle_user WITH PASSWORD 'senha';
ALTER ROLE cattle_user SET client_encoding TO 'utf8';
ALTER ROLE cattle_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE cattle_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE cattle_control TO cattle_user;
```

### Ou usar SQLite (desenvolvimento)
Database criado automaticamente em `sqlite:///./cattle_control.db`
