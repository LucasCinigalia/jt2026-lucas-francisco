# Skill utilizada: tlc-spec-driven

Skill de desenvolvimento orientado a especificação, usada para conduzir toda a análise deste projeto.

---

## O que é

A `tlc-spec-driven` (Tech Lead's Club — Spec-Driven Development) organiza o trabalho em 4 fases encadeadas, com profundidade adaptada à complexidade da tarefa:

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
  obrigatório     opcional       opcional     obrigatório
```

- **Specify** (obrigatório): definir O QUÊ construir — histórias de usuário, critérios de aceite (formato WHEN/THEN/SHALL), edge cases, assunções e rastreabilidade com IDs de requisito.
- **Design** (opcional): arquitetura e componentes, só para features grandes/complexas.
- **Tasks** (opcional): quebra em tarefas atômicas com dependências e comandos de verificação.
- **Execute** (obrigatório): implementar uma tarefa por vez — implementar → verificar (gate) → commit atômico.

## Auto-sizing (a profundidade segue a complexidade)

| Escopo | O que dispara |
|---|---|
| Small | ≤3 arquivos, spec de uma linha, executa direto |
| Medium | feature clara, spec breve |
| Large | multi-componente, spec + arquitetura + tarefas |
| Complex | ambiguidade/domínio novo, spec + discussão de áreas cinzentas |

**Este projeto foi classificado como Complex** (domínio novo, termos "melhor"/"perfil"/"localização" abertos).

## Regras críticas que guiaram o trabalho

1. **Testes derivam da spec**, não da implementação — cada critério de aceite vira uma verificação.
2. **Um commit atômico por tarefa** — nunca agrupar tarefas.
3. **O gate (verificação) decide**, não a autoavaliação do agente.
4. **Verifier sempre roda ao final** — validação independente (autor ≠ verificador), nunca opcional.
5. **Knowledge Verification Chain** — antes de decidir: código existente → docs → docs de libs → web → marcar como incerto. Nunca fabricar.

## Como foi aplicada aqui

1. **Specify** → `spec.md` com 8 histórias (P1/P2/P3), IDs `INV-01..08`, critérios WHEN/THEN, edge cases e tabela de assunções (critério "melhor" = yield, ocupação 60%, stack Python+pandas+DuckDB).
2. **Decisões confirmadas com o usuário** → yield como métrica primária; 60% de ocupação com cenários 50/60/70%; stack; "sem testes formais" (scripts + validação manual).
3. **Tasks** → `tasks.md` com 10 tarefas atômicas em 4 fases, matriz de cobertura de teste e comandos de gate.
4. **Execute** → 10 tarefas implementadas uma a uma, cada uma com commit atômico, verificação (gate = script rodando com exit 0 + saída esperada) e validação manual. A pedido do usuário, com **pausa antes de cada task** para confirmação.
5. **Verifier** → sub-agente independente (autor ≠ verificador) despachado ao final, que fez:
   - **Spec-anchored check**: mapeou cada critério de aceite a uma evidência `arquivo:linha`, conferindo se o valor corresponde ao resultado definido na spec.
   - **Discrimination sensor**: injetou 3 mutações de comportamento em estado descartável e confirmou que a análise é sensível às fórmulas (2 mortas, 1 sobreviveu por gap de observabilidade).
   - Resultado: **PASS ✅** (28/30 ACs, gate verde), com gaps acionáveis que foram corrigidos.

## Por que isso importa para a avaliação

A skill impôs o processo que o desafio quer ver: **rastreabilidade** (cada conclusão → um requisito → um número no CSV), **verificação independente** (não só a minha palavra), **commits atômicos** (histórico auditável) e **registro de decisões** (`.specs/STATE.md`, assunções, gaps).

---

*Os arquivos de processo ficam em `.specs/features/recomendacao-investimento-itapema/` (spec.md, tasks.md, validation.md).*
