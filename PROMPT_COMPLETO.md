# 🎯 PROMPT COMPLETO: Web Scraper Intuitivo com IA, Proxy e Automação

## 📋 Visão Geral Completa

Crie uma aplicação web de scraping profissional em Python usando **Streamlit** (frontend) e **Flask** (proxy server), com interface 100% em português brasileiro. O sistema deve permitir extração de dados de qualquer site através de múltiplos métodos, incluindo IA, com automação completa e notificações por email.

---

## ⚠️ CONCEITO FUNDAMENTAL: CARREGAMENTO ≠ EXTRAÇÃO

### 🚨 ATENÇÃO: NÃO CONFUNDIR OS CONCEITOS!

O sistema funciona em **2 ETAPAS COMPLETAMENTE SEPARADAS**:

```
┌─────────────────────────────────────────────────────────┐
│  ETAPA 1: CARREGAR HTML (Como pegar a página)          │
├─────────────────────────────────────────────────────────┤
│  • ⚡ Rápido (Python): requests.get()                   │
│  • 🌐 Proxy CORS: Flask + corsproxy.io                  │
│  • 📁 Upload HTML: Arquivo salvo do navegador           │
│                                                          │
│  RESULTADO: HTML em memória (st.session_state)          │
└─────────────────────────────────────────────────────────┘
                          ⬇️
┌─────────────────────────────────────────────────────────┐
│  ETAPA 2: EXTRAIR DADOS (Como coletar informações)     │
├─────────────────────────────────────────────────────────┤
│  • 📊 Estrutura HTML: Ver tags/classes/IDs              │
│  • 🤖 Extração com IA: IA identifica seletores          │
│  • 🚀 Scraping em Massa: Aplicar em múltiplas URLs      │
│  • ⚡ Validador: Testar seletores manualmente           │
│  • 🤖 Automação: Agendar scraping periódico             │
│                                                          │
│  RESULTADO: Dados extraídos em CSV/JSON                 │
└─────────────────────────────────────────────────────────┘
```

### ❌ ERRO COMUM:

**ERRADO**: "A IA carrega a página"
**CERTO**: "A IA identifica seletores no HTML JÁ CARREGADO"

**ERRADO**: "Proxy é para extrair dados"
**CERTO**: "Proxy é para CARREGAR HTML de sites que bloqueiam Python"

**ERRADO**: "Upload de HTML extrai automaticamente"
**CERTO**: "Upload CARREGA o HTML, depois você escolhe ABA para extrair"

### ✅ FLUXO CORRETO:

1. **Primeiro**: Escolha COMO carregar (Python/Proxy/Upload)
2. **Depois**: Escolha ABA para extrair (IA/Massa/Validador/etc)

---

## 🔐 AUTENTICAÇÃO E SEGURANÇA

### Sistema de Login Customizado
- **Autenticação simples** com usuário/senha via Streamlit
- Credenciais configuráveis via **Replit Secrets**:
  - `ADMIN_USERNAME` (padrão: "admin")
  - `ADMIN_PASSWORD` (padrão: "admin123")
- **Tela de login** com formulário antes de qualquer acesso
- **Botão de logout** no sidebar
- **Session state** para manter usuário logado durante a sessão
- **Email admin master**: igor.as0703@gmail.com (hardcoded)

### Gerenciamento de Acessos (Admin)
- Painel no sidebar: "👑 Gerenciar Acessos (Admin)"
- **Adicionar usuários**: Campo de email + botão "Adicionar Acesso"
- **Remover usuários**: Botão 🗑️ ao lado de cada email
- **Lista de usuários autorizados**: Visual com indicadores 👑 (admin) e ✉️ (usuários)
- **Proteção**: Admin master não pode ser removido
- **Persistência**: Arquivo `authorized_emails.json` (excluído do git)

---

## 🔑 GERENCIAMENTO DE API KEYS

### Sistema Híbrido (Replit Secrets + Custom)
- **Prioridade**: Replit Secrets > API Keys Customizadas
- **Painel Admin** no sidebar: "🔑 Gerenciar API Keys"

#### Adicionar Keys Customizadas:
- Formulário: Nome da Key + Valor
- Botão "Salvar API Key"
- **Mascaramento**: Exibe apenas início/fim (ex: `sk-...xyz`)
- **Indicadores**: 🔒 (Replit Secrets) vs 🔑 (Custom)

#### Remover Keys:
- Botão 🗑️ ao lado de cada key
- Confirmação antes de excluir

#### Persistência:
- Arquivo `api_keys.json` (excluído do git)
- Função `get_api_key(name)`: busca em Secrets primeiro, depois em custom

#### Provedores Suportados:
- `OPENAI_API_KEY` - OpenAI GPT-5
- `ANTHROPIC_API_KEY` - Anthropic Claude Sonnet 4
- `GEMINI_API_KEY` - Google Gemini 2.5 Flash

---

## 🌐 PROXY SERVER (Flask - Porta 5001)

### Arquivo: `proxy_server.py`
- **Framework**: Flask com CORS habilitado
- **Porta**: 5001 (5000 é do Streamlit)
- **Host**: 0.0.0.0 (acessível externamente)

### Endpoints:

#### 1. `/proxy?url=<URL>`
- **Método**: GET
- **Função**: Proxy CORS usando corsproxy.io
- **Headers**: User-Agent customizado (navegador real)
- **Timeout**: 15 segundos
- **Retorno**: HTML da página com headers CORS
- **Uso**: Contornar bloqueios CORS e anti-scraping

#### 2. `/health`
- **Método**: GET
- **Função**: Health check do servidor
- **Retorno**: `{"status": "ok"}`

### Workflow Automático:
- Comando: `python proxy_server.py`
- Nome: "Proxy Server"
- Inicia automaticamente com o projeto

---

## 🕷️ APLICAÇÃO STREAMLIT (Porta 5000)

### Arquivo: `app.py` (~1760 linhas)

### Configuração Inicial:
```python
st.set_page_config(
    page_title="Web Scraper Intuitivo",
    page_icon="🕷️",
    layout="wide"
)
```

---

## 📂 SIDEBAR - PAINEL DE CONTROLE

### ⚠️ CONCEITOS SEPARADOS: CARREGAMENTO vs EXTRAÇÃO

**É FUNDAMENTAL entender que há 2 etapas INDEPENDENTES:**

#### 🔵 ETAPA 1: CARREGAR O HTML (Como buscar a página)
**Escolha COMO pegar o HTML:**
- **⚡ Rápido (Python)**: Requisição HTTP direta com `requests`
- **🌐 Proxy CORS**: Via servidor Flask + corsproxy.io
- **📁 Upload de HTML**: Arquivo salvo do navegador

#### 🟢 ETAPA 2: EXTRAIR DADOS (Como identificar e coletar informações)
**Escolha COMO extrair os dados do HTML já carregado:**
- **Estrutura HTML**: Ver tags, classes, IDs
- **Extração com IA**: IA identifica seletores CSS/XPath
- **Scraping em Massa**: Aplicar seletores em múltiplas páginas
- **Validador**: Testar seletores manualmente
- **Automação**: Agendar scraping periódico

---

### 1. ETAPA 1 - Configurações de Carregamento

#### A. Método de Carregamento (COMO BUSCAR O HTML):

**Opção 1: ⚡ Rápido (Python)**
- Usa biblioteca `requests` do Python
- Headers customizados (User-Agent, Accept-Language, etc)
- Timeout: 10 segundos
- Cookies especiais para Steam (verificação de idade)
- **QUANDO USAR**: Sites normais, blogs, lojas simples
- **NÃO FUNCIONA**: Sites com JavaScript pesado (Steam, Amazon)

**Opção 2: 🌐 Proxy CORS**
- Usa servidor Flask na porta 5001
- Proxy intermediário: corsproxy.io
- Contorna bloqueios CORS e anti-scraping
- Timeout: 20 segundos
- **QUANDO USAR**: Sites que bloqueiam requisições Python
- **LIMITAÇÃO**: Pode falhar se JavaScript carregar dados dinamicamente

**Opção 3: 📁 Upload de arquivo HTML**
- Salve a página no navegador (Ctrl+S)
- Ou visualize código (Ctrl+U) e salve
- Upload do arquivo .html
- **QUANDO USAR**: Sites JavaScript-heavy (Steam, Amazon, SPAs)
- **VANTAGEM**: HTML completo renderizado pelo navegador

#### B. Carregar a Página:
- **📡 Carregar de URL**: 
  - Campo de input para URL
  - Botão "🔍 Carregar Página"
  - Usa método escolhido (Python ou Proxy)
  
- **📁 Upload de arquivo HTML**: 
  - File uploader (.html, .htm)
  - Botão "📥 Processar HTML"
  - Ignora método de carregamento (lê arquivo direto)

#### C. Download do HTML:
- Botão: "💾 Baixar HTML da Página"
- Salva HTML atual em arquivo .html
- **ÚTIL PARA**: 
  - Backup da página
  - Processar offline depois
  - Compartilhar HTML com outras pessoas

### 2. Painéis de Administração (apenas admin)

#### 👑 Gerenciar Acessos
- Adicionar emails autorizados
- Remover usuários (exceto admin master)
- Visualizar lista completa

#### 🔑 Gerenciar API Keys
- Adicionar keys customizadas
- Visualizar keys (mascaradas)
- Remover keys
- Ver origem (Secrets vs Custom)

### 3. Histórico de Execuções (Scraping Automático)
- **Últimas 5 execuções** de tarefas automáticas
- Exibe: Nome, Status, Data/Hora, Produtos encontrados
- Indicadores visuais: ✅ Sucesso / ❌ Erro

### 4. Botão de Logout
- 🚪 Sair (disponível após login)

---

## 📑 ETAPA 2 - SISTEMA DE ABAS (5 MÉTODOS DE EXTRAÇÃO)

### ⚠️ IMPORTANTE: As abas são MÉTODOS DIFERENTES de EXTRAIR dados

**Depois de CARREGAR o HTML (Etapa 1), escolha UMA das abas para extrair:**

1. **📊 Estrutura HTML**: Ver o que tem na página (tags, classes, IDs)
2. **🤖 Extração com IA**: IA identifica seletores CSS/XPath automaticamente
3. **🚀 Scraping em Massa**: Aplicar seletores em múltiplas URLs/HTMLs
4. **⚡ Validador de Seletores**: Testar vários seletores de uma vez
5. **🤖 Scraping Automático**: Agendar scraping periódico com email

**TODAS AS ABAS TRABALHAM COM O MESMO HTML JÁ CARREGADO!**

---

### 📊 TAB 1: Estrutura HTML

**Objetivo**: Visualizar estrutura completa da página para identificar elementos.

**⚠️ ESTA ABA NÃO USA IA! Apenas mostra o HTML carregado na Etapa 1.**

#### Estatísticas da Página:
- Total de elementos HTML
- Tipos de tags únicos
- Contagem específica: Links (a), Imagens (img), Divs, Parágrafos (p), Títulos (h1-h6)
- Exibição em tabela interativa

#### Tags Disponíveis:
- Lista ordenada alfabeticamente de todas as tags HTML encontradas
- Text area com todas as tags separadas por vírgula

#### Classes CSS Disponíveis:
- Extração automática de todas as classes CSS da página
- Ordenadas alfabeticamente
- Text area para fácil busca/cópia

#### IDs Disponíveis:
- Lista de todos os IDs encontrados na página
- Ordenados alfabeticamente
- Text area para referência

#### Prévia do HTML:
- Primeiros 5000 caracteres do HTML formatado (prettify)
- Syntax highlighting para HTML
- Code block interativo

#### Visualização Melhorada:
- Renderização visual do HTML com CSS customizado:
  - `display: block` para elementos de bloco
  - `clear: both` para evitar sobreposição
  - Espaçamento correto (h1-h6, p, img)
  - **Imagens HD**: Prioriza `data-src`, `data-screenshot`, depois `src`
  - Imagens inline quando apropriado (detecção por keywords)
- Height: 600px scrollável
- Unsafe HTML habilitado para renderização completa

---

### 🤖 TAB 2: Extração com IA

**Objetivo**: Identificar seletores automaticamente usando IA com descrição em linguagem natural.

**⚠️ IMPORTANTE**: 
- A IA analisa o HTML **JÁ CARREGADO na Etapa 1**
- Não faz requisição nova - trabalha com o HTML em memória
- Identifica CSS/XPath para extrair dados específicos
- **NÃO É** um método de carregamento - é um método de EXTRAÇÃO

#### Seleção de Provedor de IA:
- **OpenAI (ChatGPT)**
  - Modelo: **gpt-5** (mais recente - agosto 2025)
  - Link para keys: https://platform.openai.com/api-keys
  
- **Anthropic (Claude)**
  - Modelo: **Claude Sonnet 4**
  - Link para keys: https://console.anthropic.com/settings/keys
  
- **Google (Gemini)**
  - Modelo: **gemini-2.5-flash** (mais recente)
  - Link para keys: https://ai.google.dev/gemini-api/docs/api-key

#### Configuração de API Key:
- Detecta se existe key salva (Secrets ou Custom)
- Mostra origem da key: 🔒 (Secrets) ou 🔑 (Custom)
- Checkbox: "Usar API Key salva" (padrão: marcado)
- Input manual opcional se desmarcar
- Link para adicionar em "Gerenciar API Keys"

#### Descrição do que Extrair:
- **Text area** grande para descrição em linguagem natural
- **Placeholder com exemplos**:
  ```
  Exemplo 1: "Encontre o título do jogo, preço e link para compra"
  Exemplo 2: "Extraia nome do produto, avaliação em estrelas e disponibilidade"
  Exemplo 3: "Busque todos os artigos com data de publicação e autor"
  ```
- Botão: **"🔍 Buscar com IA"**

#### Formato de Resposta da IA:
A IA retorna JSON estruturado:
```json
{
  "seletores": [
    {
      "campo": "Título do Produto",
      "seletor": "h1.product-title",
      "tipo": "CSS",
      "explicacao": "Tag h1 com classe product-title contém o título principal",
      "exemplo": "Smartphone XYZ 128GB"
    },
    {
      "campo": "Preço",
      "seletor": "//span[@class='price']/text()",
      "tipo": "XPath",
      "explicacao": "Span com classe price contém o valor monetário",
      "exemplo": "R$ 1.499,90"
    }
  ]
}
```

#### Exibição de Resultados:
1. **Tabela consolidada** com dados extraídos usando TODOS os seletores identificados
2. **Download direto**: CSV e JSON dos resultados
3. **Expander "Detalhes dos Seletores"**:
   - Tabela com: Campo, Seletor, Tipo, Explicação, Exemplo
   - Botão: **"📋 Copiar Seletores"** - copia APENAS as strings dos seletores (um por linha, sem comentários)
4. **Botão "Limpar"**: Limpa resultados e permite nova consulta
5. **Persistência**: Resultados salvos em `st.session_state.ai_result` (mantém entre reloads)

#### Integração com Outras Abas:
- Seletores ficam disponíveis para uso em **Scraping em Massa**
- Checkbox automático: "✨ Usar seletores identificados pela IA"

---

### 🚀 TAB 3: Scraping em Massa

**Objetivo**: Extrair dados de múltiplas URLs ou arquivos HTML usando mesmos seletores.

#### Seletores da IA (se disponíveis):
- Banner de sucesso: "🤖 Seletores da IA disponíveis!"
- Checkbox: **"✨ Usar seletores identificados pela IA"** (padrão: marcado)
- Se marcado, aplica TODOS os seletores da IA automaticamente

#### Método de Entrada:
**Opção 1: 📝 Inserir URLs**
- Text area para múltiplas URLs (uma por linha)
- Placeholder com exemplos de URLs
- Processo: Faz requisição HTTP para cada URL

**Opção 2: 📄 Upload de Arquivos HTML**
- Upload múltiplo de arquivos .html/.htm
- Exibe número de arquivos + nomes
- **Ideal para sites JavaScript-heavy** (Steam, Amazon, etc):
  - Salve a página com Ctrl+S (navegador)
  - Ou Ctrl+U → Save (HTML puro)
  - Upload do arquivo salvo
  - Aplica seletores de IA em todos os arquivos
- Resultados mostram nome do arquivo de origem

#### Seletores Customizados (se não usar IA):
**Métodos disponíveis**:
1. **Seletor CSS**: `div.produto`, `#header > p`
2. **XPath**: `//div[@class='produto']`, `//a/@href`
3. **Tag HTML**: `h1`, `div`, `span`
4. **Classe CSS**: `produto`, `price`

#### Opções de Extração:
- Checkbox: **"Extrair texto"** (padrão: marcado)
- Checkbox: **"Extrair atributos"** (href, src, alt, title, etc)

#### Processamento:
- Botão: **"🚀 Iniciar Scraping em Massa"**
- **Progress bar** visual com contagem
- Para cada URL/arquivo:
  1. Carrega conteúdo (requisição ou arquivo)
  2. Parseia com BeautifulSoup
  3. Aplica seletores (IA ou custom)
  4. Coleta dados
  5. Adiciona coluna "URL Origem" ou "Arquivo Origem"

#### Resultados:
- **Tabela consolidada** com todos os dados extraídos
- Colunas: URL/Arquivo + campos extraídos
- **Downloads**:
  - 📥 CSV: `scraping_massa.csv`
  - 📥 JSON: `scraping_massa.json`

---

### ⚡ TAB 4: Validador de Seletores

**Objetivo**: Testar múltiplos seletores (CSS + XPath) simultaneamente na página carregada.

#### Input de Seletores:
- **Text area grande** para colar seletores
- **Um seletor por linha**
- **Aceita mistura** de CSS e XPath
- **Placeholder com exemplos**:
  ```
  div.apphub_AppName
  //div[@class='produto']/h1
  span.price
  //a/@href
  ```

#### Opções de Extração:
- Checkbox: **"Extrair texto"** (padrão: marcado)
- Checkbox: **"Extrair atributos"**

#### Detecção Automática de Tipo:
A ferramenta identifica automaticamente se é CSS ou XPath:
- **Indicadores de XPath**:
  - Começa com `//`, `/`, `./`, `(//`, `(./`
  - Contém `::` (eixos como `descendant::`, `child::`)
  - Contém `@` com `/` (atributos com path)
- **Se não for XPath**: considera CSS

#### Processamento:
- Botão: **"🚀 Testar Todos os Seletores"**
- Para cada seletor:
  1. Detecta tipo (XPath vs CSS)
  2. Aplica seletor na página
  3. Conta elementos encontrados
  4. Extrai primeiro valor (preview)
  5. Trata erros (exibe mensagem)

#### Resultados:
- **Tabela com 4 colunas**:
  1. **Seletor**: String original
  2. **Tipo**: "XPath" ou "CSS"
  3. **Encontrados**: Número de elementos
  4. **Primeiro Valor**: Preview do primeiro resultado
- Indicadores visuais:
  - ✅ Verde: Encontrou elementos
  - ⚠️ Amarelo: Nenhum elemento encontrado
  - ❌ Vermelho: Erro no seletor

#### Downloads:
- 📥 CSV: `teste_universal.csv`
- 📥 JSON: `teste_universal.json`

---

### 🤖 TAB 5: Scraping Automático

**Objetivo**: Configurar tarefas de scraping periódicas com agendamento e notificações por email.

**⚠️ ACESSO RESTRITO**: Apenas administradores

#### Banner Informativo:
```
💡 Execução Manual: Use o botão ▶️ para executar tarefas sob demanda.
Para agendamento automático, configure Replit Scheduled Deployments no painel de deployment.
```

#### Layout: 2 Colunas

---

##### COLUNA 1: Nova Tarefa de Scraping

**Formulário em 5 Etapas:**

**1️⃣ Configuração da Fonte**
- **Nome da Tarefa**: Input text (ex: "Lançamentos Steam Semanal")
- **URL da Página de Lançamentos**: Input text com placeholder

**2️⃣ Configuração de Busca**
- **Site Alvo para Buscar Produtos**: Input text
- **Método de Busca**: Selectbox com 3 opções:
  - "Híbrido (Python + IA)"
  - "Apenas Python"
  - "Apenas IA"

**3️⃣ Campos para Extrair**
- **Text area** para campos desejados (um por linha)
- **Placeholder**:
  ```
  Título
  Preço
  Disponibilidade
  Link
  Imagem
  ```

**4️⃣ Agendamento**
- **Frequência**: Selectbox
  - "Diário"
  - "Semanal"
  - "Mensal"
  - "Personalizado"
- **Se Personalizado**: Input para cron expression (ex: `0 10 * * 1`)

**5️⃣ Notificações por Email**

**Provedor de Email**: Selectbox com 4 opções:

**A. SMTP Customizado** (Totalmente Funcional)
- **Servidor SMTP**: Input (ex: `smtp.gmail.com`)
- **Porta**: Number input (ex: `587`)
- **Usuário (Email Remetente)**: Input
- **Senha**: Password input
- **Email Destinatário**: Input
- **Funcionamento**:
  - Suporta Gmail, Outlook, Yahoo, qualquer SMTP
  - Usa `smtplib` do Python
  - TLS habilitado
  - Testa conexão antes de salvar

**B. SendGrid** (Integração Preparada)
- **API Key**: Password input
- **Email Destinatário**: Input
- **Status**: Aviso de implementação

**C. Resend** (Integração Preparada)
- **API Key**: Password input
- **Email Destinatário**: Input
- **Status**: Aviso de implementação

**D. Gmail** (Integração Preparada)
- **Email Remetente (Gmail)**: Input
- **Senha de Aplicativo**: Password input
- **Email Destinatário**: Input
- **Status**: Aviso de implementação

**Botão Final**:
- **"💾 Salvar Tarefa"**: Submit button (full width)

---

##### COLUNA 2: Tarefas Ativas

**Lista de Tarefas Configuradas:**

Para cada tarefa, exibe **card expansível**:
- **Nome da tarefa** (título do expander)
- **Conteúdo expandido**:
  ```
  🎯 Fonte: [URL]
  🔍 Site Alvo: [URL]
  🧠 Método: [Híbrido/Python/IA]
  📋 Campos: [lista]
  ⏰ Frequência: [Diário/Semanal/etc]
  📧 Email: [provedor] → [destinatário]
  ```

**Ações por Tarefa**:
- **▶️ Executar Agora**: Button (largura completa)
  - Executa scraping imediatamente
  - Exibe spinner durante execução
  - **Mostra preview dos produtos**:
    - Tabela com primeiros resultados
    - Contagem total de produtos
  - Salva execução em histórico
  
- **🗑️ Deletar**: Button (largura completa)
  - Remove tarefa permanentemente
  - Atualiza lista

#### Armazenamento:

**Arquivo 1: `scraping_tasks.json`**
Estrutura:
```json
{
  "task_id_uuid": {
    "id": "uuid-gerado",
    "name": "Nome da Tarefa",
    "source_url": "https://...",
    "target_site": "https://...",
    "search_method": "Híbrido (Python + IA)",
    "fields": ["Título", "Preço", "Link"],
    "frequency": "Semanal",
    "custom_schedule": "",
    "email_config": {
      "provider": "SMTP Customizado",
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_user": "user@gmail.com",
      "smtp_password": "senha_criptografada",
      "recipient": "destino@email.com"
    },
    "created_at": "2025-10-27T20:00:00"
  }
}
```

**Arquivo 2: `scraping_history.json`**
Estrutura:
```json
[
  {
    "task_id": "uuid-da-tarefa",
    "task_name": "Nome da Tarefa",
    "status": "success",
    "timestamp": "2025-10-27T21:30:00",
    "products_found": 15,
    "error_message": null,
    "data_preview": [
      {"Título": "Produto 1", "Preço": "R$ 99"},
      {"Título": "Produto 2", "Preço": "R$ 149"}
    ]
  }
]
```

**Exclusão do Git**: Ambos arquivos em `.gitignore`

#### Histórico de Execuções (Sidebar):
- **Seção no sidebar**: "📊 Histórico de Execuções"
- **Últimas 5 execuções**
- Para cada execução:
  ```
  [Nome da Tarefa]
  ✅ Sucesso / ❌ Erro
  🕐 27/10/2025 21:30
  📦 15 produtos encontrados
  ```
- Ordenado por mais recente

---

## 🧩 FUNÇÕES AUXILIARES IMPORTANTES

### 1. Extração de Dados

#### `extract_with_css(selector, extract_text, extract_attrs)`
- Usa `BeautifulSoup.select()`
- Retorna lista de dicionários
- Colunas: "Texto", "Atributos"

#### `extract_with_xpath(xpath, extract_text, extract_attrs)`
- Usa `lxml_html.fromstring()` e `.xpath()`
- Detecta se é atributo ou elemento
- Retorna lista de dicionários

#### `extract_with_tag(tag_name)`
- Usa `BeautifulSoup.find_all(tag)`
- Retorna textos extraídos

#### `extract_with_class(class_name)`
- Usa `BeautifulSoup.find_all(class_=class_name)`
- Retorna textos extraídos

### 2. IA e Seletores

#### `ask_ai_for_selectors(html_content, user_query, ai_provider, api_key)`
- Monta prompt detalhado para IA
- **Prompt inclui**:
  - HTML completo da página
  - Requisitos de resposta JSON
  - Exemplos de seletores CSS e XPath
  - Instruções para explicação e exemplos
- **Retorna**: JSON com array de seletores
- **Tratamento de erros**: Anthropic concatena blocos de texto

#### `get_api_key(key_name)`
- Busca em Replit Secrets (`os.environ.get()`)
- Se não encontrar, busca em custom keys (`api_keys.json`)
- Retorna valor ou None

### 3. Gerenciamento de Tarefas

#### `load_scraping_tasks()`
- Carrega `scraping_tasks.json`
- Retorna dicionário de tarefas

#### `save_scraping_tasks(tasks)`
- Salva dicionário em `scraping_tasks.json`
- Formato JSON indentado

#### `execute_scraping_task(task)`
- Executa uma tarefa de scraping
- Passos:
  1. Faz requisição HTTP para `source_url`
  2. Parseia HTML com BeautifulSoup
  3. Aplica método de busca (Python/IA/Híbrido)
  4. Extrai campos especificados
  5. Retorna lista de produtos
- **Retorna**: tupla `(success, data, error_message)`

#### `send_email_notification(email_config, task_name, products)`
- Monta email HTML formatado
- **Suporta SMTP customizado** (funcionando):
  ```python
  server = smtplib.SMTP(smtp_server, smtp_port)
  server.starttls()
  server.login(smtp_user, smtp_password)
  server.send_message(msg)
  ```
- **SendGrid/Resend/Gmail**: Preparado mas não totalmente implementado

#### `save_execution_history(task_id, task_name, status, products_count, error_msg, data_preview)`
- Adiciona execução ao histórico
- Salva em `scraping_history.json`
- Mantém últimas 100 execuções

---

## 📦 DEPENDÊNCIAS E ARQUIVOS

### Bibliotecas Python (pyproject.toml):
```toml
dependencies = [
    "anthropic",
    "apscheduler",
    "beautifulsoup4",
    "flask",
    "flask-cors",
    "google-genai",
    "lxml",
    "openai",
    "pandas",
    "replit",
    "requests",
    "selenium",
    "streamlit",
    "trafilatura",
    "webdriver-manager",
]
```

### Arquivos de Dados (excluídos do git):
1. **api_keys.json**: API keys customizadas
2. **authorized_emails.json**: Emails autorizados
3. **scraping_tasks.json**: Tarefas de scraping configuradas
4. **scraping_history.json**: Histórico de execuções

### Configuração Streamlit (.streamlit/config.toml):
```toml
[server]
port = 5000
address = "0.0.0.0"
headless = true

[theme]
# Tema padrão do Streamlit
```

### .gitignore:
```
api_keys.json
authorized_emails.json
scraping_tasks.json
scraping_history.json
__pycache__/
*.pyc
.env
```

---

## 🚀 WORKFLOWS DE EXECUÇÃO

### Workflow 1: Proxy Server
```bash
python proxy_server.py
```
- Inicia Flask na porta 5001
- Sempre ativo

### Workflow 2: Server (Streamlit)
```bash
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
```
- Inicia Streamlit na porta 5000
- Interface principal

---

## 🎨 CARACTERÍSTICAS TÉCNICAS

### Headers HTTP (Requests):
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

### Session State (Streamlit):
```python
st.session_state.html_content = "..."  # HTML bruto
st.session_state.soup = BeautifulSoup(...)  # Objeto parseado
st.session_state.url = "https://..."  # URL atual
st.session_state.ai_result = {...}  # Resultado da IA
st.session_state.authenticated = True/False  # Login
st.session_state.user_email = "..."  # Email do usuário
st.session_state.is_admin = True/False  # Se é admin
```

### Tratamento de Erros:
- **HTTP**: `response.raise_for_status()`
- **IA**: Try/except com mensagens específicas
- **Seletores**: Validação e mensagens de erro amigáveis
- **Email**: Testa conexão SMTP antes de salvar

---

## 📱 INTERFACE EM PORTUGUÊS

### Exemplos de Textos:
- ✅ "Login realizado com sucesso!"
- ❌ "Usuário ou senha incorretos!"
- 🚀 "Iniciar Scraping em Massa"
- 📥 "Download CSV"
- 💡 "Credenciais padrão: usuário: admin | senha: admin123"
- ⚠️ "Esta funcionalidade está disponível apenas para administradores"
- 🤖 "Seletores da IA disponíveis!"

### Placeholders:
- "Digite seu usuário"
- "Digite sua senha"
- "https://exemplo.com"
- "Encontre o título do jogo, preço e link para compra"

---

## 🔒 SEGURANÇA

1. **Senhas**: Type="password" em todos os inputs sensíveis
2. **API Keys**: Mascaradas na exibição (sk-...xyz)
3. **Session State**: Limpo ao fazer logout
4. **Admin Master**: Email hardcoded, não pode ser removido
5. **SMTP**: Credenciais não exibidas depois de salvar
6. **Git**: Arquivos sensíveis em .gitignore

---

## 📊 FUNCIONALIDADES COMPLETAS

### Métodos de Extração:
1. ✅ CSS Selectors
2. ✅ XPath
3. ✅ HTML Tags
4. ✅ CSS Classes
5. ✅ IDs (via CSS)
6. ✅ IA-Assisted (3 provedores)
7. ✅ Bulk Scraping (URLs + HTML files)
8. ✅ Universal Validator (mistura CSS + XPath)

### Provedores de IA:
1. ✅ OpenAI GPT-5
2. ✅ Anthropic Claude Sonnet 4
3. ✅ Google Gemini 2.5 Flash

### Automação:
1. ✅ Configuração de tarefas via UI
2. ✅ Execução manual sob demanda
3. ✅ Agendamento (frequências pré-definidas + cron custom)
4. ✅ Email notifications (SMTP custom funcional)
5. ✅ Histórico de execuções
6. ✅ Preview de resultados

### Proxy e Anti-Scraping:
1. ✅ Servidor Flask proxy (porta 5001)
2. ✅ Integração com corsproxy.io
3. ✅ Headers customizados (User-Agent, etc)
4. ✅ Upload de HTML para JS-heavy sites

---

## 🎯 CASOS DE USO COMPLETOS

### ⚠️ ATENÇÃO: Cada caso mostra ETAPA 1 (Carregar) + ETAPA 2 (Extrair)

---

### 1. Scraping Simples de Blog/Notícia:

**🔵 ETAPA 1 - CARREGAR HTML:**
1. Login (admin / admin123)
2. Sidebar: Método = "⚡ Rápido (Python)"
3. Sidebar: Inserir URL → "🔍 Carregar Página"
4. ✅ HTML carregado em memória

**🟢 ETAPA 2 - EXTRAIR DADOS:**
1. Aba "📊 Estrutura HTML" → Ver tags, classes disponíveis
2. Aba "⚡ Validador de Seletores" → Testar seletores manualmente
3. Download CSV/JSON

---

### 2. Scraping com IA (Loja Online):

**🔵 ETAPA 1 - CARREGAR HTML:**
1. Login
2. Sidebar: Método = "⚡ Rápido (Python)" ou "🌐 Proxy CORS"
3. Inserir URL da página de produto
4. Clicar "🔍 Carregar Página"
5. ✅ HTML carregado

**🟢 ETAPA 2 - EXTRAIR DADOS:**
1. Aba "🤖 Extração com IA"
2. Escolher provedor (OpenAI, Claude, Gemini)
3. Adicionar API key (se necessário)
4. Descrever: "Extraia título, preço, disponibilidade e imagem do produto"
5. Clicar "🔍 Buscar com IA"
6. IA identifica seletores CSS/XPath automaticamente
7. Resultados aparecem em tabela
8. Download CSV/JSON direto
9. Copiar seletores para reusar depois

---

### 3. Scraping em Massa (Múltiplos Produtos):

**🔵 ETAPA 1A - CARREGAR PÁGINA DE EXEMPLO:**
1. Login
2. Carregar UMA página de produto (para treinar IA)
3. ✅ HTML carregado

**🟢 ETAPA 2A - IA IDENTIFICA SELETORES:**
1. Aba "🤖 Extração com IA"
2. Descrever campos desejados
3. IA identifica seletores
4. ✅ Seletores salvos em memória

**🔵 ETAPA 1B - NÃO PRECISA CARREGAR NADA!**
(Scraping em Massa carrega múltiplas URLs sozinho)

**🟢 ETAPA 2B - APLICAR SELETORES EM MASSA:**
1. Aba "🚀 Scraping em Massa"
2. Marcar "✨ Usar seletores identificados pela IA"
3. Inserir lista de URLs (uma por linha)
4. Clicar "🚀 Iniciar Scraping em Massa"
5. Sistema carrega CADA URL automaticamente
6. Aplica seletores da IA em todas
7. Download CSV/JSON consolidado

---

### 4. Sites JavaScript-heavy (Steam, Amazon):

**🔵 ETAPA 1 - SALVAR HTML DO NAVEGADOR:**
1. Abrir Steam/Amazon no Chrome/Firefox
2. Ctrl+S (Salvar página completa) OU Ctrl+U (View Source) → Save
3. Salvar arquivo .html no computador
4. ✅ HTML completo com JavaScript renderizado

**🟢 ETAPA 2A - IA IDENTIFICA SELETORES:**
1. Login no app
2. Sidebar: "📁 Upload de arquivo HTML"
3. Upload do arquivo salvo
4. Clicar "📥 Processar HTML"
5. Aba "🤖 Extração com IA"
6. Descrever campos
7. IA identifica seletores
8. ✅ Seletores salvos

**🟢 ETAPA 2B - PROCESSAR MÚLTIPLOS HTMLS:**
1. Salvar vários produtos (10, 20 páginas)
2. Aba "🚀 Scraping em Massa"
3. Opção "📄 Upload de Arquivos HTML"
4. Selecionar TODOS os arquivos de uma vez
5. Marcar "✨ Usar seletores da IA"
6. Processar
7. Download consolidado com nome do arquivo origem

---

### 5. Automação com Email (Admin):

**🔵 ETAPA 1 - CONFIGURAR TAREFA (não carrega nada):**
1. Login como admin
2. Aba "🤖 Scraping Automático"

**🟢 ETAPA 2 - CONFIGURAR EXTRAÇÃO AUTOMÁTICA:**
1. Preencher formulário:
   - Nome: "Lançamentos Semanais Steam"
   - URL Fonte: página de novidades
   - Site Alvo: Steam
   - Método: "Híbrido (Python + IA)"
   - Campos: Título, Preço, Link
   - Frequência: Semanal
   - Email: SMTP Customizado
     - Servidor: smtp.gmail.com
     - Porta: 587
     - Usuário: seu@gmail.com
     - Senha: senha_app
     - Destinatário: destino@email.com
2. Salvar tarefa
3. Clicar "▶️ Executar Agora" para testar
4. Sistema carrega URL automaticamente
5. IA identifica seletores
6. Extrai produtos
7. Mostra preview
8. Envia email com resultados
9. ✅ Tarefa salva para repetição futura

---

### 6. Validar Múltiplos Seletores:

**🔵 ETAPA 1 - CARREGAR HTML:**
1. Login
2. Carregar qualquer página
3. ✅ HTML em memória

**🟢 ETAPA 2 - TESTAR SELETORES:**
1. Aba "⚡ Validador de Seletores"
2. Colar lista de seletores (CSS e XPath misturados):
   ```
   div.produto
   //h1[@class='titulo']
   span.price
   //a/@href
   ```
3. Clicar "🚀 Testar Todos os Seletores"
4. Ver resultados: tipo detectado, quantos encontrados, preview
5. Download CSV/JSON

---

## 🏗️ ARQUITETURA FINAL

```
┌─────────────────────────────────────────────┐
│         USUÁRIO ACESSA O APP                │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     🔐 TELA DE LOGIN (app.py)               │
│     - Usuário/Senha                         │
│     - Validação via Secrets                 │
└──────────────────┬──────────────────────────┘
                   │ ✅ Autenticado
                   ▼
┌─────────────────────────────────────────────┐
│     📂 SIDEBAR - CONTROLE                   │
│     - Método de carregamento                │
│     - Carregar URL / Upload HTML            │
│     - Gerenciar Acessos (admin)             │
│     - Gerenciar API Keys (admin)            │
│     - Histórico de Execuções                │
│     - Logout                                │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     📑 5 ABAS PRINCIPAIS                    │
├─────────────────────────────────────────────┤
│  1. 📊 Estrutura HTML                       │
│     - Estatísticas                          │
│     - Tags/Classes/IDs                      │
│     - Preview HTML                          │
│     - Visualização renderizada              │
├─────────────────────────────────────────────┤
│  2. 🤖 Extração com IA                      │
│     - 3 Provedores (GPT-5, Claude, Gemini)  │
│     - Descrição em linguagem natural        │
│     - Auto-identificação de seletores       │
│     - Extração automática + download        │
│     - Cópia de seletores                    │
├─────────────────────────────────────────────┤
│  3. 🚀 Scraping em Massa                    │
│     - URLs múltiplas                        │
│     - Upload de HTMLs                       │
│     - Seletores IA ou custom                │
│     - Progress bar                          │
│     - Resultado consolidado                 │
├─────────────────────────────────────────────┤
│  4. ⚡ Validador de Seletores               │
│     - Teste múltiplo                        │
│     - Detecção auto CSS/XPath               │
│     - Resultados em tabela                  │
├─────────────────────────────────────────────┤
│  5. 🤖 Scraping Automático (admin)          │
│     - Configurar tarefas                    │
│     - Agendamento                           │
│     - Email (SMTP custom)                   │
│     - Execução manual                       │
│     - Histórico                             │
└─────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     🌐 PROXY SERVER (proxy_server.py)       │
│     - Flask na porta 5001                   │
│     - /proxy?url=...                        │
│     - CORS bypass via corsproxy.io          │
│     - /health para status                   │
└─────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│     💾 PERSISTÊNCIA                         │
│     - api_keys.json                         │
│     - authorized_emails.json                │
│     - scraping_tasks.json                   │
│     - scraping_history.json                 │
└─────────────────────────────────────────────┘
```

---

## 📝 NOTAS FINAIS

### Pontos Fortes:
- ✅ Interface 100% em português
- ✅ Múltiplos métodos de extração
- ✅ IA com 3 provedores principais
- ✅ Proxy para contornar bloqueios
- ✅ Automação completa com email
- ✅ Upload de HTML para sites JavaScript
- ✅ Gerenciamento híbrido de API keys
- ✅ Sistema de autenticação funcional
- ✅ Admin panel completo

### Melhorias Futuras Possíveis:
- Integração completa SendGrid/Resend/Gmail
- Agendamento real via Replit Scheduled Deployments
- Dashboard de analytics de scraping
- Export para Google Sheets
- Webhooks para notificações
- Rate limiting configurável
- Retry automático em caso de falha

---

**Este é o PROMPT COMPLETO com TODAS as funcionalidades implementadas no Web Scraper Intuitivo.**
