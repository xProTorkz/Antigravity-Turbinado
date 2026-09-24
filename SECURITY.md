# POLÍTICA DE SEGURANÇA & MODELO DE CONFIANÇA (SECURITY.MD)

O **Antigravity Turbinado** opera sob o princípio fundamental de **Soberania do Usuário e Mínimo Privilégio**.

---

## 1. GARANTIAS ANTI-SPYWARE (TRUST MODEL)

Garantimos formalmente e comprovamos por testes automatizados (`scripts/security_audit.py`):

1. **Zero Keylogging:** Não há interceptação, gravação ou leitura de pressionamento de teclas em nível global de sistema operacional.
2. **Zero Captura Oculta de Tela:** Não há rotinas de captura de vídeo contínua ou streaming invisível de tela.
3. **Zero Monitoramento de Clipboard:** A área de transferência do usuário não é monitorada silenciosamente.
4. **Zero Extração de Dados Pessoais:** Perfis de navegadores, cookies, sessões ou históricos pessoais nunca são acessados ou transmitidos.
5. **Zero Modificação Invasiva de Sistema:**
   - Nenhum bypass de macOS TCC (Transparency, Consent, and Control) ou SIP (System Integrity Protection).
   - Nenhuma alteração silenciosa em `/etc/sudoers` ou desativação de UAC no Windows.
   - Nenhum túnel de rede oculto sem consentimento explícito.

---

## 2. ARMAZENAMENTO SEGURO DE SEGREDOS

- **Segredos em Repouso:** Credenciais do usuário (como tokens do GitHub) são gerenciadas exclusivamente através do armazenamento seguro oficial do sistema operacional:
  - macOS: `macOS Keychain` via `git-credential-osxkeychain`.
  - Windows: `Windows Credential Manager` via `git-credential-manager`.
  - Linux: `libsecret` ou chave GPG local.
- **Saneamento de Logs:** Todas as rotinas de execução filtram saídas para mascarar tokens, passwords e segredos conhecidos.

---

## 3. AUDITORIA E REPORTE DE VULNERABILIDADES

Caso identifique qualquer comportamento imprevisto, falha de isolamento de escopo ou anomalia de segurança:
1. Abra um chamado confidencial imediatamente pelo Telegram oficial [@xprotorkzdev](https://t.me/xprotorkzdev).
2. Não divulgue a vulnerabilidade publicamente antes do lançamento de um patch de correção.
3. Todas as correções são disponibilizadas via SemVer com checksums SHA256 verificáveis.
