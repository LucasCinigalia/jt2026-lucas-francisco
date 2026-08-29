# Recomendação de Investimento Itapema — Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute flow and Critical Rules.** Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor).

**If the skill cannot be activated, STOP and tell the user — do not proceed without it.**

---

**Spec**: `.specs/features/recomendacao-investimento-itapema/spec.md`
**Status**: Done

---

## Test Coverage Matrix

> Generated from codebase + user decision. **Guidelines found:** none — user chose "no formal tests" (scripts + manual validation). Strong default replaced by user decision: analysis scripts print deterministic results; verification is manual against spec ACs.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Data loading / ETL scripts | none (manual validation) | Script runs exit 0; prints coverage counts + key-resolution counts matching spec ACs | `src/invest/*.py` | `uv run python -m invest.<module>` |
| Analysis / metric scripts | none (manual validation) | Script runs exit 0; prints rankings/tables with the fields the spec ACs demand (winner named, sample-size flags, scenario table) | `src/invest/*.py` | `uv run python -m invest.<module>` |
| Report / docs | none | Files exist with required sections; repo reproducible via README | `relatorio.md`, `README.md` | manual review |

## Gate Check Commands

> Generated from codebase + user decision (no formal test runner).

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After each analysis-module task | `uv run python -m invest.<module>` (exit 0 + expected output) |
| Full | After tasks with cross-module dependencies | `uv run python -m invest.<module>` (exit 0 + expected output) |
| Build | After phase completion / final pipeline | `uv run python scripts/run_all.py` (exit 0, full output) |

---

## Execution Plan

Phases are ordered and run sequentially — each phase completes before the next begins, and tasks within a phase execute in order.

### Phase 1: Foundation (fundação do pipeline)

```
T1 → T2 → T3
```

### Phase 2: Metrics & Aggregations (receita e rankings)

```
T4 → T5 → T6 → T7
```

### Phase 3: Recommendation & Robustness (recomendação + robustez)

```
T8 → T9
```

### Phase 4: Packaging (entrega)

```
T10
```

---

## Task Breakdown

### T1: Setup do projeto Python

**What**: Criar `pyproject.toml` (pandas + duckdb), estrutura de pastas `src/invest/`, `scripts/`, e instalar dependências com `uv`.
**Where**: `pyproject.toml`, `src/invest/__init__.py`, `scripts/`
**Depends on**: None
**Reuses**: N/A (greenfield)
**Requirement**: INV-01 (base), suporte a todas as histórias

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] `uv run python -c "import pandas, duckdb"` sai com exit 0
- [ ] `src/invest/__init__.py` existe e o pacote é importável
- [ ] `data/` é acessível pelos scripts

**Tests**: none
**Gate**: build — `uv run python -c "import pandas, duckdb; print('ok')"`

---

### T2: Módulo de carregamento (load)

**What**: `load.py` com funções que detectam encoding/delimitador e carregam os 5 CSVs em DataFrames, com fallback de `suburb` (Mesh → VivaReal), conforme Edge Cases da spec.
**Where**: `src/invest/load.py`
**Depends on**: T1
**Reuses**: N/A
**Requirement**: INV-01

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] `load.py` carrega os 5 arquivos com exit 0
- [ ] Imprime contagem de linhas/colunas por arquivo (espelha: Details 4441, Hosts 4440, Mesh 4441, Price 118839, VivaReal 8329)
- [ ] CSV vazio/header corrompido → falha com mensagem clara (Edge Case)
- [ ] Detecção de encoding/delimitador é automática

**Tests**: none
**Gate**: quick — `uv run python -m invest.load`

---

### T3: Consolidação (ETL)

**What**: `etl.py` que une Details + Mesh + Hosts por chave estrangeira, deduplica listings pela captura mais recente (`aquisition_date`), e gera relatório de cobertura.
**Where**: `src/invest/etl.py`
**Depends on**: T2
**Reuses**: `load.py`
**Requirement**: INV-01

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] Cada `airbnb_listing_id` tem `suburb` (Mesh), atributos de listing (Details) e de host (Hosts) resolvidos
- [ ] Dedup mantém a captura mais recente e reporta quantas linhas foram descartadas
- [ ] Relatório de cobertura imprime: nº de listings, nº sem bairro, nº sem preço, nº de hosts órfãos
- [ ] Suburb nulo preenchido por fonte alternativa antes de marcar "sem bairro" (Edge Case)

**Tests**: none
**Gate**: quick — `uv run python -m invest.etl`

---

### T4: Métrica de receita por listing

**What**: `revenue.py` que calcula ADR (mediana do `price` por listing) e receita anual (`ADR × 365 × ocupação`), com ocupação default 60% e cenários 50/60/70%.
**Where**: `src/invest/revenue.py`
**Depends on**: T3
**Reuses**: `etl.py`
**Requirement**: INV-02

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] ADR usa mediana (robusto a outlier)
- [ ] `receita_anual = ADR × 365 × ocupação`; cenários 50/60/70% disponíveis
- [ ] Listing sem preço marcado `sem_receita` e excluído das agregações (contado no relatório)
- [ ] Preço 0/negativo tratado como inválido e reportado (Edge Case)
- [ ] Imprime estatísticas descritivas da receita (nº listings com receita, mediana/média)

**Tests**: none
**Gate**: quick — `uv run python -m invest.revenue`

---

### T5: Melhor perfil de imóvel (Q1)

**What**: `profile.py` que agrega por `listing_type` + `number_of_bedrooms` e gera ranking por yield e por receita bruta anual, com flag de amostra pequena (N<10) e destaque dos compactos (studio/1 quarto). Inclui helper `market.py` (acesso ao VivaReal) exigido pelo cálculo de yield.
**Where**: `src/invest/profile.py`, `src/invest/market.py`
**Depends on**: T4
**Reuses**: `revenue.py`, `load.py`
**Requirement**: INV-03

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] Ranking por yield (mediana + média) e por receita bruta anual (mediana + média)
- [ ] Perfis com <10 listings sinalizados "amostra pequena"
- [ ] Compactos (studio/1 quarto) destacados no ranking
- [ ] Imprime o ranking ordenado de forma legível (tabela)

**Tests**: none
**Gate**: quick — `uv run python -m invest.profile`

---

### T6: Melhor localização por receita (Q2)

**What**: `location.py` que agrega por `suburb` e gera ranking por receita bruta total, receita média por listing e ADR médio, com flag de amostra pequena.
**Where**: `src/invest/location.py`
**Depends on**: T4
**Reuses**: `revenue.py`
**Requirement**: INV-04

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] Ranking por receita total, receita média por listing e ADR médio
- [ ] Bairros com <10 listings sinalizados "amostra pequena"
- [ ] Nomeia o bairro vencedor e a margem sobre o 2º colocado
- [ ] Imprime ranking legível

**Tests**: none
**Gate**: quick — `uv run python -m invest.location`

---

### T7: Características que explicam receita (Q3)

**What**: `drivers.py` que quantifica a associação de nº de quartos, `listing_type`, bairro, `is_superhost`, `star_rating`, nº de avaliações com a receita estimada, ordenando por impacto.
**Where**: `src/invest/drivers.py`
**Depends on**: T4
**Reuses**: `revenue.py`
**Requirement**: INV-05

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] Associação quantificada para pelo menos: quartos, listing_type, bairro, superhost, star_rating, nº avaliações
- [ ] Características ordenadas por impacto, com valor do efeito (diferença de mediana entre categorias)
- [ ] Efeito nulo/inconclusivo declarado explicitamente (não forçar conclusão)
- [ ] Imprime tabela de drivers ordenada

**Tests**: none
**Gate**: quick — `uv run python -m invest.drivers`

---

### T8: Recomendação + retorno (Q4/Q5)

**What**: `investment.py` que cruza receita Airbnb com `sale_price` do VivaReal (por suburb + tipologia/quartos), calcula yield anual e payback (receita − condomínio − IPTU), e seleciona um anúncio exemplo representativo.
**Where**: `src/invest/investment.py`
**Depends on**: T5, T6, T7
**Reuses**: `revenue.py`, `profile.py`, `location.py`
**Requirement**: INV-06

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] Yield anual e payback estimados por perfil/bairro (descontando condomínio + IPTU quando presentes)
- [ ] Indica perfil + bairro concretos e um anúncio VivaReal real representativo
- [ ] Yield/payback nos 3 cenários de ocupação
- [ ] `sale_price` nulo excluído do yield mas mantido na análise de mercado (Edge Case)
- [ ] Imprime tabela de yield/payback por perfil/bairro + cenários

**Tests**: none
**Gate**: full — `uv run python -m invest.investment`

---

### T9: Robustez da análise

**What**: `robustness.py` que aplica regra de outlier em `price`/`sale_price` (percentil), reporta missing por coluna-chave, e monta tabela de sensibilidade de yield/payback por cenário de ocupação.
**Where**: `src/invest/robustness.py`
**Depends on**: T4, T8
**Reuses**: `revenue.py`, `investment.py`
**Requirement**: INV-07

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] Regra de outlier definida e aplicada; nº de tratados reportado
- [ ] Percentual de missing por coluna-chave reportado + estratégia
- [ ] Tabela de sensibilidade yield/payback por cenário de ocupação
- [ ] Imprime relatório de robustez legível

**Tests**: none
**Gate**: quick — `uv run python -m invest.robustness`

---

### T10: Empacotamento da entrega

**What**: `scripts/run_all.py` (pipeline completo), `relatorio.md` (recomendação final escrita com as 5 respostas + posição sobre a tese), `README.md` (como rodar + link do relatório) e pasta `ai-log/`.
**Where**: `scripts/run_all.py`, `relatorio.md`, `README.md`, `ai-log/`
**Depends on**: T8, T9
**Reuses**: todos os módulos
**Requirement**: INV-08

**Tools**:
- MCP: NONE
- Skill: NONE

**Done when**:
- [ ] `scripts/run_all.py` roda o pipeline completo com exit 0
- [ ] `relatorio.md` contém as 5 respostas + posição sobre a tese, com números de apoio
- [ ] `README.md` tem instruções reproduzíveis (dependências + comandos) e link do relatório
- [ ] `ai-log/` contém a conversa com a IA exportada em texto

**Tests**: none
**Gate**: build — `uv run python scripts/run_all.py`

---

## Phase Execution Map

```
Phase 1 → Phase 2 → Phase 3 → Phase 4

Phase 1:  T1 ──→ T2 ──→ T3
Phase 2:  T4 ──→ T5 ──→ T6 ──→ T7
Phase 3:  T8 ──→ T9
Phase 4:  T10
```

Execution is strictly sequential — there is no intra-phase parallelism. A single agent (or batch worker) works one task at a time, in order.

**Packing (for sub-agent offer):** 10 tasks → Batch 1 = Phase 1 + Phase 2 (7 tasks), Batch 2 = Phase 3 + Phase 4 (3 tasks).

---

## Task Granularity Check

| Task | Scope | Status |
| ---- | ----- | ------ |
| T1: setup + pyproject | 1 file + scaffolding | ✅ Granular |
| T2: load.py | 1 module | ✅ Granular |
| T3: etl.py | 1 module | ✅ Granular |
| T4: revenue.py | 1 module | ✅ Granular |
| T5: profile.py | 1 module | ✅ Granular |
| T6: location.py | 1 module | ✅ Granular |
| T7: drivers.py | 1 module | ✅ Granular |
| T8: investment.py | 1 module | ✅ Granular |
| T9: robustness.py | 1 module | ✅ Granular |
| T10: run_all + relatório + README + ai-log | 1 script + 3 docs | ⚠️ Cohesive (final packaging) |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| ---- | ---------------------- | ------------- | ------ |
| T1 | None | (no inbound) | ✅ Match |
| T2 | T1 | T1 → T2 | ✅ Match |
| T3 | T2 | T2 → T3 | ✅ Match |
| T4 | T3 | T3 → T4 | ✅ Match |
| T5 | T4 | T4 → T5 | ✅ Match |
| T6 | T4 | T4 → T6 | ✅ Match |
| T7 | T4 | T4 → T7 | ✅ Match |
| T8 | T5, T6, T7 | T5/T6/T7 → T8 | ✅ Match |
| T9 | T4, T8 | T8 → T9 | ✅ Match |
| T10 | T8, T9 | T9 → T10 | ✅ Match |

## Test Co-location Validation

> Matrix requires "none" for all layers (user decision: no formal tests). Every task declares `Tests: none`.

| Task | Code Layer | Matrix Requires | Task Says | Status |
| ---- | ---------- | --------------- | --------- | ------ |
| T1 | project scaffolding | none | none | ✅ OK |
| T2 | data loading script | none | none | ✅ OK |
| T3 | ETL script | none | none | ✅ OK |
| T4 | metric script | none | none | ✅ OK |
| T5 | analysis script | none | none | ✅ OK |
| T6 | analysis script | none | none | ✅ OK |
| T7 | analysis script | none | none | ✅ OK |
| T8 | analysis script | none | none | ✅ OK |
| T9 | analysis script | none | none | ✅ OK |
| T10 | docs/scripts | none | none | ✅ OK |
