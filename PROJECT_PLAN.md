# Plano de Projeto: Aplicação Web de Controle de Reprodução de Rebanho

## 📋 Visão Geral

Transformar o sistema existente em Excel para uma **aplicação web moderna** que permite:
- ✅ Entrada de dados por linguagem natural (chat-based)
- ✅ Visualização de painéis de acompanhamento
- ✅ Exportação de relatórios
- ✅ Interface amigável para usuários com pouca experiência digital

---

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue.js 3)                     │
│  - Dashboard intuitivo                                      │
│  - Chat input com NLP                                       │
│  - Gráficos e painéis                                       │
│  - Responsivo (móvel + desktop)                             │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS REST API
┌────────────────────▼────────────────────────────────────────┐
│              Backend (FastAPI + Python)                     │
│  - Autenticação & Autorização                               │
│  - NLP para processamento de linguagem natural              │
│  - APIs RESTful CRUD                                        │
│  - Lógica de negócios                                       │
│  - Relatórios & Exportações                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ SQL Queries
┌────────────────────▼────────────────────────────────────────┐
│            Database (PostgreSQL/SQLite)                     │
│  - Tabelas: Matrizes, Crias, Reprodutores, Desempenho      │
│  - Integridade referencial                                  │
│  - Índices otimizados                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Schema do Banco de Dados

### Tabela: `matrizes`
```sql
id                  INTEGER PRIMARY KEY
brinco              VARCHAR(50) UNIQUE NOT NULL
nome                VARCHAR(255)
data_nascimento     DATE
raca                VARCHAR(50) DEFAULT 'Nelore'
data_aquisicao      DATE
status              ENUM('ativa', 'inativa', 'descartada')
observacoes         TEXT
created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at          TIMESTAMP
```

### Tabela: `crias`
```sql
id                  INTEGER PRIMARY KEY
id_matriz           INTEGER FOREIGN KEY -> matrizes(id)
id_reprodutor       INTEGER (referência a reprodutor)
sexo                CHAR(1) ('M' ou 'F')
cor                 VARCHAR(50)
data_nascimento     DATE NOT NULL
brinco              VARCHAR(50)
peso_nascimento     DECIMAL(5,2)
id_comprador        INTEGER FOREIGN KEY -> compradores(id)
data_venda          DATE
valor_venda         DECIMAL(10,2)
observacoes         TEXT
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### Tabela: `desempenho` (Toque Veterinário)
```sql
id                  INTEGER PRIMARY KEY
id_matriz           INTEGER FOREIGN KEY -> matrizes(id)
data_avaliacao      DATE NOT NULL
mes_gestacao        SMALLINT
semana_provavel     SMALLINT
escore_corporal     DECIMAL(3,1)
veterinario         VARCHAR(255)
observacoes         TEXT
created_at          TIMESTAMP
```

### Tabela: `reprodutores`
```sql
id                  INTEGER PRIMARY KEY
brinco              VARCHAR(50) UNIQUE NOT NULL
nome                VARCHAR(255)
data_nascimento     DATE
raca                VARCHAR(50) DEFAULT 'Nelore'
proveniencia        VARCHAR(255)
observacoes         TEXT
```

### Tabela: `compradores`
```sql
id                  INTEGER PRIMARY KEY
nome                VARCHAR(255) NOT NULL
telefone            VARCHAR(20)
email               VARCHAR(255)
endereco            TEXT
cidade              VARCHAR(100)
uf                  CHAR(2)
data_cadastro       DATE
observacoes         TEXT
```

---

## 🎯 Funcionalidades Principais

### Módulo 1: Cadastro & Manutenção de Dados

**Via Chat (NLP):**
- "Registrar nova matriz 2025"
- "Adicionar cria nascida hoje, matriz 2025, reprodutor 2018, fêmea"
- "Atualizar dados da matriz 2025: compra em 01/01/2020"
- "Registrar toque veterinário matriz 2025, 3 meses de gestação"

**Via Formulário (UI Tradicional):**
- CRUD completo para Matrizes
- CRUD para Crias
- CRUD para Reprodutores
- CRUD para Compradores
- Registro de Desempenho

### Módulo 2: Painéis de Acompanhamento (Dashboards)

- **Dashboard Principal**
  - Total de matrizes (ativas/inativas)
  - Crias nascidas (mês/ano)
  - Matrizes em gestação
  - Faturamento do período
  - Gráfico de tendências

- **Matriz Individual**
  - Histórico reprodutivo
  - Todas as crias geradas
  - Status de gestação atual
  - Timeline visual

- **Análises**
  - Taxa de parição
  - Idade média do rebanho
  - Valor médio de venda
  - Reprodutores mais usados

### Módulo 3: Relatórios & Exportação

- Relatório de Desempenho de Matrizes (Excel/PDF)
- Listagem de Crias para Venda (com fotos opcionais)
- Histórico de Compras/Vendas
- Análise Financeira
- Exportação em Excel, PDF, CSV

### Módulo 4: Administração

- Usuários e permissões
- Backup de dados
- Histórico de alterações (audit log)
- Configurações gerais

---

## 💻 Stack Tecnológico

### Frontend
- **Framework:** Vue.js 3 (Composition API)
- **UI Components:** Tailwind CSS + shadcn/vue ou PrimeVue
- **Charts:** Chart.js ou Plotly
- **NLP Input:** Rasa NLU ou spaCy via API
- **Versionamento:** Git/GitHub

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy
- **NLP:** spaCy + Rasa NLU  
- **Autenticação:** JWT + bcrypt
- **Validação:** Pydantic
- **Background Tasks:** Celery + Redis
- **API Docs:** Swagger/OpenAPI

### Database
- **Primary:** PostgreSQL (produção)
- **Dev:** SQLite (desenvolvimento local)
- **Migrations:** Alembic

### DevOps
- **Containerização:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Hosting:** AWS/Digital Ocean/Heroku (a decidir)
- **Monitoring:** Sentry para erros

---

## 📅 Roadmap Sugerido

### Fase 1 (Sprint 1-2): MVP Básico
- [ ] Setup projeto (Backend + Frontend)
- [ ] Schema DB e migrations
- [ ] CRUD básico de Matrizes
- [ ] CRUD básico de Crias
- [ ] Dashboard simples

### Fase 2 (Sprint 3-4): Expansão
- [ ] NLP para entrada de dados (MVP)
- [ ] CRUD Desempenho
- [ ] Painéis mais completos
- [ ] Autenticação de usuários

### Fase 3 (Sprint 5-6): Relatórios & Finishes
- [ ] Sistema de relatórios
- [ ] Exportações (Excel, PDF)
- [ ] Refinamento NLP
- [ ] Testes e otimizações

### Fase 4: Produção
- [ ] Deploy
- [ ] Documentação
- [ ] Treinamento do usuário
- [ ] Suporte e manutenção

---

## 🔧 Próximos Passos

1. **Análise Detalhada do Excel**
   - Extrair headers exatos de cada aba
   - Identificar todas as colunas e tipos de dados
   - Documentar validações e regras de negócio

2. **Design do Schema**
   - Refinar modelo de dados
   - Definir relacionamentos
   - Criar script SQL de inicialização

3. **Prototipar Interface**
   - Wireframes/mockups
   - Decidir sobre cores e fontes
   - Definir user flows

4. **Iniciar Desenvolvimento**
   - Setup do repositório
   - Scaffold Backend
   - Scaffold Frontend
   - Primeiro commit

---

## 📝 Notas Importantes

- **Backup:** Manter backups regulares de dados
- **Auditoria:** Rastrear todas as mudanças (quem, quando, o quê)
- **Mobile:** Priorizar responsividade
- **Velocidade:** Interface deve ser rápida e fluida
- **Idioma:** Portuguese (Brazil) - pt_BR

---

*Documento criado: 14/05/2026*  
*Última atualização: 14/05/2026*
