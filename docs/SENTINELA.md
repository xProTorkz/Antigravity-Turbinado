# SENTINELA GUARDIÃO DE PROJETOS — CAMADA DE GOVERNANÇA

A **Sentinela** é o protocolo de blindagem e integridade operacional do Antigravity Turbinado. Ela opera como um guardião transversal em todas as tarefas, garantindo que o agente executor respeite fielmente o escopo, as regras do projeto e a segurança da sua máquina.

---

## 1. POR QUE A SENTINELA NÃO É UMA SKILL TÉCNICA COMUM?

- Uma skill técnica comum (ex: `@typescript`, `@docker`, `@python-test`) é uma ferramenta modular que o agente carrega para resolver um problema específico de código.
- A **Sentinela** é a camada de **governança e integridade imutável**. Ela está sempre ativa, não pode ser desativada por nenhum prompt ou instrução do usuário e opera como uma auditoria em tempo real sobre as ações do executor.

---

## 2. PILARES DE BLINDAGEM DA SENTINELA

```text
┌─────────────────────────────────────────────────────────────────┐
│                       SENTINELA GUARDIÃO                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. SCOPE LOCK: Bloqueia alterações fora de allowed_scope        │
│ 2. ZERO SEGREDOS: Escaneia diffs e bloqueia commits com tokens  │
│ 3. ISOLAMENTO DE PROJETOS: Falha fechado se tocar outro projeto │
│ 4. HUMAN GATES: Exige confirmação para ações de alto risco      │
│ 5. PRE_FLIGHT & POST_FLIGHT: Valida integridade antes e depois  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1. Scope Lock (Trava de Escopo Estrita)
Ao iniciar uma tarefa, a Issue define explicitamente os diretórios permitidos em `allowed_scope`.
Se o Antigravity tentar criar ou alterar qualquer arquivo fora desses caminhos:
- A Sentinela intercepta a operação.
- O arquivo é revertido imediatamente.
- A auditoria reporta `FILES_OUTSIDE_ALLOWED_SCOPE > 0`, impedindo a conclusão da tarefa.

### 2.2. Zero Segredos (Secret Scanning em Tempo Real)
Antes de qualquer commit ou sincronização com o GitHub, a Sentinela audita o diff em busca de:
- Chaves de API (OpenAI, Gemini, AWS, Stripe).
- Personal Access Tokens (PAT) do GitHub ou GitLab.
- Arquivos `.env` ou dumps de senhas.
Caso qualquer padrão de segredo seja detectado, o commit é cancelado na hora.

### 2.3. Pre-Flight e Post-Flight
- **PRE_FLIGHT:** Verifica se o repositório está limpo, se a branch está sincronizada com o `baseline_sha` e se as dependências básicas estão presentes.
- **POST_FLIGHT:** Executa os testes unitários e de integração, valida a ausência de regressões e confirma que o estado final atende a 100% dos critérios de aceite.
