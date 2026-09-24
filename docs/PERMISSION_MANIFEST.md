# MANIFESTO DE PERMISSÕES DO SISTEMA (PERMISSION MANIFEST)

Este manifesto lista e justifica todas as permissões de sistema necessárias para o funcionamento do **Antigravity Turbinado**, garantindo transparência absoluta e mínimo privilégio.

---

## 1. MATRIZ FORMAL DE PERMISSÕES

### Permissão 1: Acesso a Arquivos e Pastas (Files and Folders)
- **PERMISSION:** `macOS Files and Folders` / `Windows File Access`
- **WHY_NEEDED:** Necessária para que o Antigravity e o Control Plane possam ler, criar e editar arquivos dentro dos workspaces dos projetos autorizados pelo usuário.
- **COMPONENT_REQUESTING:** Antigravity Executor & Control Plane Daemon
- **SCOPE:** Restrito aos diretórios configurados em `PROJECT_REGISTRY.json` (ex: `~/projetos/*`).
- **CAN_RUN_WITHOUT_IT:** `NO` (o executor não consegue modificar arquivos de código sem esta permissão).
- **HOW_TO_REVOKE:**
  - *macOS:* Ajustes do Sistema → Privacidade e Segurança → Arquivos e Pastas → Desmarcar Terminal/Antigravity.
  - *Windows:* Propriedades da pasta → Segurança → Editar permissões.

---

### Permissão 2: Acesso Total ao Disco (Full Disk Access) [Opcional / Recomendado no macOS]
- **PERMISSION:** `macOS Full Disk Access (TCC)`
- **WHY_NEEDED:** Evita prompts repetitivos do sistema operacional ao compilar códigos, instalar dependências de pacotes (npm, pip) ou acessar caches de ferramentas em diretórios temporários.
- **COMPONENT_REQUESTING:** Antigravity IDE & Terminal
- **SCOPE:** Leitura e escrita no sistema local conforme políticas de sandbox.
- **CAN_RUN_WITHOUT_IT:** `YES` (o sistema pode operar apenas com "Arquivos e Pastas", porém o macOS poderá abrir múltiplos diálogos de autorização durante builds).
- **HOW_TO_REVOKE:** Ajustes do Sistema → Privacidade e Segurança → Acesso Total ao Disco → Remover Terminal/Antigravity.

---

### Permissão 3: Acessibilidade (Accessibility)
- **PERMISSION:** `Accessibility`
- **WHY_NEEDED:** Não utilizada por padrão no core do produto.
- **COMPONENT_REQUESTING:** Nenhum componente core.
- **SCOPE:** Nenhum.
- **CAN_RUN_WITHOUT_IT:** `YES`
- **HOW_TO_REVOKE:** Ajustes do Sistema → Privacidade e Segurança → Acessibilidade.

---

### Permissão 4: Automação / Apple Events
- **PERMISSION:** `Automation / Apple Events`
- **WHY_NEEDED:** Opcional para integração com atalhos do sistema (Shortcuts) ou notificações de desktop.
- **COMPONENT_REQUESTING:** Módulo opcional de notificações locais.
- **SCOPE:** Notificações locais do sistema.
- **CAN_RUN_WITHOUT_IT:** `YES`
- **HOW_TO_REVOKE:** Ajustes do Sistema → Privacidade e Segurança → Automação.

---

### Permissão 5: Gravação de Tela (Screen Recording)
- **PERMISSION:** `Screen Recording`
- **WHY_NEEDED:** **NÃO UTILIZADA.** O produto adota garantia expressa anti-spyware de Zero Captura de Tela.
- **COMPONENT_REQUESTING:** Nenhum.
- **SCOPE:** Bloqueado por política.
- **CAN_RUN_WITHOUT_IT:** `YES`
- **HOW_TO_REVOKE:** Não aplicável (permissão não solicitada).
