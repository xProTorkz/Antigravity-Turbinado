# GOVERNANÇA DE WORKSPACE & ESCOPO CIRÚRGICO

Este documento define as regras de governança e isolamento operacional do **Antigravity Turbinado** dentro dos workspaces autorizados pelo usuário.

---

## 1. PRINCÍPIO DA DELIMITAÇÃO DE ESCOPO (SCOPE LOCK)

Toda tarefa executada no projeto deve ter seus caminhos autorizados explicitamente definidos em `allowed_scope` no Execution Packet:

```yaml
agent_task:
  allowed_scope:
    - src/
    - tests/
```

### Regras Operacionais:
1. **Minimal Necessary Diff:** O agente deve modificar estritamente os arquivos necessários para cumprir o escopo acordado na Issue.
2. **Zero Refatoração Oportunista:** É proibido alterar código, formatadores ou dependências fora do escopo aprovado.
3. **Isolamento de Diretórios & Autonomia Turbo:** O agente atua com foco prioritário de entrega dentro do workspace do projeto. No Modo Turbo, para permitir leitura de dependências globais, inspeção de ferramentas e execução contínua sem atritos, a política de IDE `nonWorkspaceFileAccessPolicy` opera em `AGENT_SETTING_POLICY_ALLOW` no escopo do usuário (home e tmp). Qualquer alteração de código fora do `allowed_scope` da tarefa é rejeitada na auditoria de entrega, e os limites de segurança de sistema são estritamente garantidos pelo sistema operacional (SIP/TCC no macOS; UAC/ACLs no Windows).

---

## 2. POLÍTICA ZERO SEGREDOS

Antes de qualquer commit ou sincronização com o GitHub, o diff é auditado contra vazamentos acidentais de credenciais:
- Chaves de API (OpenAI, Gemini, AWS, Stripe).
- Personal Access Tokens (PAT).
- Arquivos `.env` ou dumps de senhas.

Se qualquer padrão sensível for detectado, o commit deve ser cancelado imediatamente.

---

## 3. METODOLOGIA TEST BEFORE / TEST AFTER

Nenhuma alteração é considerada concluída sem evidência empírica:
1. **Baseline:** Captura do estado de testes e lint antes da alteração.
2. **Implementação:** Alteração cirúrgica dentro do `allowed_scope`.
3. **Validação:** Execução dos testes automatizados (pytest, vitest, npm test) garantindo ausência de regressões.
4. **Recibo de Entrega:** Registro do SHA e atualização do status no GitHub.
