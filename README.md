# 🐄 Cattle Control System

Sistema web intuitivo para controle de reprodução de gado Nelore, desenvolvido para facilitar a gestão de matrizes, crias, reprodutores e compradores através de linguagem natural e painéis visuais.

## 📋 Visão Geral

Este projeto transforma uma planilha Excel existente em uma aplicação web moderna, permitindo:
- ✅ Alimentação de dados por linguagem natural
- ✅ Consulta inteligente de informações
- ✅ Painéis de acompanhamento visual
- ✅ Relatórios exportáveis
- ✅ Interface intuitiva para usuários não-técnicos

## 🏗️ Arquitetura

### Backend (FastAPI)
- **Framework:** FastAPI com Python 3.9+
- **Banco:** SQLAlchemy + SQLite/PostgreSQL
- **Validação:** Pydantic v2
- **Documentação:** Swagger/OpenAPI automática

### Frontend (Planejado)
- **Framework:** Vue.js 3 + Composition API
- **UI:** Vuetify/Material Design
- **Estado:** Pinia
- **Build:** Vite

### Infraestrutura
- **Deploy:** Docker + Railway/Render
- **CI/CD:** GitHub Actions
- **Monitoramento:** Sentry (planejado)

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.9+
- Poetry (gerenciador de dependências)
- Git

### Setup Automático
```bash
# Clone o repositório
git clone <repository-url>
cd cattle-control

# Executar setup completo
python setup_dev.py
```

### Setup Manual
```bash
# Instalar dependências
cd backend
poetry install

# Criar banco de dados
poetry run python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"

# Iniciar desenvolvimento
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 📖 Uso

### Desenvolvimento
```bash
# Ativar ambiente virtual
cd backend && poetry shell

# Iniciar API
poetry run uvicorn app.main:app --reload

# Acessar documentação
# http://localhost:8000/docs
```

### Testes
```bash
# Executar suite completa
python run_tests.py

# Testes específicos
cd backend && poetry run python -m pytest tests/ -v
```

## 📁 Estrutura do Projeto

```
cattle-control/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── main.py         # Aplicação principal
│   │   ├── config.py       # Configurações
│   │   ├── models/         # SQLAlchemy models
│   │   │   ├── matriz.py
│   │   │   ├── cria.py
│   │   │   ├── reprodutor.py
│   │   │   ├── comprador.py
│   │   └── desempenho.py
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # Endpoints (TODO)
│   │   └── db/             # Database config
│   ├── tests/              # Testes (TODO)
│   ├── pyproject.toml      # Poetry dependencies
│   └── .env               # Environment variables
├── frontend/               # Vue.js app (TODO)
├── scripts/                # Utility scripts
├── docs/                   # Documentation
├── ROADMAP.md             # Development roadmap
├── DEV_CONFIG.md          # Development config
├── setup_dev.py           # Development setup script
├── run_tests.py           # Test runner
└── README.md             # This file
```

## 🗄️ Modelo de Dados

### Matrizes
- Identificação completa (nome, registro, etc.)
- Dados reprodutivos (cobertura, parto, etc.)
- Histórico de produção

### Crias
- Vinculação com matriz e reprodutor
- Dados de nascimento e desenvolvimento
- Controle sanitário

### Reprodutores
- Características genéticas
- Performance reprodutiva
- Histórico de coberturas

### Compradores
- Dados de contato
- Histórico de compras
- Preferências

### Desempenho
- Métricas de produção
- Indicadores econômicos
- Análises comparativas

## 🎯 Roadmap

### Semana 1 ✅ (Backend Core)
- [x] Models SQLAlchemy
- [x] Schemas Pydantic
- [x] API FastAPI básica
- [x] Configuração banco

### Semana 2 🔄 (Importação + Frontend)
- [ ] CRUD endpoints
- [ ] Script importação Excel
- [ ] Vue.js setup
- [ ] Interface básica

### Semana 3 ⏳ (NLP + Analytics)
- [ ] Processamento linguagem natural
- [ ] Painéis de acompanhamento
- [ ] Relatórios exportáveis

### Semana 4 ⏳ (Produção)
- [ ] Autenticação JWT
- [ ] Deploy produção
- [ ] Documentação completa

## 🧪 Qualidade e Testes

### Métricas
- **Cobertura Testes:** > 80%
- **Performance API:** < 500ms
- **Uptime:** > 99%

### Comandos de Teste
```bash
# Testes unitários
poetry run python -m pytest tests/ -v --cov=app --cov-report=html

# Testes de performance
poetry run python -m pytest tests/ -k "perf"

# Linting
poetry run black app/
poetry run isort app/
poetry run flake8 app/
```

## 🤝 Contribuição

### Processo de Desenvolvimento
1. **Daily Standup:** Reunião diária 9h e 17h
2. **Branches:** `feature/nome-funcionalidade`
3. **Commits:** Semânticos (`feat:`, `fix:`, `docs:`)
4. **PRs:** Code review obrigatório
5. **Merge:** Squash merge para master

### Padrões de Código
- **Python:** PEP 8 + Black
- **Commits:** Conventional Commits
- **Documentação:** Google Style docstrings
- **Testes:** pytest + fixtures

## 📊 Monitoramento

### Métricas Coletadas
- Performance API endpoints
- Uso de recursos (CPU/Memória)
- Taxa de erros
- Tempo de resposta

### Ferramentas
- **Logs:** Structured logging com JSON
- **Metrics:** Prometheus (planejado)
- **Alerts:** Discord webhooks
- **Dashboards:** Grafana (planejado)

## 🔒 Segurança

### Implementado
- Validação Pydantic em todos inputs
- CORS configurado
- Rate limiting básico
- Logs de segurança

### Planejado
- Autenticação JWT
- Autorização baseada em roles
- Encriptação dados sensíveis
- Auditoria de acessos

## 📚 Documentação

- [ROADMAP.md](ROADMAP.md) - Plano detalhado de desenvolvimento
- [DEV_CONFIG.md](DEV_CONFIG.md) - Configurações de desenvolvimento
- [API Docs](http://localhost:8000/docs) - Documentação interativa da API
- [Database Schema](docs/schema.md) - Esquema do banco de dados

## 🆘 Suporte

### Issues
- **Bug reports:** Template detalhado obrigatório
- **Feature requests:** Descrição clara + mockups
- **Questions:** GitHub Discussions

### Contato
- **Email:** [seu-email@exemplo.com]
- **Discord:** [link-servidor]
- **Issues:** [link-github-issues]

## 📄 Licença

Este projeto está sob a licença MIT. Ver [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido com ❤️ para facilitar a gestão de rebanhos Nelore**
- ReDoc: **http://localhost:8000/redoc**

### Database

Para desenvolvimento local, um banco SQLite é criado automaticamente em `sqlite:///./cattle_control.db`

Para produção com PostgreSQL:
```bash
# Criar database
createdb cattle_control

# Configurar .env com:
DATABASE_URL=postgresql://user:password@localhost/cattle_control

# Executar migrations (quando houver)
poetry run alembic upgrade head
```

## 📊 Modelos de Dados

### Matriz
- ID único, brinco, número registro
- Datas (nascimento, aquisição)
- Status (ativa, inativa, descartada)
- Histórico reprodutivo (total de crias, datas)

### Cria
- ID único, brinco, número registro
- Matriz (FK), Reprodutor (FK)
- Sexo, cor, pelagem
- Data nascimento
- Dados de venda (comprador, data, valor, peso)
- Índices de ganho

### Reprodutor
- ID único, brinco, número registro
- Dados de raça e pelagem
- Proveniência
- Histórico de uso (implícito via Crias)

### Comprador
- Nome, email, telefone
- Endereço (rua, cidade, UF, CEP)
- Histórico de compras (via Crias)

### Desempenho (Toque Veterinário)
- Matriz (FK)
- Data avaliação
- Mês de gestação, semana prevista
- Escore corporal
- Veterinário responsável

## 🔧 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para banco de dados
- **Pydantic** - Validação de dados
- **PostgreSQL/SQLite** - Banco de dados
- **Alembic** - Migrations

### Frontend (em breve)
- **Vue.js 3** - Framework JavaScript
- **Tailwind CSS** - Styling
- **Chart.js** - Gráficos
- **Axios** - HTTP client

### DevOps
- **Docker** - Containerização
- **Poetry** - Dependency management
- **GitHub Actions** - CI/CD

## 📝 Próximas Etapas

### Backend
- [ ] Implementar CRUD endpoints
- [ ] Criar CRUD base genérico
- [ ] Script de importação Excel
- [ ] Autenticação JWT
- [ ] Testes unitários
- [ ] Paginação e filtros
- [ ] Rate limiting

### Frontend
- [ ] Setup Vue.js 3
- [ ] Dashboard principal
- [ ] Formulários CRUD
- [ ] Chat input (NLP)
- [ ] Painéis de análise
- [ ] Exportação relatórios

### Integração
- [ ] Deploy AWS/Digital Ocean
- [ ] CI/CD pipeline
- [ ] Monitoramento
- [ ] Documentação API completa

## 📋 Roadmap Versão 1.0

### Sprint 1-2: MVP
- CRUD básico (Matrizes, Crias)
- Dashboard simples
- Testes básicos

### Sprint 3-4: Expansão
- CRUD completo
- NLP para entrada de dados
- Painéis avançados

### Sprint 5-6: Produção
- Importação Excel
- Exportação relatórios
- Deploy

## 🤝 Contribuindo

Este é um projeto em desenvolvimento. Sinta-se à vontade para sugerir melhorias e reportar bugs.

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato com o desenvolvedor.

---

**Última atualização:** 14/05/2026  
**Versão:** 0.1.0-beta
