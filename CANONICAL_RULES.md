# CANONICAL_RULES — REGRAS OPERACIONAIS PERMANENTES

<!--
  CONTRATO CANÔNICO DE EXECUÇÃO E GOVERNANÇA OPERACIONAL
  Fonte Suprema de Verdade Local para o Ecossistema Antigravity Turbinado.
  Princípio: ONE RULE → ONE CANONICAL SOURCE.
-->

## 1. PRINCÍPIOS FUNDAMENTAIS

1. **Search Before Create. Read Before Edit. Understand Before Change.**
   Nenhum arquivo de código deve ser alterado antes de sua leitura integral e da compreensão do seu impacto no sistema.
2. **Minimal Necessary Diff:**
   Modifique estritamente as linhas e arquivos indispensáveis para cumprir a tarefa autorizada. Refatorações oportunistas fora do escopo aprovado são expressamente proibidas.
3. **Zero Secrets in Code or Git:**
   Proibido gravar chaves de API, senhas, tokens OAuth, PATs ou conteúdos de arquivos `.env` em arquivos de código, mensagens de commit ou documentação versionada.
4. **Isolamento Absoluto de Projetos:**
   Cada projeto opera em seu diretório e repositório isolados. Mutações cruzadas entre projetos diferentes falham imediatamente em modo fechado (Fail-Closed).
5. **Sentinela Guardião Transversal:**
   A camada Sentinela é permanente. Ela não é desativada por nenhum prompt e governa os limites de segurança, permissões e integridade.

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
