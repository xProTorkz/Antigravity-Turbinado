# GUIA DE INSTALAÇÃO & ONBOARDING DO CLIENTE

Este documento detalha o processo de instalação do **Antigravity Turbinado** tanto no **macOS** quanto no **Windows**.

---

## 1. INSTALAÇÃO NO MACOS

### 1.1. Pré-requisitos
- macOS Monterey (12.0) ou superior (suporte nativo a Apple Silicon M1/M2/M3/M4 e Intel).
- Terminal padrão (`zsh` ou `bash`).
- Git e Python 3.10+ instalados.

### 1.2. Execução do Instalador
Abra o Terminal e execute:

```bash
curl -fsSL https://raw.githubusercontent.com/xProTorkz/ai-orchestration-kit/main/installer/install.sh | bash
```

### 1.3. Gestão de Permissões no macOS (TCC & Full Disk Access)

> [!IMPORTANT]
> O Antigravity e o Control Plane necessitam de permissão para ler e escrever arquivos nas suas pastas de projetos e executar testes locais. O macOS gerencia isso pelo sistema de segurança TCC.

O instalador executa um teste de acesso ao disco. Caso a permissão não esteja ativa:
1. Uma janela do sistema poderá ser exibida solicitando autorização para o Terminal / Antigravity.
2. Como conceder a permissão manualmente:
   - Abra **Ajustes do Sistema** (System Settings).
   - Vá em **Privacidade e Segurança** (Privacy & Security) → **Acesso Total ao Disco** (Full Disk Access).
   - Clique no ícone de `+` e adicione o seu **Terminal** (ou aplicativo de terminal em uso) e o aplicativo **Antigravity**.
   - Certifique-se de que a chave está **ativada** (azul).
3. ⚠️ **Política Fail-Closed:** Se você recusar a permissão no teste do instalador, a instalação é **cancelada imediatamente na hora**. Nenhum arquivo corrompido é deixado no sistema. Após habilitar a permissão nos Ajustes, basta rodar o comando de instalação novamente.

---

## 2. INSTALAÇÃO NO WINDOWS

### 2.1. Pré-requisitos
- Windows 10 (Build 19041+) ou Windows 11.
- PowerShell 5.1 ou PowerShell 7+ rodando como Administrador.
- Git para Windows instalado (com `git-credential-manager` habilitado).
- Python 3.10+ instalado e marcado a opção "Add python.exe to PATH".

### 2.2. Execução do Instalador
Abra o PowerShell como Administrador e execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
irm https://raw.githubusercontent.com/xProTorkz/ai-orchestration-kit/main/installer/install.ps1 | iex
```

### 2.3. Gestão de Permissões no Windows
- O script configura o armazenamento seguro de credenciais via Windows Credential Manager.
- Ele prepara o ambiente virtual isolado sem tocar nas variáveis globais do sistema.
- Caso o UAC (Controle de Conta de Usuário) solicite permissão, confirme clicando em "Sim". Se for negado, o instalador encerra com segurança.

---

## 3. PÓS-INSTALAÇÃO & VERIFICAÇÃO (DOCTOR)

Após a conclusão do instalador, um relatório consolidado é gerado. Para validar a integridade a qualquer momento:

```bash
# macOS / Linux
python3 scripts/doctor.py

# Windows
python scripts\doctor.py
```

O script confirmará que todos os nós estão verdes:
- Git & Credenciais
- Diretório de Projetos
- Sentinela Guardião ativo
- Catálogo de Skills indexado
- Antigravity conectado
