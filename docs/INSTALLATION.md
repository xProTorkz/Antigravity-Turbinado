# GUIA DE INSTALAÇÃO & ONBOARDING DO CLIENTE

Este documento detalha o processo de instalação do **Antigravity Turbinado** tanto no **macOS** quanto no **Windows**.

---

## 1. AS 3 FERRAMENTAS PRÉ-REQUISITO OBRIGATÓRIAS

Para que o ecossistema Antigravity Turbinado funcione com máxima performance, o cliente deve possuir instalado na máquina:

### 1. GitHub (Conta, Git & GitHub CLI)
- **Conta GitHub:** Crie ou utilize sua conta em [github.com](https://github.com).
- **Git:** Verifique se o Git está instalado executando `git --version` no terminal.
  - *macOS:* Instale via `xcode-select --install`.
  - *Windows:* Baixe em [git-scm.com](https://git-scm.com) com Git Credential Manager ativo.
- **GitHub CLI (`gh`):** Recomendado para autenticação rápida via `gh auth login`.

### 2. Google Antigravity
- Baixe e instale o aplicativo oficial do **Google Antigravity** na sua máquina.
- **Configuração de Permissão no Workspace:**
  - Dentro da pasta de projetos (`~/projetos`): configure para *"Sempre permitir e proceder com as implementações"* para que o agente execute autonomamente.
  - Fora da pasta: mantenha em *"Perguntar sempre / Request Review"*.

### 3. ChatGPT (Web & Desktop App)
- Tenha acesso ao ChatGPT ([chatgpt.com](https://chatgpt.com)) ou ao aplicativo desktop oficial para Mac/Windows.
- Configure as **Instruções Personalizadas (Custom Instructions)** com o perfil do **Planner** fornecido em [`docs/CHATGPT_LINKING.md`](CHATGPT_LINKING.md).

---

## 2. OBTENÇÃO DA LICENÇA & INSTALADOR AUTENTICADO

> [!CAUTION]
> **O instalador NÃO é público no GitHub.**  
> O script de instalação e a sua chave de ativação única são entregues com exclusividade pelo bot oficial no Telegram:  
> 👉 **[@xProTorkzbot](https://t.me/xProTorkzbot)**

### 🛡️ Proteção por HWID (Hardware UUID) & IP
- Cada chave de licença é gerada com assinatura criptográfica vinculada ao seu Telegram User ID.
- No **primeiro uso**, o instalador realiza a leitura do identificador único da placa-mãe/processador da sua máquina (**Hardware UUID / Machine GUID**) e do IP público de ativação.
- A licença é permanentemente travada naquele hardware. Se alguém tentar rodar o mesmo instalador ou a mesma chave em outro computador, a instalação será bloqueada imediatamente com erro de `HWID Mismatch`.

---

## 3. INSTALAÇÃO NO MACOS

1. Receba o arquivo autenticado `install.sh` e sua chave de licença no Telegram [@xProTorkzbot](https://t.me/xProTorkzbot).
2. Abra o Terminal e execute:
   ```bash
   bash install.sh --license=SUA_CHAVE_AQUI
   ```
3. O instalador verificará o HWID, confirmará a permissão de disco (TCC) e instalará o kit completo com as 2.488+ skills.
4. Se o macOS solicitar autorização de disco, habilite em **Ajustes do Sistema → Privacidade e Segurança → Acesso Total ao Disco**. Se recusar, a instalação cancela na hora por segurança (fail-closed).

---

## 4. INSTALAÇÃO NO WINDOWS

1. Receba o script autenticado `install.ps1` e sua chave de licença no Telegram [@xProTorkzbot](https://t.me/xProTorkzbot).
2. Abra o PowerShell como Administrador e execute:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1 -License SUA_CHAVE_AQUI
   ```
3. O script valida o hardware, configura o Windows Credential Manager e prepara o ambiente com todas as skills pré-instaladas.


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
