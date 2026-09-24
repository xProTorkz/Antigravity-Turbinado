# GUIA DE INSTALAÇÃO & ONBOARDING DO CLIENTE

Este documento detalha o processo de instalação e configuração do **Antigravity Turbinado** no **macOS** e no **Windows**.

---

## 1. AS 3 FERRAMENTAS PRÉ-REQUISITO

Para que o ecossistema opere com máxima eficiência, você deve possuir instalado na máquina:

### 1. GitHub (Conta, Git & GitHub CLI)
- **Conta GitHub:** Crie ou utilize sua conta em [github.com](https://github.com).
- **Git:** Verifique se o Git está instalado executando `git --version` no terminal.
  - *macOS:* Instale via `xcode-select --install`.
  - *Windows:* Baixe em [git-scm.com](https://git-scm.com) com Git Credential Manager ativo.
- **GitHub CLI (`gh`):** Recomendado para autenticação rápida via `gh auth login`.

### 2. Google Antigravity
- Baixe e instale o aplicativo oficial do **Google Antigravity** na sua máquina.
- **Configuração de Permissão no Workspace:**
  - Dentro da pasta de projetos (ex: `~/projects`): configure para *"Sempre permitir e proceder com as implementações"* para que o agente execute autonomamente.
  - Fora da pasta: mantenha em *"Perguntar sempre / Request Review"*.

### 3. ChatGPT (Web & Desktop App)
- Tenha acesso ao ChatGPT ([chatgpt.com](https://chatgpt.com)) ou ao aplicativo desktop oficial para Mac/Windows.
- Configure as **Instruções Personalizadas (Custom Instructions)** com o perfil do **Planner** fornecido em [`docs/CHATGPT_LINKING.md`](CHATGPT_LINKING.md).

---

## 2. ATIVAÇÃO & LICENCIAMENTO

O script de instalação e o suporte técnico oficial estão disponíveis através do canal de atendimento:
👉 **`<support-url>`**

### 🛡️ Proteção por Hardware ID (HWID Lock)
- A licença é associada com segurança ao identificador único da máquina (Hardware UUID / Machine GUID) e IP de ativação.
- Isso protege a exclusividade de uso da sua estação de trabalho.

---

## 3. INSTALAÇÃO NO MACOS

1. Abra o Terminal no diretório do kit e execute:
   ```bash
   bash installer/install.sh
   ```
   *(Ou passe `--license=SUA_CHAVE_AQUI` se possuir chave de ativação).*
2. O instalador verificará o sistema operacional, confirmará a permissão de disco (TCC) no workspace e configurará o catálogo de skills.
3. Se o macOS solicitar autorização de disco, habilite em **Ajustes do Sistema → Privacidade e Segurança → Acesso Total ao Disco**. Se recusar, a instalação cancela com segurança (fail-closed).

---

## 4. INSTALAÇÃO NO WINDOWS

1. Abra o PowerShell como Administrador e execute:
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\installer\install.ps1
   ```
2. O script valida o ambiente, configura as permissões e prepara o catálogo de skills essenciais.

---

## 5. PÓS-INSTALAÇÃO & VERIFICAÇÃO (DOCTOR)

Após a conclusão da instalação, valide a integridade do ambiente a qualquer momento:

```bash
# macOS / Linux
python3 scripts/doctor.py

# Windows
python scripts\doctor.py
```

O script confirmará que todos os nós estão operacionais:
- Git & Credenciais
- Diretório de Projetos
- Catálogo de Skills indexado
- Antigravity conectado
