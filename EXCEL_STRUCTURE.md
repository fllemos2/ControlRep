# EXCEL STRUCTURE - DETAILED ANALYSIS

## ABA 1: CRIAS (1014 registros)
**Headers em linha 4, dados iniciam linha 5**

| Col | Header | Tipo | Descrição |
|-----|--------|------|-----------|
| 1 | ID_System | VARCHAR | Identificador único sistema (ex: 871-I) |
| 2 | Matriz | INTEGER | Número da matriz geradora |
| 3 | N. de Ordem | INTEGER | Ordem de nascimento |
| 4 | Reg.Nasc. | INTEGER | Registro nascimento |
| 5 | Raça Pelagem | VARCHAR | Raça e cor (ex: Nelore) |
| 6 | Sexo | CHAR(1) | M ou F |
| 7 | Data Parto | DATE | Data nascimento (formato Excel date) |
| 8 | Pai | VARCHAR | Reprodutor (Pai) |
| 9 | Matriz_Ref | INTEGER | Referência matriz |
| 10 | Origem | VARCHAR | Origem da cria |
| 11 | Vendido para | VARCHAR | Nome comprador |
| 12 | Observação | TEXT | Observações |
| 13 | Data da venda | DATE | Data venda |
| 14 | Peso (@) | DECIMAL | Peso em arrobas |
| 15 | Preço Real | DECIMAL | Preço unitário |
| 16 | Sócios | VARCHAR | Sócios envolvidos |
| 17 | Peso | DECIMAL | Peso (repetido?) |
| 18 | Indice de Ganho | DECIMAL | Índice ganho peso |
| 19 | (em branco) | - | - |

---

## ABA 2: MATRIZES (149 registros)
**Headers em linha 4, dados iniciam linha 5**

| Col | Header | Tipo | Descrição |
|-----|--------|------|-----------|
| 1 | Ant | VARCHAR | Antigo/Anterior |
| 2 | Nº Ord. | INTEGER | Número ordem |
| 3 | Nº Reg. | INTEGER | Número registro |
| 4 | 1ª Cria | DATE | Data primeira cria |
| 5 | ULT. Cria | DATE | Data última cria |
| 6 | Meses + 9,5 Meses | DECIMAL | Meses entre parições |
| 7 | Nº Crias | INTEGER | Total de crias |
| 8 | Meses/Cria | DECIMAL | Meses por cria (intervalo) |
| 9 | OBS | TEXT | Observações |
| 10-13 | (em branco) | - | - |

---

## ABA 3: DESEMPENHO (233 registros)
**Header em linha 2 ou 3**
- Muitas colunas dinâmicas (16384 = máximo Excel)
- Conteúdo: Avaliação de toque veterinário
- Estrutura: Provavelmente matriz vs datas de avaliação em colunas

**Campos esperados:**
- Matriz ID
- Data avaliação
- Mês gestação
- Semana prevista nascimento
- Escore corporal
- Veterinário
- Observações

---

## ABA 4: COMPRADORES (21 registros)
**3 colunas, 21 linhas**
- Provavelmente: Nome, Telefone, Email ou similar

---

## ABA 5: PLAN1 (5 registros)
**Aba auxiliar - Investimento/Retorno**
Colunas: Invest/Retorno, Data, Períodos (Mês), Acum, Rend

---

## PROBLEMAS IDENTIFICADOS NO EXCEL

1. **Headers espalhados** - Não seguem padrão (linha 1, 3, 4)
2. **Formatação inconsistente** - Títulos em colunas diferentes
3. **Dados mistos** - Valores calculados junto com dados brutos
4. **Sem relacionamentos explícitos** - FKs implícitas
5. **Datas em formato Excel** - Números (ex: 39625 = data serial)
6. **Dados incompletos** - Muitos campos vazios nas linhas iniciais

---

## ESTRATÉGIA DE MIGRAÇÃO

### 1. LIMPEZA & TRANSFORMAÇÃO
- [ ] Converter datas Excel para formato padrão (YYYY-MM-DD)
- [ ] Normalizar valores NULL/vazios
- [ ] Validar tipos de dados
- [ ] Remover linhas duplicadas/inválidas

### 2. MAPEAMENTO DE ENTIDADES
```
EXCEL → DATABASE

Matrizes.Nº Reg → matrizes.numero_registro
Crias.Matriz → crias.id_matriz
Crias.Pai → crias.id_reprodutor
Crias.Data Parto → crias.data_nascimento
Crias."Vendido para" → crias.id_comprador + vendas.data
```

### 3. IMPORTAÇÃO FASEADA
- Fase 1: Matrizes (referência)
- Fase 2: Reprodutores (caso não existam)
- Fase 3: Crias (com FK para matrizes)
- Fase 4: Vendas (com FK para crias)
- Fase 5: Desempenho (histórico)

---

## SCRIPT DE IMPORTAÇÃO NECESSÁRIO

Será necessário criar script Python que:
1. Lê Excel com `openpyxl`
2. Valida e transforma dados
3. Insere em banco SQLAlchemy
4. Registra erros/avisos
5. Gera relatório de importação

---

*Análise completada: 14/05/2026*
