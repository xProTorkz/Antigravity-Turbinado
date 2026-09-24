# PACOTES COMERCIAIS & INTEGRAÇÃO DE PAGAMENTO SHARKBOT

Este documento descreve as modalidades comerciais de licenciamento do **Antigravity Turbinado**, a automação do funil de checkout via Sharkbot e o fluxo de compra no Telegram oficial.

---

## 1. PACOTES E PREÇOS DISPONÍVEIS

| Oferta | Preço | O que inclui | Indicado para |
|---|---|---|---|
| **Plano Core** | **R$ 299,00** | • Kit completo Antigravity Turbinado<br>• Instaladores automáticos macOS e Windows<br>• Sentinela Guardião v2.0 com Scope Lock<br>• 100 Skills essenciais + Skill Router para 2.488 skills<br>• Templates canônicos de Issue, Governança e AGENTS.md<br>• Instruções personalizadas do ChatGPT (Web/App) | Desenvolvedores que já possuem assinatura ativa de IA e desejam o ecossistema pronto para usar. |
| **Combo Pro (Com Gemini 18 Meses)** | **R$ 399,00** | • **Tudo do Plano Core**<br>• **Conta Google Gemini Pro/Ultra configurada por 18 meses**<br>• Suporte prioritário no Telegram [@xprotorkzdev](https://t.me/xprotorkzdev)<br>• Assistência no primeiro onboarding e setup de projeto | Desenvolvedores e times que querem a solução 100% pronta sem se preocupar com assinaturas extras. |

---

## 2. CANAL DE VENDAS & GATEWAY SHARKBOT

- **Canal Oficial no Telegram:** [@xprotorkzdev](https://t.me/xprotorkzdev)
- **Processamento de Pagamento:** Gateway de alta conversão integrado com **Sharkbot Automation**.
- **Métodos de Pagamento Suportados:** Pix com aprovação instantânea e Cartão de Crédito.

---

## 3. FLUXO INTERATIVO NO BOT DO TELEGRAM

O bot implementa um sistema de menu com navegação intuitiva e botão de retorno:

```text
[Menu Principal]
├── 1. Conhecer o Antigravity Turbinado
├── 2. Escolher Plano / Comprar
│   ├── [Opção A] Plano Core (R$ 299)
│   ├── [Opção B] Combo Pro + Gemini 18 Meses (R$ 399)
│   └── ⬅️ Voltar ao Menu Principal
├── 3. Suporte & Falar com Engenheiro
└── 4. Perguntas Frequentes (FAQ)
```

### O que acontece após a confirmação do pagamento:
1. O Sharkbot valida a transação via webhook seguro.
2. O bot entrega imediatamente a chave de acesso e o link de liberação do repositório privado no GitHub.
3. Se o cliente optou pelo **Combo Pro (R$ 399)**, as credenciais da conta Gemini de 18 meses são fornecidas com instruções passo a passo para vinculação imediata no Antigravity.
