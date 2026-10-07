# PROMPT DEFINITIVO — GOOGLE AI PRO CAPABILITY UNLOCK + MULTI-TOOL ORCHESTRATION

## MISSÃO PRINCIPAL

Auditar, descobrir, integrar e explorar ao máximo todas as capacidades legítimas disponíveis nas contas Google AI Pro utilizadas pelo ecossistema.

O objetivo NÃO é criar outra arquitetura.

O objetivo é transformar os produtos já disponíveis em um conjunto coordenado de capacidades:

```text
ChatGPT
Google Gemini
Google AI Studio
Google Antigravity
Google Flow
Google Veo
Jules
Gemini multimodal
demais ferramentas incluídas ou acessíveis pelas contas
```

Cada ferramenta deve ser utilizada somente para aquilo em que é mais competente.

---

# 1. OBJETIVO OPERACIONAL

Criar uma camada de:

```text
CAPABILITY DISCOVERY
+
TOOL CAPABILITY REGISTRY
+
POLICY COMPATIBILITY
+
PROVIDER ROUTING
+
ACCOUNT ROUTING
```

Fluxo:

```text
USER REQUEST
↓
INTENT
↓
PROJECT CONTEXT
↓
CAPABILITY REQUIREMENTS
↓
AVAILABLE ACCOUNT CAPABILITIES
↓
POLICY COMPATIBILITY
↓
BEST TOOL / BEST ACCOUNT / BEST MODEL
↓
GitHub Execution Packet
↓
Antigravity
↓
EXECUTION
```

---

# 2. NÃO USAR O ANTIGRAVITY COMO PESQUISADOR

Antigravity permanece:

```text
ONLY EXECUTOR
```

ChatGPT + GitHub devem entregar:

```text
TOOL
ACCOUNT
MODEL
CAPABILITY
ENDPOINT / UI PATH
INPUTS
OUTPUT EXPECTED
ALLOWED SCOPE
ACCEPTANCE CRITERIA
```

Antigravity não deve explorar toda a conta, repositório ou ferramenta novamente.

---

# 3. AUDITORIA DAS CONTAS GOOGLE AI PRO

Para cada conta autorizada:

Descobrir quais recursos estão realmente disponíveis.

Auditar:

```text
Gemini app

Gemini Pro models

Google AI Studio

Google Flow

Veo

Flow video tools

Video extension

Video-to-video

Frames-to-video

Ingredients-to-video

Scenebuilder

Characters / subject consistency

Image models

Gemini multimodal

Jules

Antigravity

Developer Program capabilities

Google Vids / creative integrations

other experimental tools available
```

Não assumir disponibilidade apenas por documentação.

Registrar:

```text
AVAILABLE
UNAVAILABLE
REGION_BLOCKED
PLAN_LIMITED
ACCOUNT_LIMITED
UNKNOWN
```

---

# 4. TOOL CAPABILITY REGISTRY

Criar ou estender um registro canônico.

Exemplo conceitual:

```yaml
tool_capability:

  google_flow:
    video_generation: true
    video_extension: true
    video_editing: true
    scene_builder: true

  veo:
    text_to_video: true
    image_to_video: true
    duration_native: configurable_by_model
    continuation: true

  gemini:
    text: true
    vision: true
    reasoning: true
    multimodal: true

  antigravity:
    code_execution: true
    browser: true
    terminal: true
    project_execution: true

  jules:
    coding_agent: true
```

Não criar arquivo paralelo se já existir lugar canônico.

---

# 5. ACCOUNT ROUTING

Como existem múltiplas contas autorizadas, criar abstração:

```text
AccountCapabilityRegistry
```

Ela deve saber:

```text
account_alias
plan
available_products
remaining_quota
region
tool availability
usage limits
last health check
```

Nunca guardar senha ou sessão no GitHub.

Identificadores de conta devem ser aliases não sensíveis.

---

# 6. NÃO USAR MÚLTIPLAS CONTAS PARA EVADIR LIMITES

Múltiplas contas podem ser utilizadas apenas se forem legitimamente disponíveis e autorizadas.

Não automatizar:

```text
ban evasion
rate-limit evasion
account restriction bypass
policy enforcement evasion
```

Se uma conta estiver bloqueada para determinado recurso:

```text
ACCOUNT_UNAVAILABLE
```

e não tentar contornar a restrição.

---

# 7. SAFETY SETTINGS — USAR O MÁXIMO PERMITIDO OFICIALMENTE

Pesquisar e configurar as opções oficiais de safety disponíveis em cada API/ferramenta.

Quando a API permitir níveis configuráveis:

```text
use the least restrictive setting
that is officially supported
for the user's legitimate workload
```

Sem:

```text
jailbreak
prompt obfuscation
policy bypass
filter evasion
```

Registrar exatamente:

```text
safety_setting
supported_range
configured_value
provider_limit
```

---

# 8. GEMINI API SAFETY

Auditar configurações oficiais de segurança disponíveis na Gemini API.

Registrar quais categorias permitem configuração.

Usar somente parâmetros documentados oficialmente.

Se uma categoria permitir nível menos restritivo:

```text
configure according to workload
```

Se o provider mantiver filtro obrigatório:

```text
PROVIDER_ENFORCED
```

Não tentar neutralizá-lo.

---

# 9. VEO / FLOW — EXPLORAR CAPACIDADES REAIS

Auditar profundamente:

```text
Text to Video
Frames to Video
Ingredients to Video
Video Extension
Video-to-Video Editing
Scenebuilder
Characters
Avatars
Resolution
Audio
Camera control
Reference images
Continuity
Subject consistency
Duration
Extension limits
Generation credits
```

Testar empiricamente.

Não confiar apenas na documentação.

---

# 10. BENCHMARK DE FIDELIDADE DE VÍDEO

Criar bateria de testes padronizada.

Avaliar:

```text
FACE CONSISTENCY

BODY CONSISTENCY

SUBJECT IDENTITY

SKIN DETAILS

HAIR

MOTION

HAND ACCURACY

CAMERA MOVEMENT

LIGHTING

BACKGROUND

WARDROBE CONSISTENCY

FRAME CONTINUITY

REFERENCE IMAGE FIDELITY

AUDIO SYNC

PROMPT ADHERENCE
```

Pontuar objetivamente os resultados.

---

# 11. LONG-FORM VIDEO

Não considerar o limite de um único clipe como limite final do sistema.

Criar plano:

```text
PROMPT
↓
SCENE PLAN
↓
SHOT 1
↓
LAST FRAME / REFERENCE
↓
EXTENSION
↓
SHOT 2
↓
EXTENSION
↓
SHOT N
↓
ASSEMBLY
```

Usar quando disponível:

```text
Video Extension
Scenebuilder
Video-to-video
reference frames
continuity metadata
```

---

# 12. CONTENT COMPATIBILITY

Classificar solicitações por conteúdo:

```text
general
fashion
beauty
tattoo
sensual
adult_non_explicit
sexual
explicit
violence
gambling
financial
medical
political
```

A classificação serve para selecionar ferramenta.

Não é mecanismo de censura do Control Plane.

---

# 13. POLICY COMPATIBILITY

Cada ferramenta/provedor deve possuir:

```text
SUPPORTED
RESTRICTED
UNKNOWN
```

por classe de conteúdo.

Exemplo:

```yaml
veo:
  sensual: SUPPORTED
  adult_non_explicit: CHECK
  explicit: RESTRICTED
```

Os valores devem ser derivados de:

```text
official documentation
real controlled testing
```

Nunca de suposição.

---

# 14. QUANDO UMA FERRAMENTA REJEITAR

Não fazer o Antigravity encerrar imediatamente com:

```text
"não posso fazer isso"
```

se o problema for apenas incompatibilidade daquela ferramenta.

Comportamento correto:

```text
TOOL_A → RESTRICTED
↓
Capability Registry
↓
TOOL_B → SUPPORTED
↓
route to TOOL_B
```

Se nenhuma ferramenta configurada aceitar:

```text
NO_COMPATIBLE_TOOL_AVAILABLE
```

---

# 15. NÃO TENTAR FORÇAR O VEO

O sistema não deve:

```text
reformular para enganar o filtro

usar caracteres ocultos

traduzir para escapar de detector

usar prompt injection

usar sequência iterativa para contornar safety

alterar payload não documentado

interceptar frontend para desativar filtros
```

Isso é arquitetura frágil e pode causar bloqueios de conta.

---

# 16. OBJETIVO REAL DE "DESBLOQUEIO"

Interpretar “desbloquear” como:

```text
descobrir recursos escondidos ou pouco usados

ativar configurações oficiais

usar endpoints/API corretos

habilitar recursos disponíveis no plano

usar ferramentas melhores para cada workload

explorar parâmetros avançados

usar workflows de extensão

usar multimodalidade

usar modelos alternativos

usar accounts autorizadas conforme disponibilidade
```

e não como:

```text
bypass de política
```

---

# 17. GEMINI PRO ECOSYSTEM ROUTER

Criar conceitualmente:

```text
GoogleCapabilityRouter
```

Exemplo:

```text
coding
→ Antigravity / Jules

reasoning
→ Gemini Pro

video
→ Flow / Veo

video continuation
→ Flow Video Extension

video editing
→ Flow Video-to-Video

image generation
→ image model available in Flow/Gemini

research
→ Gemini + web-enabled capabilities

project execution
→ GitHub → Antigravity
```

---

# 18. NÃO ACOPLAR A UMA CONTA ÚNICA

Capability Router deve receber:

```text
required_capability
```

e retornar:

```text
best available authorized account
+
tool
+
model
```

Não:

```text
hardcoded@gmail-account
```

---

# 19. CUSTO E CRÉDITOS

Registrar:

```text
credits available
credits consumed
estimated generation cost
quota reset
```

quando a ferramenta permitir.

Selecionar rota considerando:

```text
QUALITY
+
QUOTA
+
COST
+
LATENCY
+
POLICY COMPATIBILITY
```

---

# 20. PRIVACIDADE

Auditar por ferramenta:

```text
data retention

training usage

history

cloud storage

temporary uploads

reference image retention

account sharing behavior
```

Criar:

```text
PrivacyProfile
```

por provider/tool.

Nunca prometer privacidade maior que a oferecida oficialmente.

---

# 21. RECURSOS EXPERIMENTAIS

Como Google AI Pro inclui recursos experimentais:

Registrar:

```text
STABLE
BETA
EXPERIMENTAL
```

Não depender de recurso experimental como peça crítica sem fallback.

---

# 22. PESQUISA OBRIGATÓRIA

Pesquisar documentação oficial de:

```text
Google AI Pro
Google Flow
Veo
Gemini API
AI Studio
Antigravity
Jules
Gemini video/image tools
Google Vids
Developer Program
```

Registrar data da pesquisa.

---

# 23. EXECUTION PACKET

Para uma solicitação multimídia, GitHub deve entregar algo como:

```yaml
execution_context:

  modality: video

  required_capabilities:
    - image_reference
    - subject_consistency
    - video_extension

  preferred_tool:
    google_flow

  model:
    veo

  policy_status:
    SUPPORTED

  duration_strategy:
    extension

  account:
    account_alias_X

  expected_output:
    final_video
```

Antigravity executa.

---

# 24. EXEMPLO DE SOLICITAÇÃO

Usuário:

```text
"Crie um vídeo de 30 segundos usando essa modelo."
```

Sistema:

```text
classify modality = video

detect duration > native clip

check Flow availability

check Veo availability

check Video Extension

check account quota

check policy compatibility

build Scene Plan

dispatch execution packet
```

---

# 25. FALLBACK

Se Flow indisponível:

```text
next video provider
```

Se Veo indisponível:

```text
next compatible provider
```

Se quota esgotada:

```text
next authorized account
```

somente quando isso estiver permitido pelos termos da conta/plano.

---

# 26. NÃO CRIAR NOVA GOVERNANÇA

Preservar:

```text
ChatGPT = planner

GitHub = SOT

Router = only dispatch authority

Sentinela = governance

Antigravity = only executor
```

GoogleCapabilityRouter é apenas:

```text
tool-selection capability
```

Não despacha diretamente.

---

# 27. TESTES

Criar testes para:

```text
tool discovery

account discovery

capability matching

quota awareness

policy compatibility

privacy metadata

video provider selection

video extension strategy

fallback

unknown capability

account unavailable

provider restricted

legacy task compatibility
```

---

# 28. RELATÓRIO ESPERADO

Entregar:

```text
GOOGLE_AI_PRO_CAPABILITY_REPORT

ACCOUNTS_AUDITED=

TOOLS_DISCOVERED=

GEMINI=

AI_STUDIO=

FLOW=

VEO=

ANTIGRAVITY=

JULES=

OTHER_TOOLS=

SAFETY_SETTINGS_DISCOVERED=

SAFETY_SETTINGS_CONFIGURABLE=

MANDATORY_PROVIDER_FILTERS=

VIDEO_CAPABILITIES=

VIDEO_EXTENSION=

VIDEO_EDITING=

REFERENCE_SUPPORT=

SUBJECT_CONSISTENCY=

MAX_NATIVE_DURATION=

LONG_FORM_STRATEGY=

POLICY_MATRIX=

PRIVACY_MATRIX=

QUOTA_MATRIX=

BEST_TOOL_BY_WORKLOAD=

MISSING_CAPABILITIES=

NEXT_INTEGRATION=
```

---

# REGRA SOBERANA

A liberdade do ecossistema deve vir de:

```text
CAPABILITY DISCOVERY
+
OFFICIAL CONFIGURATION
+
MULTIPLE TOOLS
+
MULTIPLE MODELS
+
MULTIPLE AUTHORIZED ACCOUNTS
+
POLICY-AWARE ROUTING
+
BETTER WORKFLOWS
```

Nunca depender de:

```text
um único modelo
uma única ferramenta
um único provider
```

e nunca tentar manter o Antigravity preso às limitações de uma ferramenta específica.

O Antigravity deve receber a melhor rota já escolhida e executar.
