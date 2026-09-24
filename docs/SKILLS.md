# GESTÃO & ROTEAMENTO DE SKILLS

O **Antigravity Turbinado** opera com um catálogo profissional de habilidades modulares especializadas, evitando o inchaço de contexto e garantindo máxima precisão em cada linha de código gerada.

---

## 1. COMPOSIÇÃO DO CATÁLOGO DE SKILLS

O ecossistema é estruturado em três níveis complementares:

| Nível | Localização | Quantidade | Propósito |
|---|---|---|---|
| **Skills Nativas Essenciais** | `~/.agents/skills/` | 100 | Habilidades técnicas completas e auto-contidas prontas para uso imediato em desenvolvimento web, mobile, backend, APIs e dados. |
| **Catálogo Extendido de Referência** | `projects/config/Skills` | 2.492 | Acervo de especialidades em infraestrutura, inteligência artificial, linguagens específicas e bancos de dados, consultadas sob demanda. |

---

## 2. COMPONENTE SKILL ROUTER & CURATOR (`scripts/skill_router.py`)

Diferente de sistemas que injetam milhares de instruções no prompt gerando alucinações e estouro de contexto, o Antigravity Turbinado utiliza o **Skill Router**:

1. **Descoberta Dinâmica:** Em tempo de execução, o script descobre as skills instaladas nas pastas canônicas sem números fixos ou hardcoded.
2. **Classificação Semântica da Tarefa:**
   - Analisa o título, tipo e descrição da Issue do GitHub.
   - Determina a categoria da tarefa (`TASK_CLASS`: frontend, backend, devops, security, database, etc.).
3. **Seleção de Mínimo Privilégio:**
   - Seleciona **apenas 1 `@skill` primária** indispensável para a tarefa.
   - Adiciona uma `@skill` de suporte secundária **somente se estritamente justificado**.
4. **Cálculo de Confiança:**
   - Se a confiança for igual ou superior a 80%, a skill é atribuída automaticamente no Execution Packet.
   - Se a confiança for inferior a 80%, o router define `SKILL_SELECTION=HUMAN_REVIEW` para validação pelo desenvolvedor.

---

## 3. EXEMPLO DE SAÍDA DO ROTEADOR

Ao processar uma tarefa como "Otimizar consultas lentas no PostgreSQL":

```text
TASK_CLASS=database
SKILL_PRIMARY=@sql-optimization
SKILL_SUPPORT=@postgres-dba
SKILL_SOURCE=native
CONFIDENCE=94%
CONTEXT_REQUIRED=minimal
FILES_HINT=db/queries.sql, db/indexes.sql
```

O Antigravity lê apenas o arquivo `SKILL.md` da skill selecionada, mantendo o restante do contexto 100% livre para o raciocínio do código da sua aplicação.
