# GUIA DE RESOLUÇÃO DE PROBLEMAS (TROUBLESHOOTING)

Soluções rápidas e diagnósticos para os cenários operacionais mais comuns.

---

## 1. O INSTALADOR FOI CANCELADO NO MACOS POR FALTA DE PERMISSÃO

- **Sintoma:** O instalador exibe uma mensagem de encerramento imediato informando que as permissões de disco foram negadas.
- **Causa:** O macOS bloqueou o acesso a pastas do sistema por meio do mecanismo de segurança TCC.
- **Solução:**
  1. Abra **Ajustes do Sistema → Privacidade e Segurança → Acesso Total ao Disco**.
  2. Adicione e habilite o seu aplicativo de **Terminal** e o **Antigravity**.
  3. Execute novamente o comando de instalação: `curl -fsSL ... | bash`.

---

## 2. GITHUB: ERRO DE PERMISSÃO AO LER OU CRIAR ISSUES

- **Sintoma:** `401 Unauthorized` ou `403 Forbidden` ao consultar a fila de tarefas.
- **Causa:** O Personal Access Token expirou ou não possui as permissões mínimas necessárias.
- **Solução:**
  1. Gere um novo token no GitHub com os escopos `repo` e `read:org`.
  2. Atualize o chaveiro seguro executando:
     ```bash
     python3 scripts/doctor.py --reauth
     ```

---

## 3. O ANTIGRAVITY ESTÁ PEDINDO PERMISSÃO PARA CADA ARQUIVO EDITADO

- **Sintoma:** O agente interrompe o raciocínio solicitando aprovação repetitiva para editar arquivos de código.
- **Causa:** O workspace não está configurado para o modo "Sempre permitir e proceder".
- **Solução:**
  1. No Antigravity, acesse **Settings → Workspace Permissions**.
  2. Para o diretório do projeto, defina **File Operations** como `Auto-Approve In Workspace`.
  3. Mantenha `Outside Workspace` em `Request Review` para manter o isolamento fora do projeto.

---

## 4. COMO GERAR UM DIAGNÓSTICO COMPLETO PARA SUPORTE

Execute o comando nativo:

```bash
python3 scripts/doctor.py --verbose
```

Copie o relatório gerado (que não conterá nenhum segredo ou token) e envie para o nosso canal de suporte no Telegram: [@xprotorkzdev](https://t.me/xprotorkzdev).
