---
name: seguranca
description: "Skill local fixa de AppSec, segurança defensiva, conformidade OWASP, proteção de segredos, sanitização de inputs e mitigação de vulnerabilidades."
category: security
scope: project_local
source: canonical
tags: [security, appsec, owasp, secrets, encryption, headers, compliance]
---

# 🛡️ Skill Local de Projeto — Segurança

Esta skill governa a postura de segurança, proteção contra vazamentos e resiliência a ataques do projeto ativo.

## 📌 Escopo e Responsabilidades
1. **Zero Segredos:** Proibição absoluta de comitar senhas, tokens, cookies, chaves de API e arquivos `.env`.
2. **Mitigação OWASP Top 10:** Sanitização estrita contra injeções (SQLi, NoSQLi, Command Injection), XSS, CSRF e SSRF.
3. **Cabeçalhos de Segurança:** Garantia de CSP, HSTS, X-Content-Type-Options e políticas de CORS rígidas.
4. **Defesa em Profundidade:** Validação de schemas no limite perimétrico de entrada e saída.
5. **Autenticação & Autorização:** Gestão segura de sessões, hashes criptográficos adequados e checagem de privilégios em cada rota.
