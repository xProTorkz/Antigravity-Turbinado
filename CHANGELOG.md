# CHANGELOG — HISTÓRICO DE VERSÕES

Todas as alterações notáveis neste projeto serão documentadas neste arquivo, seguindo as diretrizes do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-10-07

### Adicionado
- **Dicionário Léxico Canônico v3.8 (`dicionario_lexico.json`):**
  - Mapeamento e aliases de linguagem para espelhamento estático e recriação visual de frontend (`copia`, `clone`, `espelho`, `replicar`).
  - Regra estrita de salvamento em diretório dedicado dentro de `/Users/lucasvinicius/projetos/<NOME_PASTA>`.
  - Inicialização automática de servidor HTTP local e abertura no navegador (Google Chrome).
- **Comando Canônico de Auto-Atualização do Sentinela:**
  - Gatilho rápido por voz ou texto: `"baixa a nova atualizacao sentinela"`.
  - Script oficial `scripts/atualizar_sentinela.sh` para sincronização via Git (`git pull origin main`) e atualização automática de `~/.gemini/config/dicionario_lexico.json` e skills da Sentinela.
  - Integração nativa no roteador `agy_cmd.sh` e no `install.sh`.

---

## [0.1.0] - 2026-09-24

### Adicionado
- **Bootstrap Oficial da Arquitetura Comercial:**
  - Criação do repositório privado `xProTorkz/ai-orchestration-kit` com histórico Git totalmente novo e limpo.
  - Implementação da divisão quadripartite de papéis: ChatGPT (Planner) → GitHub (SOT) → Control Plane (Router) → Sentinela (Governança) → Antigravity (Executor).
- **Scripts de Instalação Multiplataforma:**
  - `installer/install.sh` para macOS com checagem de permissões TCC e cancelamento seguro (fail-closed) se recusadas.
  - `installer/install.ps1` para Windows com validação de políticas de execução e Credential Manager.
- **Skill Router & Curator (`scripts/skill_router.py`):**
  - Descoberta dinâmica de skills sem hardcoding de quantitativos históricos.
  - Indexação de metadados (`task_type`, `domain`, `status`) e cálculo de score de confiança.
- **Diagnóstico & Auditoria:**
  - `scripts/doctor.py`: Verificação de saúde completa pós-instalação.
  - `scripts/security_audit.py`: Validação de garantias anti-spyware e auditoria contra vazamento de segredos.
  - `scripts/uninstall.py`: Desinstalador limpo com reversão de configurações.
- **Integração Comercial & Pagamento:**
  - Configuração do Sharkbot redirecionando para canal oficial no Telegram [@xprotorkzdev](https://t.me/xprotorkzdev).
  - Modelagem das ofertas: Plano Core (R$ 299) e Combo Pro com 18 meses de Gemini configurado (R$ 399).
  - Script interativo de onboarding com botões de seleção e menu "Voltar".
- **Manifestos de Transparência:**
  - `docs/PERMISSION_MANIFEST.md` e `docs/NETWORK_MANIFEST.md`.
