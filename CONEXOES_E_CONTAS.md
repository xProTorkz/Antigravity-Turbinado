# 🌐 Guia Canônico de Conexões de Contas & Integrações Externas

> **Princípio Fundamental de Segurança:** Este ecossistema opera sob o modelo **BYOK (Bring Your Own Key)**.  
> Todas as conexões, credenciais e ambientes são **100% pessoais e isolados**. Nenhuma conta, token ou dado do mantenedor é compartilhado ou acessado. Cada usuário conecta exclusivamente as **suas próprias contas gratuitas**.

---

## 📋 Resumo das Contas que Você Pode Conectar

| Serviço | Para que serve? | Link Oficial Direto | Nível de Custo |
| :--- | :--- | :--- | :--- |
| **Google AI Studio** | Raciocínio de fronteira, testes de prompts do Gemini 2.0/1.5 e envio direto para o Antigravity/GitHub | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Gratuito (Free Tier) |
| **Google Colab** | Execução de notebooks Python, análise de dados e treinamento usando seu hardware local | [colab.research.google.com](https://colab.research.google.com/) | Gratuito |
| **GitHub** | Versionamento, rastreamento de tarefas, issues e esteira do ecossistema | [github.com](https://github.com) | Gratuito |

---

## 🤖 1. Como Conectar e Configurar o Google AI Studio

O **Google AI Studio** é o ambiente oficial de prototipagem e desenvolvimento de IA do Google para os modelos **Gemini 2.0 Flash**, **Gemini 1.5 Pro** e **Gemini 1.5 Flash**.

### Passo a Passo para Obter sua Chave Pessoal:
1. Acesse a página oficial de chaves de API:
   👉 **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
2. Faça login com a sua conta pessoal Google (`@gmail.com`).
3. Clique no botão azul **"Create API Key"** (Criar chave de API).
4. Selecione a opção **"Create API key in new project"** (ou escolha um projeto existente).
5. Copie a chave gerada (ela começa com `AIzaSy...`).

### Como Conectar com o Antigravity:
Para que tudo o que você disser no terminal ou no Antigravity possa consultar os modelos de ponta do Google AI Studio:
- Defina a sua chave no seu terminal pessoal executando:
  ```bash
  export GEMINI_API_KEY="SUA_CHAVE_AQUI"
  ```
  *(Ou salve no arquivo pessoal `~/.gemini/ai_studio_key.txt`)*.

### Como Enviar Prompts do AI Studio Direto para o GitHub:
Ao construir soluções ou prompts no Google AI Studio:
1. No Google AI Studio, clique em **"Get Code"** (no canto superior direito do prompt).
2. O AI Studio gera o código Python/JavaScript pronto.
3. Cole o código ou comando diretamente no terminal do **Antigravity**.
4. O Antigravity executa a alteração e, via Sentinela, sobe diretamente para o **GitHub** com commit atômico e rastreável:
   ```bash
   git add .
   git commit -m "feat(ai): integra prompt do Google AI Studio"
   git push origin main
   ```

### 💡 Por que algumas abas ou opções ficam travadas no Google AI Studio?
- **Code Execution vs Structured Outputs:** Se a opção **Structured Output (JSON)** estiver ativada na barra lateral, o Google AI Studio trava a aba de **Code Execution** (execução de código Python). Uma opção desliga a outra automaticamente.
- **Search Grounding vs Function Calling:** No modo Chat, a pesquisa na web pelo Google desabilita chamadas de funções customizadas.
- **Modelo Selecionado:** Certifique-se de selecionar no topo direito **`Gemini 2.0 Flash`** ou **`Gemini 1.5 Pro`**, que são os modelos que possuem suporte a 100% de todas as abas e ferramentas.
- **Resgate de $10 USD de Crédito Gratuito:** O Google concede $10 de bônus promocional para quem ativa o faturamento na API. Para resgatar, acesse [Plan Information](https://aistudio.google.com/app/plan_information), selecione **"Set up billing"** e vincule uma conta de faturamento do Google Cloud com cartão internacional válido.

---

## 📓 2. Como Conectar com o Google Colab

O **Google Colab** permite rodar notebooks Jupyter na nuvem do Google de forma totalmente gratuita.

### Passo a Passo para Conectar sua Conta:
1. Acesse o portal do Colab:
   👉 **[https://colab.research.google.com/](https://colab.research.google.com/)**
2. Faça login com a sua conta Google.
3. Abra ou crie um novo notebook (`.ipynb`).

### Como Conectar o Google Colab Diretamente ao seu PC Local (Local Runtime):
Se você quiser que o Google Colab execute células utilizando o hardware e os arquivos locais do seu computador:
1. No seu terminal, inicie o servidor Jupyter local permitindo a origem do Colab:
   ```bash
   jupyter notebook --NotebookApp.allow_origin='https://colab.research.google.com' --port=8888 --NotebookApp.port_retries=0 --no-browser
   ```
2. O terminal gerará uma URL com token de segurança (ex: `http://localhost:8888/?token=123456...`).
3. No Google Colab aberto no seu navegador:
   - Clique na seta ao lado de **"Conectar"** (canto superior direito).
   - Escolha **"Conectar a um ambiente de execução local"**.
   - Cole a URL do seu terminal e clique em **Conectar**.
4. **Pronto!** O Google Colab agora lê e escreve arquivos diretamente no seu diretório local do Antigravity.

---

## 🐙 3. Como Conectar sua Conta do GitHub

Para sincronizar suas tarefas, branches e repositórios:
1. Abra o terminal e execute o GitHub CLI:
   ```bash
   gh auth login
   ```
2. Selecione:
   - **What account do you want to log into?** ➔ `GitHub.com`
   - **What is your preferred protocol for Git operations?** ➔ `HTTPS` (ou `SSH`)
   - **Authenticate Git with your GitHub credentials?** ➔ `Yes`
   - **How would you like to authenticate?** ➔ `Login with a web browser`
3. Copie o código de 8 dígitos exibido no terminal, aperte Enter para abrir o navegador e autorize.
4. O Antigravity e o Sentinela estarão prontos para enviar código, criar issues e sincronizar tudo com o seu GitHub.

---

## 🪟 4. Desbloqueio Automático no Windows (PowerShell)

Para usuários do sistema operacional **Windows (10/11)**, o Windows costuma bloquear por padrão scripts `.ps1` da internet via `ExecutionPolicy` e SmartScreen.

### A Única Automação Necessária no Windows:
Você **não precisa** configurar nada manualmente. O instalador do Windows cuida de tudo:
1. Abra o **PowerShell** no diretório do projeto e execute:
   ```powershell
   .\install.ps1
   ```
2. O script automaticamente:
   - Libera a política de execução (`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force`).
   - Remove as travas de download dos arquivos (`Unblock-File`).
   - Configura o terminal integrado do VS Code / Antigravity com **Git Bash** padrão ou PowerShell com `-ExecutionPolicy Bypass`.

---

## 🛡️ 5. Governança Enxuta: Uma Única Skill Instalada

Para garantir máxima estabilidade e evitar qualquer conflito:
- **Única Skill Global Instalada:** `@sentinela` localizada em `~/.gemini/config/skills/sentinela/SKILL.md`.
- **Zero Inchaço:** Nenhum script paralelo desnecessário.
- **Regra Suprema:** *ONE RULE → ONE CANONICAL SOURCE*. Todas as diretrizes operam sob a vigilância do Sentinela Guardião.
