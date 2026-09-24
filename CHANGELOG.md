# CHANGELOG — HISTÓRICO DE VERSÕES

Todas as alterações notáveis neste projeto serão documentadas neste arquivo, seguindo as diretrizes do [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e [Semantic Versioning](https://semver.org/).

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
