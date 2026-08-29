# Recomendação de Investimento Imobiliário — Itapema (SC)

**Para:** Seazone — onde e no que investir em short stay.
**Base:** 5 CSVs reais de Itapema (Airbnb: listings, hosts, geo, preço; VivaReal: venda).

---

## Resumo executivo

**Recomendo apartamentos compactos de 2 quartos em Morretes** (segunda opção: Tabuleiro dos Oliveiras), com **yield anual estimado de ~12,4%** e **payback de ~8 anos**.

A tese interna de que "studio/1 quarto no Centro é a aposta mais eficiente" é **parcialmente sustentada**: os dados confirmam que **compactos são eficientes**, mas **não no Centro** — Morretes e Tabuleiro entregam yield maior porque o preço de compra é mais baixo.

---

## 1. Critério e método

O desafio deixa "melhor" em aberto. **Critério definido:** rentabilidade (**yield anual** = receita líquida ÷ preço de compra) como métrica primária; receita bruta como secundária.

- **Receita anual** = ADR × 365 × ocupação, com ADR = **mediana** do preço diário por listing e **ocupação = 60%** (cenários 50/60/70% reportados).
- **Custo de aquisição** = `sale_price` do VivaReal, casado com Airbnb por **bairro + tipologia + nº de quartos** (mediana por grupo).
- **Custo anual** = 12 × condomínio + IPTU (mediana do grupo, quando disponível).

> ⚠️ **Limitação central dos dados:** apenas **999 de 4.441 listings** (~22%) têm preço. Toda a análise de receita/yield cobre esse subconjunto. O ranking é relativo (comparação entre grupos), então a ocupação de 60% não altera a ordem — só o valor absoluto do retorno.

---

## 2. Q1 — Melhor perfil de imóvel

Yield mediano por perfil (`listing_type` + nº de quartos), na média da cidade:

| Perfil | Yield mediano | n | Obs |
|---|---|---|---|
| casa 3Q | 14,6% | 14 | amostra pequena |
| casa 2Q | 13,4% | 17 | amostra pequena |
| **apartamento 2Q** | **12,5%** | 333 | ✅ robusto |
| **apartamento 1Q** | **12,5%** | 106 | ✅ robusto |
| apartamento 3Q | 8,0% | 390 | |
| apartamento 4Q | 6,2% | 68 | |

**Resposta:** entre os perfis com amostra robusta (n ≥ 100), **apartamentos compactos de 1–2 quartos** lideram (~12,5%). Casas têm yield nominalmente maior, mas amostras pequenas (n ≤ 17) e produto diferente do que a Seazone opera em escala.

> **Atenção:** o 12,5% acima é uma **média de cidade** — esconde a variação entre bairros. O número que realmente importa para decidir é o yield **por bairro** (seção 4).

---

## 3. Q2 — Melhor localização

**Por receita** (pergunta 2 fala em receita), o bairro vencedor é **Meia Praia**:

| Bairro | Receita média/listing (60%) | n |
|---|---|---|
| **Meia Praia** | **R$ 150.612** | 632 |
| Morretes | R$ 136.423 | 83 |
| Centro | R$ 131.411 | 205 |

Margem de Meia Praia sobre Morretes: **10,4%**.

**Por rentabilidade (yield), o ranking muda** — preço de compra menor em Morretes/Tabuleiro compensa a receita um pouco menor:

| Bairro | Yield mediano | Payback mediano |
|---|---|---|
| Tabuleiro dos Oliveiras | 13,3% | 7,5 anos |
| **Morretes** | **12,6%** | **8,0 anos** |
| Centro | 8,9% | 11,3 anos |
| Meia Praia | 7,8% | 12,8 anos |

---

## 4. Q4/Q5 — O que comprar e retorno estimado

**Recomendação: apartamento de 2 quartos em Morretes.**

Yield mediano do perfil (por bairro, T8):

| Perfil (bairro) | Yield | Payback | Preço ref. | n |
|---|---|---|---|---|
| **Morretes 2Q** | **12,4%** | **8,1 anos** | R$ 790.000 | 51 |
| Tabuleiro 2Q | 11,9% | 8,4 anos | R$ 780.000 | 12 |
| Meia Praia 1Q | 11,0% | 9,2 anos | R$ 877.500 | 20 |
| Centro 1Q | 10,3% | 9,7 anos | R$ 890.000 | 78 |

**Exemplo concreto (anúncio real do VivaReal):** apartamento de 67 m², 2 quartos, em Morretes, por **R$ 790.000**.

| Item | Valor |
|---|---|
| Preço de venda | R$ 790.000 |
| Receita bruta anual (60%) | R$ 101.616 |
| Custos (cond. R$ 300/mês + IPTU R$ 425/ano) | R$ 4.025 |
| Receita líquida | R$ 97.591 |
| **Yield** | **12,35%** |
| **Payback** | **8,1 anos** |

**Retorno por cenário de ocupação (Morretes):**

| Ocupação | Yield | Payback |
|---|---|---|
| 50% | 10,4% | 9,6 anos |
| 60% | 12,6% | 8,0 anos |
| 70% | 14,8% | 6,8 anos |

---

## 5. Q3 — Características que explicam as melhores receitas

Ordenado por impacto na receita (mediana):

1. **Nº de quartos** (impacto 111,8%) — mais quartos, mais receita (4Q rende ~2,6× mais que 1Q).
2. **Avaliação (star rating)** (98,1%) — com ressalva: listings "sem avaliação" têm mediana alta (n=22, viés de imóveis novos/premium).
3. **Nº de avaliações** (81,1%) — padrão inverso: menos reviews → receita maior (imóveis novos).
4. **Tipo de anúncio** (74,5%) — apartamento > casa > outros.
5. **Bairro** (43,8%).
6. **Superhost** (10,4%) — efeito fraco e contraintuitivo; não é driver confiável.

---

## 6. Posição sobre a tese

> **Tese:** "apartamentos compactos (studio/1 quarto) na região do Centro seriam a aposta mais eficiente."

**Parcialmente sustentada.**

- **Compactos: sustentado.** Apartamentos de 1–2 quartos entregam os melhores yields entre os perfis com amostra robusta (~12%, vs. 6–8% dos 3–4 quartos).
- **Centro: refutado.** O Centro rende menos em yield que Morretes e Tabuleiro (10,3% vs. 12,4%), porque o preço de compra no Centro (~R$ 890k para 1Q) é mais alto para uma receita parecida. **O que torna o investimento eficiente é o preço de compra baixo em bairros adjacentes à praia, não o Centro em si.**

---

## 7. Robustez e ressalvas

- **Outliers:** removidos (fora de [P1, P99]); o ranking do vencedor **não muda**.
- **Missing:** ~30% de condomínio e IPTU ausentes no VivaReal (mediana calculada sobre valores presentes).
- **Inconsistência de dado:** há anúncios com `suburb` e título divergentes (ex.: título "Meia Praia" com `suburb` "Centro"), e bairros com grafias múltiplas ("Sertão do Trombudo" vs. "Sertão Do Trombudo") — normalizados na análise.
- **Limitação:** 78% dos listings sem preço; se a distribuição de preço deles diferir da amostra, os rankings podem mudar.

---

*Relatório gerado a partir dos módulos em `src/invest/` (ver README para reproduzir).*
