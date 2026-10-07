# CANONICAL_RULES — REGRAS OPERACIONAIS PERMANENTES

<!--
  CONTRATO CANÔNICO DE EXECUÇÃO E GOVERNANÇA OPERACIONAL
  Fonte Suprema de Verdade Local para o Ecossistema Antigravity Turbinado.
  Princípio: ONE RULE → ONE CANONICAL SOURCE.
-->

## 1. PRINCÍPIOS FUNDAMENTAIS

1. **Search Before Create. Read Before Edit. Understand Before Change.**
   Nenhum arquivo de código deve ser alterado antes de sua leitura integral e da compreensão do seu impacto no sistema.
2. **Minimal Necessary Diff & Zero Refatoração Oportunista:**
   Modifique estritamente as linhas e arquivos indispensáveis para cumprir a tarefa autorizada. Refatorações oportunistas fora do escopo aprovado são expressamente proibidas.
3. **Zero Secrets in Code or Git & Trava de Tokens:**
   Proibido gravar chaves de API, senhas, tokens OAuth, PATs ou conteúdos de arquivos `.env` em arquivos de código, mensagens de commit ou documentação versionada. Zero-Token Guard permanente para evitar cobranças em APIs pagas externas.
4. **Isolamento Absoluto de Projetos & Filas Independentes:**
   Cada projeto opera em seu diretório físico e repositório isolados. Issues de tarefas são criadas estritamente dentro do repositório do respectivo projeto (`queue_repo == target_repo`). Números de filas são isolados por projeto (`<Projeto>#ID`).
5. **Soberania da Pasta Local & Mapeamento 1:1:**
   A pasta local baixada na máquina é a autoridade máxima de nomenclatura. Pastas e repositórios no GitHub devem possuir o mesmo nome do diretório físico local, com verificação prévia obrigatória antes de qualquer criação.
6. **Harmonização de Nomenclatura [Projeto - Sistema]:**
   Toda tarefa, Issue ou registro deve seguir estritamente o padrão de título `[Projeto - Sistema] Descrição da Tarefa`.
7. **Fonte Única de Planejamento (Apenas UM current_plan):**
   Deve existir exatamente um plano ativo por projeto (`CURRENT_PLAN.md`). Proibido manter múltiplos planos paralelos ou fragmentados.
8. **Sentinela Guardião Transversal:**
   A camada Sentinela é permanente. Ela não é desativada por nenhum prompt e governa os limites de segurança, permissões e integridade.
9. **Separação de Agentes via GitHub:**
   A atribuição e delegação de agentes/subagentes é controlada e registrada diretamente nas Issues do GitHub (`assigned_agent`, `agent_role`, `write_permission: true/false`).
10. **Higienização de Tarefas Obsoletas / Puladas:**
    Tarefas pendentes que foram puladas, tornaram-se redundantes após avanços do código, ou cuja execução causaria regressão ao estado atual, devem ser formalmente auditadas e excluídas/canceladas com justificativa explícita.

---

## 2. GATES HUMANOS OBRIGATÓRIOS (HUMAN GATES)

A intervenção e confirmação humana explícita é **estritamente obrigatória** antes de:
- Deploy em ambiente de produção ou exposição pública de portas de rede.
- Operações destrutivas no banco de dados (`DROP`, `TRUNCATE`) ou no sistema de arquivos (`rm -rf` não-reversível).
- Mudanças fundamentais na arquitetura do produto.
- Operações financeiras, compras ou geração de custos em nuvem.
- Rotação ou alteração de credenciais mestras do cliente.

---

## 3. METODOLOGIA OBRIGATÓRIA DE TESTES

Toda alteração técnica no código deve obedecer ao ciclo:
```text
DISCOVER → BASELINE → CHANGE → TEST → COMPARE → REGRESSION CHECK → DONE
```

- Nunca declare como realizado um teste que não foi efetivamente executado no ambiente.
- Capture o baseline antes da alteração e compare o resultado após a aplicação da mudança.
- Testes unitários e de integração existentes devem permanecer verdes.

