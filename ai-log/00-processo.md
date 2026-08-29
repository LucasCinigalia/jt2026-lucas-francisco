# ai-log — Processo de trabalho com IA

Registro em texto do processo de análise. Ordem cronológica das iterações, decisões e correções.

---

## 1. Contexto e especificação

- Li o desafio (`README` + `index.html`) e a skill `tlc-spec-driven` (fluxo Specify → Design → Tasks → Execute).
- Especifiquei o problema em `.specs/features/recomendacao-investimento-itapema/spec.md`, com critérios definidos (o desafio deixa "melhor" aberto):
  - **"Melhor investimento" = yield anual** (receita ÷ preço de compra).
  - **Ocupação = 60%** (cenários 50/60/70%).
  - **ADR = mediana** do preço por listing.
- Quebrei em 10 tarefas (`.specs/.../tasks.md`) e executei uma por vez, com commit atômico.

## 2. Decisões de método (confirmadas com o usuário)

- Yield como métrica primária; receita bruta secundária.
- Ocupação 60% + 3 cenários.
- Stack: Python 3.14 + pandas + DuckDB (via `uv`).
- Sem testes formais: scripts que imprimem resultados, validação manual.

## 3. Descobertas sobre os dados

- **Só 999 de 4.441 listings têm preço (~22%)** — limitação central da análise.
- Details ↔ Mesh casam 1:1 (4.441 = 4.441); Hosts tem 1.383 snapshots duplicados (3.057 owners únicos).
- O número "4.529" inicial era erro de contagem (campos com `\n` embutidos); o real é **4.441**.
- VivaReal: bairros com grafias múltiplas (`MEIA PRAIA`, `Sertão Do Trombudo`, `Jardim Praia Mar`...) — normalizados.
- ~30% de condomínio/IPTU ausentes no VivaReal.

## 4. Bugs encontrados e corrigidos

1. **Dupla subtração de custo** no exemplo concreto do yield (T8): usei receita já líquida e subtraí condomínio/IPTU de novo. Corrigido para usar receita **bruta**. Verificado contra o CSV: yield 10,0% / payback 10,0 anos (@60%).
2. **Filtro de amostra mínima** ausente na checagem de estabilidade (T9): bairros com n<10 (Varzea, Sertão do Trombudo) apareciam como "vencedores". Corrigido para aplicar n≥10, alinhando com o ranking.
3. **Tipografia "TO" vs "T8"** na comunicação (corrigido pelo usuário).

## 5. Achados principais (resumo)

- **Q1:** apartamentos compactos 1–2Q lideram yield (~12,5% na média da cidade).
- **Q2:** Meia Praia vence em receita; Morretes/Tabuleiro vencem em yield.
- **Q3:** nº de quartos é o maior driver (111,8%), seguido de avaliação e nº de reviews; superhost é fraco.
- **Q4/Q5:** recomendação **Morretes 2Q** (yield 12,4%, payback ~8 anos, preço ~R$ 790k).
- **Tese:** parcialmente sustentada — compactos sim, Centro não.

## 6. Iterações de validação

- Verifiquei a fórmula do ADR manualmente (compute_adr == mediana manual).
- Verifiquei o exemplo concreto do yield contra as linhas do CSV.
- Validação de robustez: ranking estável sem outliers.

---

*Nota: este arquivo resume o processo. A sessão completa do OpenCode pode ser exportada em texto e adicionada a esta pasta (`ai-log/`) para auditoria total.*
