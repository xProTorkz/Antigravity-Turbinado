# PROMPT MESTRE — CLOUD-FIRST AI ORCHESTRATION + GITHUB BRAIN + ANTIGRAVITY EXECUTOR

## ORDEM PRINCIPAL

Não criar apenas mais um `LLMProviderRegistry`.

O objetivo desta tarefa é consolidar a arquitetura global do ecossistema para que:

```text
ChatGPT = leitura, compreensão, planejamento e interação com o usuário

GitHub = cérebro operacional, memória técnica, contexto estruturado,
fonte de verdade, decomposição de tarefas e contratos de execução

Antigravity = executor puro e especializado

Cloud AI Providers = inteligência especializada sob demanda

Mac = cliente/orquestrador leve, NÃO servidor de LLM
```

Princípio central:

```text
PENSAR ANTES → ESTRUTURAR → REGISTRAR NO GITHUB → ENTREGAR PACKET MÍNIMO → EXECUTAR
```

Antigravity NÃO deve gastar recursos:

- lendo repositório inteiro;
- descobrindo novamente arquitetura;
- interpretando conversas enormes;
- procurando sozinho quais arquivos alterar;
- reconstruindo decisões já tomadas;
- analisando Issues históricas irrelevantes;
- selecionando contexto desnecessário.

Ele deve receber uma tarefa praticamente pronta para execução.

---

# 1. DECISÃO ARQUITETURAL — NÃO USAR LLM LOCAL

A arquitetura anterior que utilizava Qwen/OpenJarvis local deve permanecer disponível apenas onde já for necessário para compatibilidade do Jarvis até migração posterior.

Para:

- resumo de conversa;
- planejamento;
- reasoning;
- compilação de tarefas;
- geração de conteúdo;
- classificação sofisticada;
- pesquisa;
- visão;
- vídeo;
- workloads especializados;

NÃO utilizar o Mac M1 como host de modelos.

O Mac possui recursos limitados e deve funcionar como:

```text
CLIENT
CONTROL SURFACE
VOICE SURFACE
LOCAL EXECUTION ENDPOINT
```

e não como:

```text
LLM SERVER
GPU INFERENCE HOST
MODEL FARM
```

Toda inferência pesada deve preferencialmente ocorrer na nuvem.

---

# 2. ARQUITETURA FINAL PRETENDIDA

```text
USUÁRIO
   ↓
ChatGPT / Jarvis / Siri / Alexa / UI
   ↓
CONTEXT RESOLVER
   ↓
PROJECT RESOLVER
   ↓
GitHub SOURCE OF TRUTH
   ↓
TASK COMPILER
   ↓
AI / WORKLOAD ROUTER
   ↓
PROVEDOR MAIS ADEQUADO
   ↓
EXECUTION PACKET
   ↓
GitHub Issue agent_task v5
   ↓
Sentinela PRE-FLIGHT
   ↓
Antigravity
   ↓
EXECUÇÃO CIRÚRGICA
   ↓
Testes
   ↓
Sentinela POST-FLIGHT
   ↓
Commit / estado / GitHub
```

---

# 3. RESPONSABILIDADES — NÃO MISTURAR

## ChatGPT

Responsabilidades:

- conversar com o usuário;
- interpretar intenção;
- pesquisar quando necessário;
- entender o contexto atual;
- comparar alternativas;
- planejar;
- decidir quais informações precisam ser recuperadas;
- entregar uma especificação clara.

ChatGPT não é executor local.

---

## GitHub

GitHub deve ser o CÉREBRO OPERACIONAL do ecossistema.

Não apenas repositório.

Deve armazenar de maneira estruturada:

- arquitetura;
- decisões;
- estado;
- tarefas;
- dependências;
- projeto alvo;
- arquivos alvo;
- testes relevantes;
- risco;
- skills;
- contexto mínimo;
- baseline;
- resultado esperado;
- resultado obtido;
- histórico de execução.

Fluxo ideal:

```text
ChatGPT entende
      ↓
GitHub estrutura/persiste
      ↓
Antigravity recebe somente o necessário
```

---

## Antigravity

Antigravity é o executor.

Seu trabalho deve começar quando a análise já terminou.

Idealmente, um Execution Packet deve informar:

```text
PROJECT
REPOSITORY
WORKSPACE
BASELINE_SHA
TASK_ID
SKILL
ALLOWED_SCOPE

FILES_TO_READ
FILES_TO_MODIFY
FILES_NOT_TO_TOUCH

CURRENT_BEHAVIOR
TARGET_BEHAVIOR

EXACT_IMPLEMENTATION_OBJECTIVE

ACCEPTANCE_CRITERIA

TESTS_TO_RUN

KNOWN_RISKS

ROLLBACK

GITHUB_ISSUE
```

Antigravity não deve precisar descobrir isso novamente.

---

# 4. IMPLEMENTAR CONTEXT PACKETS NO GITHUB

Antes de despachar qualquer tarefa, o sistema deve gerar um `Execution Context Packet`.

Ele NÃO precisa obrigatoriamente ser um novo arquivo permanente.

Primeiro auditar se o `agent_task v5`, `execution_brief`, Issue body, Task Protocol ou estruturas existentes já suportam isso.

Prioridade:

```text
REUSE
>
EXTEND
>
CREATE
```

O packet deve conter apenas contexto relevante para aquela tarefa.

Exemplo conceitual:

```yaml
execution_context:

  project: antigravity-control-plane

  architecture_summary:
    - Router = única autoridade de despacho
    - Antigravity = único executor
    - Sentinela = governança

  files_to_read:
    - jarvis_backend/reasoner.py
    - ag_control_plane/llm_provider.py

  files_to_modify:
    - ag_control_plane/llm_provider.py

  forbidden_scope:
    - dispatcher.py
    - architecture locks

  task:
    Implementar adapter OpenRouter compatível com ProviderRegistry.

  tests:
    - tests/test_llm_provider.py
```

Objetivo:

Antigravity não deve carregar 100 arquivos para modificar 1.

---

# 5. MULTI-AI CLOUD-FIRST

Criar uma abstração mínima e extensível de provedores de IA.

Não acoplar o sistema exclusivamente a OpenAI.

Arquitetura:

```text
AIProviderRegistry
        │
        ├── OpenAI
        ├── OpenRouter
        ├── Together
        ├── Fireworks
        ├── RunPod Endpoint
        ├── Google Gemini
        ├── Google Video/Veo
        └── futuros provedores
```

Não implementar todos imediatamente.

Criar interface suficientemente genérica para permitir novos adapters.

---

# 6. WORKLOAD ROUTING

Separar:

```text
PROJECT ROUTING
```

de:

```text
AI WORKLOAD ROUTING
```

O Router canônico continua sendo a única autoridade operacional.

O AI Router serve apenas para escolher inteligência/modelo.

Categorias iniciais:

```text
engineering

reasoning

research

summarization

copywriting

marketing

creative

vision

image

video

audio

fast

cheap

high_quality

long_context

privacy_sensitive
```

Não associar automaticamente uma categoria a um fornecedor específico para sempre.

Usar policy configurável.

---

# 7. NÃO TENTAR “DESBLOQUEAR” CHATGPT

Não modificar, contornar ou tentar neutralizar políticas internas da OpenAI, Google ou qualquer outro fornecedor.

O sistema deve obter flexibilidade pela arquitetura:

```text
PROVIDER CHOICE
MODEL CHOICE
OPEN MODEL CHOICE
SELF-HOSTED CLOUD CHOICE
```

Se determinado workload não for adequado para um provedor:

```text
NÃO FORÇAR O PROVEDOR
```

Selecionar outro serviço/modelo cujo contrato e política permitam esse uso.

Isso deve ser tratado como:

```text
PROVIDER POLICY COMPATIBILITY
```

e não como:

```text
FILTER BYPASS
JAILBREAK
CENSORSHIP BYPASS
```

---

# 8. NICHOS DIFERENTES

O sistema deve conseguir lidar com vários segmentos comerciais sem amarrar a arquitetura a um nicho.

Exemplos:

```text
fashion

beauty

tattoo

fitness

dating

nightlife

adult-oriented marketing

gaming

gambling-related analysis

finance

software

ecommerce

education

health
```

Cada provedor poderá ter restrições próprias.

Criar capability/policy metadata.

Exemplo conceitual:

```yaml
provider_capabilities:

  provider_x:

    text:
      true

    image:
      true

    video:
      false

    long_context:
      true

    supported_workloads:
      - engineering
      - marketing

    policy_profile:
      provider_managed
```

Não codificar regras de evasão de filtros.

---

# 9. PESQUISA DE PROVEDORES

Antes de fixar provedores adicionais, executar benchmark.

Pesquisar pelo menos:

```text
OpenRouter
Together AI
Fireworks AI
RunPod
Google Gemini
Google Veo
Google Colab
Cloud GPU providers adicionais
```

Avaliar:

```text
PREÇO

QUALIDADE

LATÊNCIA

CONTEXT WINDOW

RATE LIMIT

OPEN WEIGHTS

API

SERVERLESS

COLD START

PRIVACIDADE

LOG RETENTION

REGION

MULTIMODAL

VISION

IMAGE

VIDEO

AUDIO

TERMOS DE USO

RESTRIÇÕES POR WORKLOAD
```

---

# 10. PESQUISA ATUAL — PONTOS A REVALIDAR

Na pesquisa realizada em setembro de 2026:

OpenRouter oferece centenas de modelos e dezenas de provedores sob uma API compatível.

Há camada gratuita limitada e modelos gratuitos.

Together AI possui inferência serverless barata para diversos modelos open-weight.

Fireworks possui inference serverless e deployments dedicados.

RunPod fornece GPU dedicada e serverless cobrados sob demanda.

Google Colab continua útil para experimentação, mas NÃO deve ser tratado como infraestrutura confiável de produção.

O tier gratuito:

- possui limites dinâmicos;
- pode encerrar runtime;
- não garante GPU;
- restringe certas formas de controle remoto;
- não deve hospedar componente crítico permanente.

Conclusão preliminar:

```text
COLAB = LAB / BENCHMARK / EXPERIMENTAÇÃO

OPENROUTER = AGREGADOR DE INFERÊNCIA

TOGETHER / FIREWORKS = SERVERLESS OPEN MODELS

RUNPOD = SELF-HOSTED CLOUD / CUSTOM MODELS
```

Revalidar preços e termos na data de implementação.

---

# 11. VÍDEO / VEO

Não assumir que Google Veo será o único mecanismo de vídeo.

Criar uma camada:

```text
VideoProvider
```

possibilitando futuramente:

```text
Google Veo
provedores compatíveis
modelos open-weight hospedados
RunPod
outras APIs
```

O Veo atual deve ser utilizado conforme sua API e regras vigentes.

Não tentar burlar filtros internos.

Se um tipo de conteúdo não for suportado por ele:

```text
PROVIDER ROUTER
→ procurar fornecedor/modelo cujo uso seja permitido
```

---

# 12. DURAÇÃO DE VÍDEO

Não limitar a arquitetura ao limite de duração nativo de um modelo.

Implementar futuramente:

```text
SCENE PLANNER
     ↓
SHOT 1
SHOT 2
SHOT 3
SHOT 4
     ↓
CONTINUITY CONTEXT
     ↓
GENERATE SEGMENTS
     ↓
STITCH / EDIT
     ↓
FINAL VIDEO
```

Portanto:

um modelo poder gerar apenas alguns segundos por chamada não significa que o produto final tenha essa duração.

A arquitetura deve suportar:

```text
MULTI-SHOT GENERATION

CHARACTER CONSISTENCY

REFERENCE IMAGES

STYLE CONSISTENCY

SHOT CONTINUATION

AUTOMATIC EDITING

AUDIO SYNC

FINAL ASSEMBLY
```

Esses recursos serão uma segunda fase.

Não implementar agora se fugirem do escopo.

---

# 13. PRIVACIDADE

Criar metadata de privacidade por workload.

Exemplo:

```yaml
privacy:

  classification:
    public | internal | confidential | secret

  provider_allowed:
    - provider_a
    - provider_b

  logging:
    disabled

  persistence:
    false
```

Nunca enviar:

- secrets;
- tokens;
- SSH keys;
- passwords;
- dados privados do usuário;

para um provedor apenas porque ele possui modelo melhor.

Provider routing deve respeitar:

```text
QUALITY
+
COST
+
PRIVACY
+
POLICY COMPATIBILITY
```

---

# 14. MODEL POLICY

Nunca hardcodar arquitetura em:

```text
engineering = GPT
creative = model X
```

Configurar.

Exemplo conceitual:

```yaml
ai_policy:

  engineering:
    priority:
      - provider: openai
        model: auto

      - provider: openrouter
        model: fallback

  summarization:
    priority:
      - provider: openrouter
        model: low_cost_long_context

  research:
    priority:
      - provider: openai
      - provider: openrouter

  video:
    priority:
      - provider: veo
      - provider: alternative_video_provider
```

---

# 15. CUSTO

Implementar futuramente seleção baseada em custo.

Cada resposta pode registrar:

```text
provider
model
input_tokens
output_tokens
estimated_cost
latency
success
```

Criar budget policy.

Exemplo:

```yaml
budget:

  default_task_max_usd: 0.10

  heavy_reasoning_max_usd: 1.00

  video_generation:
    user_confirmed_budget: true
```

Valores apenas conceituais.

Não codificar até validar com o usuário.

---

# 16. INTELIGÊNCIA DO GITHUB

Objetivo central:

Antigravity precisa parar de funcionar como investigador de repositório.

GitHub deve fornecer:

```text
project_map

ownership

architecture summary

affected_files

recent_changes

dependency graph

tests

task history
```

Entretanto NÃO criar arquivos redundantes se essas informações já existirem.

Auditar primeiro:

```text
PROJECT_REGISTRY
PROJECT_MEMORY
CURRENT_STATE
TASK_PROTOCOL
AGENTS
Architecture Locks
Issues
git history
CODEOWNERS
```

E derivar o Context Packet.

---

# 17. CONTEXT SELECTION

Nunca enviar o repositório inteiro para uma IA.

Implementar:

```text
TASK
↓
semantic/path resolver
↓
relevant files
↓
relevant symbols
↓
recent diffs
↓
dependencies
↓
context packet
```

Meta:

```text
minimum context
maximum execution precision
```

---

# 18. ANTIGRAVITY — NOVO PRINCÍPIO

Antigravity não é planejador principal.

É:

```text
SPECIALIZED EXECUTION ENGINE
```

Quando recebe uma tarefa, idealmente deve saber:

- exatamente onde está;
- o que deve alterar;
- porque está alterando;
- arquivos permitidos;
- arquivos proibidos;
- teste a executar;
- critério de aceite.

Se perceber que o contexto recebido é insuficiente:

```text
FAIL WITH:
CONTEXT_PACKET_INSUFFICIENT
```

Não iniciar exploração ilimitada do repositório.

---

# 19. HUMAN GATES

Autonomia não significa permissões ilimitadas.

Manter Human Gate somente para ações realmente sensíveis.

Exemplos:

```text
credential creation

payment

production destructive action

security protection change

irreversible deletion

external account ownership

legal acceptance
```

Operações rotineiras e reversíveis dentro do escopo aprovado não precisam gerar interrupções artificiais.

Auditar os Human Gates existentes e reduzir gates redundantes SEM reduzir segurança real.

---

# 20. OPENROUTER

A implementação já planejada continua válida.

Criar adapter mínimo.

Mas ele NÃO deve ser tratado como “o provedor sem censura”.

Ele é:

```text
PROVIDER AGGREGATOR
```

Modelos e provedores individuais possuem políticas próprias.

O sistema deve conseguir trocar:

```text
provider
model
route
```

sem alterar arquitetura.

---

# 21. CLOUD GPU

Para modelos open-weight que precisarem de maior controle:

Avaliar:

```text
RunPod
e provedores equivalentes
```

Arquitetura possível:

```text
Control Plane
↓
private model endpoint
↓
cloud GPU
```

Isso permite hospedar modelos de pesos abertos sem exigir hardware do Mac.

Não provisionar infraestrutura ainda.

Apenas preparar a arquitetura para suportar endpoints externos configuráveis.

---

# 22. O QUE NÃO IMPLEMENTAR AGORA

Não:

- instalar modelos grandes no Mac;
- alterar o Router operacional;
- criar novo Dispatcher;
- criar novo Control Plane;
- duplicar CURRENT_STATE;
- criar segunda memória;
- criar segundo sistema de Issues;
- criar novo executor;
- criar watcher de pasta;
- expor shell genérico;
- criar endpoint admin irrestrito;
- instalar 10 provedores de uma vez;
- criar serviço GPU antes de benchmark;
- alterar Jarvis Voice nesta tarefa;
- reescrever a arquitetura inteira.

---

# 23. FASE 1 — IMPLEMENTAÇÃO AGORA

Esta tarefa deve implementar SOMENTE a infraestrutura fundamental necessária para permitir evolução.

Escopo recomendado:

```text
1. Provider abstraction

2. OpenRouter adapter

3. estrutura extensível para providers cloud

4. workload metadata

5. AI routing policy

6. task protocol extension compatível

7. sanitized provider health

8. GitHub execution-context contract

9. testes
```

NÃO implementar ainda:

```text
RunPod deployment

Together adapter

Fireworks adapter

Veo automation

video pipeline

image pipeline
```

Esses itens entram depois do benchmark.

---

# 24. RECONCILIAR COM O RELATÓRIO ANTERIOR

Não descartar o PRE-FLIGHT já realizado.

Baseline confirmado:

```text
HEAD_SHA=d196a0bc4a8f73bed4b2c9e9ea70b7249d766169

WORKTREE=CLEAN

TESTS=309 PASS

TASK_PROTOCOL=v5

ARCHITECTURE_LOCK=LOCKED

Router=JarvisTextRouter

Dispatcher=Dispatcher

Antigravity=ONLY_EXECUTOR

Sentinela=GOVERNANCE

Selected Skill=@llm-app-patterns
```

Reutilizar essa descoberta.

Não repetir uma auditoria completa se HEAD não mudou.

Validar apenas:

```text
git rev-parse HEAD
git status
```

Se baseline continuar igual, prosseguir.

---

# 25. ATUALIZAR A ISSUE

A Issue anterior ficou pequena demais.

Ela deve refletir este escopo maior.

Novo objetivo:

```text
CLOUD-FIRST MULTI-AI ORCHESTRATION +
GITHUB EXECUTION CONTEXT +
MINIMAL ANTIGRAVITY DISCOVERY
```

Preservar `agent_task v5`.

Atualizar:

```text
task_id

scope

allowed_scope

acceptance criteria

implementation brief
```

Não criar Issue duplicada se a existente puder ser atualizada corretamente.

---

# 26. ACCEPTANCE CRITERIA

A fase estará concluída quando:

```text
LOCAL_LLM_REQUIRED_FOR_REASONING=0

LOCAL_LLM_REQUIRED_FOR_SUMMARIZATION=0

AI_PROVIDER_ABSTRACTION=PASS

OPENROUTER_PROVIDER=PASS

CLOUD_PROVIDER_EXTENSION_POINT=PASS

WORKLOAD_ROUTER=PASS

TASK_PROTOCOL_BACKWARD_COMPATIBILITY=PASS

GITHUB_CONTEXT_PACKET=PASS

ANTIGRAVITY_FULL_REPO_DISCOVERY_REQUIRED=0

ROUTER_AUTHORITY=UNCHANGED

DISPATCHER_AUTHORITY=UNCHANGED

ANTIGRAVITY_ONLY_EXECUTOR=PASS

SENTINELA_GOVERNANCE=PASS

ARCHITECTURE_DUPLICATION=0

SECRETS_IN_GIT=0

REGRESSION_TESTS=0 FAIL
```

---

# 27. TESTES OBRIGATÓRIOS

Executar baseline antes da alteração.

Depois validar:

1. tarefa legada sem `ai` continua funcionando;

2. workload engineering escolhe policy válida;

3. provider explícito funciona;

4. provider indisponível realiza fallback permitido;

5. provider sem secret falha de forma honesta;

6. nenhum secret entra no log;

7. OpenRouter pode trocar modelo sem mudança de código;

8. Context Packet limita os arquivos entregues ao executor;

9. Antigravity não recebe repositório inteiro quando não necessário;

10. Router DIRECT/PROJECT permanece idêntico;

11. GitHub Issue continua sendo obrigatória para PROJECT;

12. Sentinela continua rodando PRE/POST;

13. suíte completa permanece verde.

---

# 28. ENTREGÁVEL DE PESQUISA

Além da implementação mínima, produzir:

```text
docs/AI_PROVIDER_RESEARCH.md
```

APENAS se não existir documento equivalente.

Se existir:

```text
EXTEND
```

O documento deve comparar:

```text
OpenRouter
Together
Fireworks
RunPod
Google Gemini
Google Veo
Google Colab
```

com tabela:

```text
Provider
Purpose
Best Use
Models
API
Serverless
Free Tier
Minimum Cost
Privacy
Logging
Multimodal
Video
Open Weights
Custom Model Hosting
Policy Constraints
Production Suitability
```

Utilizar fontes oficiais e data da consulta.

Não escolher um único vencedor ainda.

---

# 29. DECISÃO PARA COLAB

Tratar Colab como:

```text
EXPERIMENTATION_PROVIDER
```

não:

```text
PRODUCTION_BACKEND
```

salvo se auditoria futura provar que uma modalidade paga/dedicada adequada atende requisitos de disponibilidade.

---

# 30. REGRA SOBERANA

Todo novo recurso deve obedecer:

```text
REUSE
↓
EXTEND
↓
CREATE
```

e todo pedido:

```text
UNDERSTAND
↓
PLAN
↓
PERSIST TO GITHUB
↓
COMPILE MINIMAL CONTEXT
↓
DISPATCH
↓
EXECUTE
↓
VERIFY
↓
SYNC
```

Nunca:

```text
USER
↓
ANTIGRAVITY
↓
READ EVERYTHING
↓
GUESS
↓
EXECUTE
```

---

# 31. RELATÓRIO FINAL

Ao terminar, devolver:

```text
IMPLEMENTATION_REPORT

BASELINE_SHA=
FINAL_SHA=

ISSUE=

SKILL=

PROVIDERS_IMPLEMENTED=

PROVIDERS_RESEARCHED=

LOCAL_LLM_REQUIRED_FOR_SUMMARY=

LOCAL_LLM_REQUIRED_FOR_REASONING=

OPENROUTER_STATUS=

WORKLOAD_ROUTER_STATUS=

TASK_PROTOCOL_STATUS=

GITHUB_CONTEXT_PACKET_STATUS=

ROUTER_CHANGED=NO

DISPATCHER_CHANGED=NO|MINIMAL:<reason>

ANTIGRAVITY_EXECUTION_AUTHORITY=ONLY_EXECUTOR

SENTINELA_STATUS=

FILES_CREATED=

FILES_EXTENDED=

DUPLICATIONS_REJECTED=

TESTS_BEFORE=

TESTS_AFTER=

REGRESSIONS=

SECRET_SCAN=

ROLLBACK=

NEXT_RECOMMENDED_PROVIDER=
```

Não marcar DONE enquanto houver regressão, duplicação de arquitetura ou necessidade de leitura ampla do repositório para uma tarefa cirúrgica.

## RESULTADO ARQUITETURAL ESPERADO

```text
ChatGPT
   ↓
entende o usuário
   ↓
GitHub
   ↓
mantém conhecimento + estado + tarefa
   ↓
AI Router
   ↓
seleciona inteligência cloud adequada
   ↓
GitHub Execution Packet
   ↓
Sentinela
   ↓
Antigravity
   ↓
executa somente o necessário
   ↓
testa
   ↓
GitHub recebe o resultado
```

O objetivo não é tornar o Antigravity mais inteligente.

O objetivo é fazer com que ele NÃO PRECISE gastar inteligência descobrindo o que fazer.

Sua função deve ser executar com precisão o trabalho que ChatGPT + GitHub já estruturaram.
