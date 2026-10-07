# 🪟 Guia de Instalação, Desbloqueio e Uso no Windows

Este guia é obrigatório para usuários que baixarem e utilizarem o **Antigravity Turbinado / Ecossistema Sentinela** no sistema operacional **Windows (10/11)**.

---

## ⚡ Instalação Rápida Automatizada (1 Clique)

Abra o **PowerShell** no diretório do projeto e execute:
```powershell
.\install.ps1
```
> O script cuidará do desbloqueio de políticas de execução, remoção de travas de arquivos da internet e configuração do terminal integrado no VS Code / Antigravity.

---

## 🛠️ Passo a Passo Manual (Caso prefira configurar manualmente)

### Passo 1: Liberar a Política de Execução do PowerShell (`ExecutionPolicy`)
Por padrão, o Windows impede a execução de scripts `.ps1` e ferramentas de automação baixadas da internet ou criadas localmente.

1. No Windows, abra o menu **Iniciar**, digite **PowerShell**.
2. Clique com o botão direito sobre o **Windows PowerShell** e selecione **"Executar como Administrador"**.
3. Execute o comando:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   ```
   *(Ou se for uma máquina de desenvolvimento dedicada e você quiser liberar para toda a máquina:)*
   ```powershell
   Set-ExecutionPolicy Bypass -Scope LocalMachine -Force
   ```
4. Para confirmar que a regra foi aplicada, execute:
   ```powershell
   Get-ExecutionPolicy -List
   ```
   *O escopo `CurrentUser` ou `LocalMachine` deve aparecer como `RemoteSigned` ou `Bypass`.*

---

### Passo 2: Desbloquear Scripts/Arquivos Baixados (`Unblock-File`)
Se você baixou a pasta do repositório da internet (arquivo `.zip`), o Windows aplica um marcador de segurança chamado `Zone.Identifier` (SmartScreen) que bloqueia os scripts silenciosamente.

No PowerShell (no terminal normal), navegue até a pasta do projeto e execute:
```powershell
Get-ChildItem -Path . -Recurse | Unblock-File
```
*Isso remove a trava de "arquivo baixado da internet" de todos os scripts da pasta de uma só vez.*

---

### Passo 3: Destravar o Terminal Integrado no Antigravity / VS Code

Como nossa infraestrutura utiliza ferramentas multiplataforma e scripts de terminal, recomendamos configurar o terminal integrado para rodar sem bloqueios.

Abra o arquivo `settings.json` do VS Code ou Antigravity (`Ctrl + Shift + P` → *Preferences: Open User Settings (JSON)*):

#### Opção A: Definir o Git Bash como Terminal Padrão (Recomendado)
Como nossa estrutura utiliza padrões Unix (`bash`, comandos POSIX), o Git Bash contorna qualquer incompatibilidade do PowerShell:
```json
"terminal.integrated.defaultProfile.windows": "Git Bash"
```

#### Opção B: Rodar PowerShell com Bypass Automático
Caso utilize o PowerShell, configure os argumentos de inicialização com `Bypass`:
```json
"terminal.integrated.profiles.windows": {
  "PowerShell": {
    "source": "PowerShell",
    "icon": "terminal-powershell",
    "args": ["-NoExit", "-ExecutionPolicy", "Bypass"]
  }
}
```

---

## 📋 Resumo Rápido para Novos Usuários

1. Abra o **PowerShell como Administrador**.
2. Cole e aperte Enter:
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   ```
3. Feche e abra o Antigravity / VS Code novamente.
4. Pronto! O ecossistema está 100% destravado para executar comandos autônomos.
