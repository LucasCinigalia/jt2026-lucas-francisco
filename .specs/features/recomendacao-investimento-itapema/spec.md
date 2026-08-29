# Recomendação de Investimento Imobiliário — Itapema (SC)

## Problem Statement

A Seazone precisa decidir **onde e no que investir** na cidade de Itapema (SC), com base em dados reais do mercado (anúncios de short stay no Airbnb + anúncios de venda no VivaReal). O desafio pede uma recomendação de investimento defensável: qual o perfil de imóvel, qual a localização, quais características explicam as melhores receitas, e — se a empresa investisse hoje — o que compraria, com uma estimativa simples de retorno. A recomendação **deve tomar posição** sobre a tese preliminar de que "apartamentos compactos (studio/1 quarto) na região do Centro" são a aposta mais eficiente.

Os termos "melhor", "perfil" e "localização" são propositalmente abertos — esta spec **define o critério e o justifica**, tornando a decisão auditável.

## Goals

- [ ] Produzir uma recomendação de investimento escrita, com retorno estimado, que responda às 5 perguntas da missão e se posicione sobre a tese dos compactos no Centro.
- [ ] Basear 100% da recomendação em análise dos 5 CSVs fornecidos (nenhuma conclusão sem dado que a sustente).
- [ ] Deixar todo o processo reprodutível (código + instruções de execução no README).

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Modelo preditivo de preço/ocupacão (ML) | Não pedido; o desafio pede raciocínio de negócio, não machine learning. |
| Dashboard / app web interativo | Não é entregável do desafio; entregamos relatório + código. |
| Dados externos à base (IBGE, sazonalidade turística real, taxas de juros) | A base fornecida é o único insumo da análise; inferências externas são descartadas. |
| Previsão de valorização futura do imóvel | Fora do escopo de "estimativa simples de retorno". |
| Vídeo de 3 minutos | Entregável 2 do desafio, tratado à parte (não é código). |

---

## Assumptions & Open Questions

Cada ambiguidade foi resolvida com um critério definido ou registrada como assunção. Nada fica silenciosamente aberto.

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| **Critério de "melhor"** (Q1/Q4) | **Rentabilidade (yield anual)** = receita anual estimada ÷ preço de compra, como critério primário; **receita bruta anual** como secundário | "Investimento" = retorno sobre capital imobilizado, não faturamento. Yield compara perfis de preços diferentes de forma justa. | y |
| **Receita por localização** (Q2) | **Receita bruta anual** (total e média por bairro) + ADR (diária média) | A pergunta 2 fala explicitamente "em termos de receita", então aqui o critério é receita, não yield. | n |
| **Estimativa de receita anual** | `receita_anual = ADR × 365 × ocupação`, com ADR = mediana do preço diário por listing (de `Price_AV`) e **ocupação = 60%** (default) | A base não tem taxa de ocupação. 60% é benchmark usual de short stay no Brasil; a ocupação é uniforme entre grupos, então **não muda o ranking**, só o valor absoluto do retorno. | y |
| **Sensibilidade da ocupação** | Relatório deve mostrar retorno em 3 cenários (ex.: 50% / 60% / 70%) | Torna a decisão robusta a um pressuposto não observado. | n |
| **Custo de aquisição** | `sale_price` do VivaReal, comparado por `suburb` + tipologia/nº quartos | VivaReal é o mercado de compra; é o insumo de custo disponível. | n |
| **Custos operacionais no retorno** | Condomínio (`monthly_condo_fee`) e IPTU (`yearly_iptu`) descontados quando presentes; demais custos (gestão, manutenção, taxas) tratados como premissa única na narrativa | Estimativa "simples" conforme o desafio; não inventar precisão que os dados não têm. | n |
| **Stack** | Python 3.14 + pandas + DuckDB, scripts/notebooks versionados no repo | Reproduzível e auditável; `uv` disponível no ambiente. | y |
| **Deduplicação de listings** | Um `airbnb_listing_id` pode ter múltiplas capturas; consolidar pela captura mais recente (`aquisition_date`) | Evita dupla contagem de receita. | n |
| **Listings sem preço** | Excluídos da análise de receita, **contados e reportados** | Transparência sobre cobertura dos dados. | n |

**Open questions:** nenhuma — todas resolvidas ou registradas acima (aguardando confirmação do usuário).

---

## User Stories

### P1: Consolidação da base (ETL) ⭐ MVP

**User Story**: Como analista, quero uma base única e limpa que una listings, host, geolocalização e preço, para poder analisar sem inconsistências.

**Why P1**: Tudo depende de uma base confiável; é o alicerce das demais histórias.

**Acceptance Criteria**:

1. WHEN carregando os 5 CSVs THEN o sistema SHALL detectar automaticamente encoding e delimitador de cada arquivo e produzir um DataFrame por arquivo.
2. WHEN unindo os dados THEN cada `airbnb_listing_id` SHALL ter `suburb` (via Mesh), atributos do listing (via Details) e atributos do host (via Hosts) resolvidos por chave estrangeira.
3. WHEN houver múltiplas capturas do mesmo listing THEN o sistema SHALL manter a captura mais recente por `aquisition_date` e reportar quantas foram descartadas.
4. WHEN a consolidação terminar THEN o sistema SHALL reportar cobertura: nº de listings, nº sem bairro, nº sem preço, nº de hosts órfãos.

**Independent Test**: Rodar o script de ETL e inspecionar o relatório de cobertura + contagens de chaves.

---

### P1: Métrica de receita por listing ⭐ MVP

**User Story**: Como analista, quero uma estimativa de receita anual por listing, para poder comparar perfis e bairros.

**Why P1**: A receita é a variável-resposta central das perguntas 1–4.

**Acceptance Criteria**:

1. WHEN calculando ADR THEN o sistema SHALL usar a **mediana** do `price` por `airbnb_listing_id` (robusto a outliers).
2. WHEN calculando receita THEN `receita_anual = ADR × 365 × ocupação`, com ocupação default 60% e cenários 50%/60%/70% disponíveis.
3. WHEN um listing não tiver nenhuma linha de preço THEN ele SHALL ser marcado como `sem_receita` e excluído das agregações de receita (mas contado no relatório de cobertura).

**Independent Test**: Para um listing conhecido, conferir ADR e receita anual manualmente contra o CSV.

---

### P1: Melhor perfil de imóvel (Q1) ⭐ MVP

**User Story**: Como Seazone, quero saber qual perfil (tipologia, nº de quartos, tipo de anúncio) rende mais, para direcionar a originação.

**Why P1**: É a pergunta 1 da missão e o eixo da tese a testar.

**Acceptance Criteria**:

1. WHEN agregando por `listing_type` e `number_of_bedrooms` THEN o sistema SHALL produzir ranking por **rentabilidade (yield)** e por **receita bruta anual** (ambos, com mediana e média).
2. WHEN o perfil tiver menos de N listings (N=10) THEN o sistema SHALL sinalizá-lo como "amostra pequena" no ranking, para não decidir por ruído.
3. WHEN gerando o ranking THEN o sistema SHALL destacar explicitamente onde ficam os compactos (studio/1 quarto), para embasar a posição sobre a tese.

**Independent Test**: Conferir o ranking contra agregação manual de um subconjunto pequeno.

---

### P1: Melhor localização por receita (Q2) ⭐ MVP

**User Story**: Como Seazone, quero saber qual bairro gera mais receita, para priorizar onde comprar.

**Why P1**: Pergunta 2 da missão.

**Acceptance Criteria**:

1. WHEN agregando por `suburb` THEN o sistema SHALL produzir ranking por receita bruta total, receita média por listing e ADR médio.
2. WHEN um bairro tiver < N listings (N=10) THEN o sistema SHALL sinalizá-lo como "amostra pequena".
3. WHEN respondendo à pergunta THEN o sistema SHALL nomear o bairro vencedor e a margem sobre o segundo colocado.

**Independent Test**: Conferir ranking de bairros contra agregação manual.

---

### P1: Características que explicam receita (Q3) ⭐ MVP

**User Story**: Como Seazone, quero saber quais características (quartos, tipo, superhost, avaliação, bairro) mais se associam a receita alta, para fundamentar a decisão.

**Why P1**: Pergunta 3 da missão.

**Acceptance Criteria**:

1. WHEN analisando drivers THEN o sistema SHALL quantificar a associação de pelo menos: nº de quartos, `listing_type`, bairro, `is_superhost`, `star_rating`, nº de avaliações — com a receita estimada.
2. WHEN reportando drivers THEN o sistema SHALL ordenar as características por impacto na receita, com o valor do efeito (ex.: diferença de receita mediana entre categorias).
3. WHEN um efeito for nulo ou inconclusivo THEN o sistema SHALL dizê-lo explicitamente em vez de forçar uma conclusão.

**Independent Test**: Reproduzir a diferença de mediana de receita entre duas categorias manualmente.

---

### P1: Recomendação de investimento + retorno (Q4/Q5) ⭐ MVP

**User Story**: Como Seazone, quero uma recomendação concreta ("o que compraria hoje"), com estimativa de retorno, para agir.

**Why P1**: É o entregável final e a síntese de todas as perguntas.

**Acceptance Criteria**:

1. WHEN cruzando receita Airbnb com `sale_price` do VivaReal THEN o sistema SHALL estimar **yield anual** e **payback** por perfil/bairro (receita − condomínio − IPTU, quando disponíveis).
2. WHEN recomendando THEN o sistema SHALL indicar um perfil + bairro concretos e um exemplo real de anúncio de venda (do VivaReal) que o represente.
3. WHEN estimando retorno THEN o sistema SHALL apresentar yield e payback nos 3 cenários de ocupação.
4. WHEN concluindo THEN o sistema SHALL **tomar posição explícita sobre a tese** dos compactos no Centro (sustenta / refuta / sustenta parcialmente) e justificar com números.

**Independent Test**: Conferir yield/payback de um anúncio escolhido manualmente contra o CSV.

---

### P2: Qualidade e robustez da análise

**User Story**: Como avaliador, quero ver que a análise trata dados ruins (outliers, missing, duplicados) e testa a sensibilidade do pressuposto, para confiar na conclusão.

**Why P2**: Sustenta os 45% de "raciocínio e qualidade da análise" na avaliação.

**Acceptance Criteria**:

1. WHEN tratando outliers THEN o sistema SHALL definir e aplicar regra de outlier para `price` e `sale_price` (ex.: limite em percentil) e reportar quantos foram tratados.
2. WHEN avaliando missing THEN o sistema SHALL reportar o percentual de ausência por coluna-chave e a estratégia adotada.
3. WHEN testando sensibilidade THEN o sistema SHALL apresentar tabela de yield/payback por cenário de ocupação.

**Independent Test**: Rodar a análise com e sem tratamento de outlier e conferir que a conclusão não inverte sem justificativa.

---

### P3: Empacotamento da entrega (relatório + README + ai-log)

**User Story**: Como avaliador, quero abrir o repositório e entender como rodar e onde está a resposta, para avaliar.

**Why P3**: Necessário para a entrega ser avaliável (README "como rodar" + recomendação escrita).

**Acceptance Criteria**:

1. WHEN abrindo o repo THEN o README SHALL conter instruções de execução reproduzíveis (dependências + comandos) e o link para o relatório final.
2. WHEN lendo o relatório THEN ele SHALL conter a recomendação final escrita (as 5 respostas + posição sobre a tese) com os números de apoio.
3. WHEN olhando `ai-log/` THEN ele SHALL conter a conversa com a IA exportada em texto.

**Independent Test**: Clonar limpo, seguir o README e reproduzir os números do relatório.

---

## Edge Cases

- WHEN um CSV estiver vazio ou com header corrompido THEN o sistema SHALL falhar com mensagem clara (não silenciosamente).
- WHEN `suburb` estiver nulo em Mesh mas presente em Details/VivaReal THEN o sistema SHALL tentar preencher a partir da fonte alternativa antes de marcar como "sem bairro".
- WHEN um preço for 0 ou negativo THEN o sistema SHALL tratá-lo como inválido e excluí-lo da métrica, reportando a contagem.
- WHEN `sale_price` for nulo em VivaReal THEN o anúncio SHALL ser excluído do cálculo de yield, mas permanecer na análise de mercado.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| -------------- | ----- | ----- | ------ |
| INV-01 | P1: Consolidação (ETL) | Specify | Pending |
| INV-02 | P1: Métrica de receita | Specify | Pending |
| INV-03 | P1: Perfil (Q1) | Specify | Pending |
| INV-04 | P1: Localização (Q2) | Specify | Pending |
| INV-05 | P1: Drivers (Q3) | Specify | Pending |
| INV-06 | P1: Recomendação + retorno (Q4/Q5) | Specify | Pending |
| INV-07 | P2: Qualidade/robustez | Specify | Pending |
| INV-08 | P3: Empacotamento | Specify | Pending |

**Coverage:** 8 total, 0 mapped to tasks, 8 unmapped ⚠️

---

## Success Criteria

- [ ] A recomendação final responde às 5 perguntas com números da base e toma posição clara sobre a tese dos compactos no Centro.
- [ ] Toda conclusão tem um número de apoio rastreável até um CSV.
- [ ] O repositório reproduz os resultados seguindo o README (clone limpo).
- [ ] A sensibilidade da ocupação (3 cenários) está presente no relatório.
