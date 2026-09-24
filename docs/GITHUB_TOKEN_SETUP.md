# CONFIGURAÇÃO SEGURA DO GITHUB (GITHUB TOKEN SETUP)

Este documento orienta o cliente sobre como conectar sua própria conta do GitHub com segurança total, garantindo que o token opere com mínimo privilégio e nunca seja exposto.

---

## 1. MÉTODOS SUPORTADOS

Existem dois caminhos oficiais recomendados:

### Método A: GitHub CLI Oficial (Mais Simples e Seguro)
Caso você utilize o GitHub CLI (`gh`):
```bash
gh auth login -w -s repo,read:org
```
O login é realizado diretamente no navegador via OAuth, e suas credenciais são armazenadas de forma criptografada no chaveiro seguro do sistema (macOS Keychain ou Windows Credential Manager).

---

### Método B: Fine-Grained Personal Access Token (PAT)

Se você preferir criar um token manual no GitHub:

1. Acesse o GitHub: **Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**.
2. Clique em **Generate new token**.
3. Defina os parâmetros:
   - **Token name:** `Antigravity Turbinado Client Token`
   - **Expiration:** Recomendado 90 dias (ou conforme política interna).
   - **Repository access:** Selecione **Only select repositories** (e marque seus projetos) ou **All repositories**.
4. **Permissões mínimas de Repositório (Repository Permissions):**
   - `Contents`: Read & Write (para ler código, criar branches e fazer commits).
   - `Issues`: Read & Write (para ler e atualizar as tarefas da fila).
   - `Pull requests`: Read & Write (para abrir e revisar PRs).
   - `Metadata`: Read-only (obrigatório pelo GitHub).
5. Clique em **Generate token** e copie o valor gerado.

---

## 2. ARMAZENAMENTO BLINDADO DO TOKEN

> [!CAUTION]
> **NUNCA** cole seu token em arquivos `.env`, mensagens de Issue, código versionado ou logs do terminal.

Para registrar o token no Git com proteção do sistema operacional:

### No macOS (Keychain):
```bash
git credential-osxkeychain store <<EOF
protocol=https
host=github.com
username=oauth2
password=SEU_TOKEN_AQUI
EOF
```

### No Windows (Credential Manager):
```powershell
cmdkey /generic:git:https://github.com/ /user:oauth2 /pass:SEU_TOKEN_AQUI
```

O instalador do Antigravity Turbinado também oferece um prompt interativo que armazena a chave diretamente no cofre seguro sem exibir o texto na tela.
