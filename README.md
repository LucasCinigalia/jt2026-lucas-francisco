🔗 **Vídeo (até 3 min):** [INSERIR LINK DO GOOGLE DRIVE AQUI — compartilhar como "qualquer pessoa com o link"]

# Hackathon Jovens Talentos AI Builder 2026 — Itapema (SC)

Recomendação de investimento imobiliário para a Seazone, construída com IA.

## Resposta final

> **Recomendação:** apartamentos compactos de **2 quartos em Morretes** (yield ~12,4%, payback ~8 anos). Tese dos compactos no Centro: **parcialmente sustentada** (compactos sim, Centro não).

A recomendação completa está em **[`relatorio.md`](relatorio.md)**.

## Como rodar

Requisitos: `uv` (ou Python 3.10+ com `pip`).

```bash
# 1. Instalar dependências (pandas)
uv sync

# 2. Rodar o pipeline completo
uv run python scripts/run_all.py

# 3. (Opcional) Rodar cada etapa individualmente
uv run python -m invest.load        # carrega os 5 CSVs
uv run python -m invest.etl         # consolida + cobertura
uv run python -m invest.revenue     # ADR e receita anual
uv run python -m invest.profile     # Q1 — perfil (yield/receita)
uv run python -m invest.location    # Q2 — bairro (receita)
uv run python -m invest.drivers     # Q3 — drivers de receita
uv run python -m invest.investment  # Q4/Q5 — yield, payback, tese
uv run python -m invest.robustness  # outliers, missing, sensibilidade
```

## Estrutura

- `data/` — os 5 CSVs do desafio (não modificados).
- `src/invest/` — módulos da análise (um por etapa).
- `scripts/run_all.py` — pipeline completo.
- `relatorio.md` — recomendação final escrita.
- `ai-log/` — conversas com a IA em texto.
- `.specs/` — especificação e tarefas (processo spec-driven).

## Dados

Snapshot estático do mercado imobiliário de Itapema (SC): anúncios de Airbnb e de venda (VivaReal).

| Arquivo | Conteúdo |
|---|---|
| `Details_Itapema.csv` | Anúncios Airbnb (título, quartos, tipo, owner_id) |
| `Hosts_ids_Itapema.csv` | Dados do host (superhost, reviews, anos) |
| `Mesh_Ids_Data_Itapema.csv` | Lat/long + bairro |
| `Price_AV_Itapema.csv` | Preço por anúncio/dia |
| `VivaReal_Itapema.csv` | Anúncios de venda (preço, condomínio, área) |
