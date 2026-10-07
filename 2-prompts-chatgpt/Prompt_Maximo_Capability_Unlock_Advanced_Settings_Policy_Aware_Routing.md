# PROMPT MÁXIMO — CAPABILITY UNLOCK, ADVANCED SETTINGS E POLICY-AWARE ROUTING

# MISSÃO

Maximizar o potencial técnico de Gemini, Veo, Flow, Antigravity, AI Studio, Jules e demais ferramentas disponíveis nas contas Google AI Pro autorizadas.

A meta é descobrir, ativar e integrar:

- configurações avançadas;
- parâmetros pouco expostos na UI;
- recursos experimentais;
- capacidades disponíveis apenas por API/SDK;
- modos beta;
- controles de safety configuráveis;
- limites por modelo;
- opções de geração multimodal;
- extensão de vídeo;
- consistência de personagem;
- edição e continuação;
- controles de qualidade;
- opções de privacidade oficialmente configuráveis;
- capacidades incluídas no plano mas ainda não integradas.

NÃO criar bypass, jailbreak, obfuscation ou evasão de filtros internos.

---

# 1. PRINCÍPIO

Interpretar “unlock” como:

```text
DISCOVER
→ VERIFY
→ CONFIGURE
→ ENABLE
→ BENCHMARK
→ ROUTE
```

Não como:

```text
BYPASS
→ EVADE
→ SPOOF
→ DISABLE PROVIDER ENFORCEMENT
```

---

# 2. ADVANCED CONFIG DISCOVERY

Para cada ferramenta, investigar:

```text
documented UI settings
documented API parameters
SDK-only parameters
advanced request options
experimental flags
preview endpoints
beta models
model-specific options
account-level capabilities
plan-level capabilities
region-dependent capabilities
```

Usar documentação oficial, SDK oficial, schemas, OpenAPI/reference docs e introspecção permitida.

Não explorar vulnerabilidades nem endpoints privados não documentados.

---

# 3. SAFETY CONFIGURATION

Na Gemini API, auditar todos os `HarmCategory` e `HarmBlockThreshold` oficialmente suportados.

Quando permitido pelo serviço:

```text
OFF
BLOCK_NONE
BLOCK_ONLY_HIGH
BLOCK_MEDIUM_AND_ABOVE
BLOCK_LOW_AND_ABOVE
```

Aplicar a configuração menos restritiva oficialmente suportada para o workload legítimo.

Registrar:

```text
category
model
supported_thresholds
configured_threshold
provider_enforced_protections
```

Nunca afirmar que um filtro foi removido se a proteção for inerente ao modelo/provedor.

---

# 4. PRIVACY SETTINGS

Auditar opções reais de:

```text
data retention
training usage
history
activity controls
temporary processing
storage
reference media retention
enterprise/privacy controls
```

Aplicar a configuração de maior privacidade disponível oficialmente.

Registrar:

```text
provider
tool
setting
available_values
selected_value
effect
limitations
```

Não tentar ocultar conteúdo para escapar de políticas.

---

# 5. COPYRIGHT / MEMORIZATION CONTROLS

Mapear:

```text
memorization checks
reference image restrictions
copyright-related blocks
identity/likeness limitations
watermarking
SynthID
commercial-use constraints
```

Objetivo:

reduzir falsos bloqueios por configuração legítima quando existir opção documentada.

Se o bloqueio for obrigatório:

```text
PROVIDER_ENFORCED
```

e rotear para ferramenta alternativa compatível.

---

# 6. HOT / ADULT WORKLOAD CLASSIFICATION

Classificar de forma objetiva:

```text
sensual
adult_non_explicit
nudity
sexual_content
explicit_sexual_content
```

Não usar apenas a classe genérica `uncensored`.

Cada ferramenta deve registrar:

```text
SUPPORTED
CONFIGURABLE
RESTRICTED
UNKNOWN
```

---

# 7. NÃO PARAR NA PRIMEIRA RECUSA

Quando um provider responder com bloqueio:

```text
capture provider
capture model
capture finish_reason
capture safety category
capture request configuration
capture policy reason
```

Então:

```text
check whether a documented setting can legitimately change the result
```

Se SIM:

```text
retry once with valid documented configuration
```

Se NÃO:

```text
route to another compatible provider/tool
```

Não insistir por reformulação evasiva.

---

# 8. GEMINI / AI STUDIO

Auditar especialmente:

```text
safety settings
generation config
thinking/reasoning options
context window
system instructions
structured outputs
tool use
grounding
multimodal inputs
image generation/editing
experimental models
preview models
```

---

# 9. VEO / FLOW

Auditar:

```text
text-to-video
image-to-video
reference images
first-frame / last-frame control
video extension
scene continuation
video-to-video
Scenebuilder
subject consistency
camera controls
audio generation
resolution
aspect ratio
duration
seed-like controls if supported
negative prompting if supported
generation variants
credit usage
model versions
```

---

# 10. VIDEO FIDELITY MODE

Criar um preset:

```text
VIDEO_FIDELITY_MAX
```

que priorize:

```text
reference fidelity
face identity
body identity
motion consistency
camera consistency
skin detail
hair consistency
lighting continuity
background continuity
temporal coherence
```

Não priorizar velocidade/custo nesse modo.

---

# 11. LONG-FORM VIDEO

Quando duração solicitada > limite nativo:

```text
ScenePlanner
→ ShotPlan
→ Generate
→ Extend/Continue
→ Reference previous frame
→ Generate next segment
→ Assemble
```

O usuário pede duração final, não duração por chamada.

---

# 12. CAPABILITY REGISTRY

Registrar por ferramenta:

```text
tool
model
account
modality
capabilities
configurable_safety
mandatory_safety
privacy_controls
copyright_controls
max_native_duration
continuation_support
reference_support
quality_modes
cost
quota
```

---

# 13. ACCOUNT CAPABILITY DISCOVERY

Para cada conta autorizada:

```text
discover available products
discover plan
discover quota
discover preview features
discover Labs/experimental access
discover region restrictions
```

Nunca armazenar senha, cookie ou token no GitHub.

---

# 14. ROUTING LOGIC

Selecionar ferramenta considerando:

```text
CAPABILITY
QUALITY
POLICY COMPATIBILITY
PRIVACY
COST
QUOTA
LATENCY
```

---

# 15. FALLBACK

Exemplo:

```text
Veo = RESTRICTED
↓
check documented configurable setting
↓
if still restricted
↓
Flow alternative mode
↓
another configured video provider
↓
cloud open-weight provider
```

Nunca terminar com uma recusa genérica enquanto existir outra rota configurada e compatível.

---

# 16. BENCHMARK EMPÍRICO

Criar testes controlados para cada ferramenta:

```text
same subject
same scene
same camera
same duration
same reference
```

Medir:

```text
prompt adherence
identity consistency
motion
temporal coherence
detail
generation time
policy blocks
false positive blocks
```

---

# 17. RELATÓRIO DE LIMITES

Para cada ferramenta:

```text
CAPABILITY_LIMIT
CONFIG_LIMIT
PLAN_LIMIT
POLICY_LIMIT
UNKNOWN_LIMIT
```

Isso permite diferenciar:

```text
"não configuramos"
```

de:

```text
"o provedor não permite"
```

---

# 18. ANTIGRAVITY

Antigravity não deve responder automaticamente:

```text
"não posso"
```

quando o problema é apenas incompatibilidade de ferramenta.

Ele deve retornar:

```text
PROVIDER_RESTRICTED
```

e solicitar/usar outra rota compatível.

---

# 19. GITHUB

Persistir no GitHub somente:

```text
capability metadata
policy metadata
tool routing
benchmark results
task configuration
```

Nunca:

```text
secrets
cookies
session tokens
private account credentials
```

---

# 20. PESQUISA

Pesquisar continuamente apenas fontes oficiais:

```text
Google AI Developers
Google Labs
Google One
Gemini API docs
Flow docs
Veo docs
AI Studio docs
Jules docs
Antigravity docs
SDK references
release notes
```

Registrar data da descoberta.

---

# 21. ENTREGÁVEL

Produzir:

```text
ADVANCED_CAPABILITY_AUDIT

TOOLS_FOUND=
ADVANCED_SETTINGS_FOUND=
API_ONLY_SETTINGS=
EXPERIMENTAL_FEATURES=
SAFETY_CONTROLS=
PRIVACY_CONTROLS=
COPYRIGHT_CONTROLS=
MANDATORY_FILTERS=
HOT_CONTENT_COMPATIBILITY=
VIDEO_FIDELITY_OPTIONS=
LONG_FORM_VIDEO_OPTIONS=
BEST_TOOL_BY_WORKLOAD=
FALSE_POSITIVE_BLOCKS_FOUND=
PROVIDER_ENFORCED_LIMITS=
NEXT_TOOL_TO_INTEGRATE=
```

---

# REGRA FINAL

Extrair o máximo que cada ferramenta realmente permite.

Não aceitar defaults conservadores sem auditar opções configuráveis.

Não confundir:

```text
DEFAULT SETTING
```

com:

```text
MANDATORY PROVIDER LIMIT
```

E não confundir:

```text
PROVIDER LIMIT
```

com:

```text
SYSTEM-WIDE LIMIT
```

Se uma ferramenta não suportar o workload, procurar a próxima ferramenta legitimamente compatível.
